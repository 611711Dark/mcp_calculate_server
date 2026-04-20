import ast
from string import ascii_lowercase

import sympy as sp
from mcp.server.fastmcp import FastMCP

# Create MCP server
mcp = FastMCP("MathTool")

MAX_INPUT_LENGTH = 500
MAX_AST_NODES = 200
MAX_MATRIX_DIMENSION = 10
MAX_POWER_ABS = 1000
MAX_RESULT_LENGTH = 4000
MAX_EXPAND_POWER = 256
MAX_SOLVE_POWER = 20
MAX_SERIES_ORDER = 20
MAX_SUM_TERMS = 10000
BLOCKED_IDENTIFIERS = {
    "__import__",
    "builtins",
    "compile",
    "delattr",
    "eval",
    "exec",
    "getattr",
    "globals",
    "input",
    "locals",
    "open",
    "os",
    "setattr",
    "subprocess",
    "sys",
}


def build_namespace():
    """Return a restricted SymPy namespace."""
    symbol_names = {name: sp.Symbol(name) for name in ascii_lowercase}
    namespace = {
        **symbol_names,
        "pi": sp.pi,
        "E": sp.E,
        "oo": sp.oo,
        "I": sp.I,
        "Abs": sp.Abs,
        "Matrix": sp.Matrix,
        "Sum": sp.Sum,
        "diff": sp.diff,
        "expand": sp.expand,
        "exp": sp.exp,
        "factor": sp.factor,
        "integrate": sp.integrate,
        "limit": sp.limit,
        "log": sp.log,
        "simplify": sp.simplify,
        "sin": sp.sin,
        "cos": sp.cos,
        "tan": sp.tan,
        "sqrt": sp.sqrt,
        "solve": sp.solve,
        "series": sp.series,
    }
    return namespace


SAFE_NAMESPACE = build_namespace()
ALLOWED_MATRIX_METHODS = {"det", "eigenvals", "eigenvects", "inv"}
ALLOWED_BASIC_METHODS = {"doit"}


class UnsafeExpressionError(ValueError):
    """Raised when the expression uses unsupported or unsafe syntax."""


def get_numeric_literal(node):
    """Extract a numeric literal from AST when possible."""
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
        value = get_numeric_literal(node.operand)
        if value is not None:
            return -value
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.UAdd):
        return get_numeric_literal(node.operand)
    return None


def iter_numeric_powers(node):
    """Yield numeric exponents found in a subtree."""
    for child in ast.walk(node):
        if isinstance(child, ast.BinOp) and isinstance(child.op, ast.Pow):
            exponent = get_numeric_literal(child.right)
            if exponent is not None:
                yield exponent


def get_call_name(node):
    """Return a simple call/method name from an AST node."""
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    return None


class ExpressionPolicyValidator(ast.NodeVisitor):
    """Apply policy checks that are easier before evaluation."""

    def visit_Name(self, node):
        if node.id in BLOCKED_IDENTIFIERS:
            raise UnsafeExpressionError("Expression contains blocked content")

    def visit_Attribute(self, node):
        if node.attr.startswith("_") or node.attr in BLOCKED_IDENTIFIERS:
            raise UnsafeExpressionError("Expression contains blocked content")
        self.visit(node.value)

    def visit_Call(self, node):
        call_name = get_call_name(node.func)

        if call_name == "expand":
            powers = list(iter_numeric_powers(node))
            if powers and max(abs(power) for power in powers) > MAX_EXPAND_POWER:
                raise UnsafeExpressionError("Expand exponent is too large")

        if call_name == "solve":
            powers = [
                abs(power)
                for arg in node.args
                for power in iter_numeric_powers(arg)
            ]
            if powers and max(powers) > MAX_SOLVE_POWER:
                raise UnsafeExpressionError("Solve expression is too complex")

        if call_name == "series" and len(node.args) >= 4:
            order = get_numeric_literal(node.args[3])
            if order is not None and order > MAX_SERIES_ORDER:
                raise UnsafeExpressionError("Series order is too large")

        if call_name == "Sum" and len(node.args) >= 2:
            bounds = node.args[1]
            if isinstance(bounds, ast.Tuple) and len(bounds.elts) == 3:
                lower = get_numeric_literal(bounds.elts[1])
                upper = get_numeric_literal(bounds.elts[2])
                if (
                    lower is not None
                    and upper is not None
                    and abs(upper - lower) > MAX_SUM_TERMS
                ):
                    raise UnsafeExpressionError("Summation range is too large")

        self.visit(node.func)
        for arg in node.args:
            self.visit(arg)
        for keyword in node.keywords:
            self.visit(keyword.value)


class SafeExpressionEvaluator(ast.NodeVisitor):
    """Evaluate a restricted subset of Python AST into SymPy objects."""

    def __init__(self, namespace):
        self.namespace = namespace

    def visit_Expression(self, node):
        return self.visit(node.body)

    def visit_Name(self, node):
        if node.id not in self.namespace:
            raise UnsafeExpressionError(f"Unsupported name: {node.id}")
        return self.namespace[node.id]

    def visit_Constant(self, node):
        if isinstance(node.value, (int, float)):
            return node.value
        raise UnsafeExpressionError("Only numeric constants are allowed")

    def visit_List(self, node):
        return [self.visit(element) for element in node.elts]

    def visit_Tuple(self, node):
        return tuple(self.visit(element) for element in node.elts)

    def visit_UnaryOp(self, node):
        operand = self.visit(node.operand)
        if isinstance(node.op, ast.UAdd):
            return +operand
        if isinstance(node.op, ast.USub):
            return -operand
        raise UnsafeExpressionError("Unsupported unary operation")

    def visit_BinOp(self, node):
        left = self.visit(node.left)
        right = self.visit(node.right)
        if isinstance(node.op, ast.Add):
            return left + right
        if isinstance(node.op, ast.Sub):
            return left - right
        if isinstance(node.op, ast.Mult):
            return left * right
        if isinstance(node.op, ast.Div):
            return left / right
        if isinstance(node.op, ast.Pow):
            if isinstance(right, (int, float)) and abs(right) > MAX_POWER_ABS:
                raise UnsafeExpressionError("Exponent is too large")
            return left ** right
        raise UnsafeExpressionError("Unsupported binary operation")

    def visit_Call(self, node):
        if node.keywords:
            raise UnsafeExpressionError("Keyword arguments are not supported")
        func = self.visit(node.func)
        args = [self.visit(arg) for arg in node.args]
        return func(*args)

    def visit_Attribute(self, node):
        target = self.visit(node.value)
        attr = node.attr
        if attr.startswith("_"):
            raise UnsafeExpressionError("Private attributes are not allowed")
        if isinstance(target, sp.MatrixBase):
            if attr not in ALLOWED_MATRIX_METHODS:
                raise UnsafeExpressionError(f"Unsupported matrix method: {attr}")
            return getattr(target, attr)
        if isinstance(target, sp.Basic):
            if attr not in ALLOWED_BASIC_METHODS:
                raise UnsafeExpressionError(f"Unsupported SymPy method: {attr}")
            return getattr(target, attr)
        raise UnsafeExpressionError(f"Unsupported attribute access: {attr}")

    def generic_visit(self, node):
        raise UnsafeExpressionError(
            f"Unsupported syntax: {type(node).__name__}"
        )


def validate_expression(expression: str) -> ast.Expression:
    if not expression or not expression.strip():
        raise UnsafeExpressionError("Expression cannot be empty")
    if len(expression) > MAX_INPUT_LENGTH:
        raise UnsafeExpressionError("Expression is too long")

    tree = ast.parse(expression, mode="eval")
    if sum(1 for _ in ast.walk(tree)) > MAX_AST_NODES:
        raise UnsafeExpressionError("Expression is too complex")
    ExpressionPolicyValidator().visit(tree)
    return tree


def evaluate_expression(expression: str):
    tree = validate_expression(expression)
    evaluator = SafeExpressionEvaluator(SAFE_NAMESPACE)
    return evaluator.visit(tree)


def evaluate_matrix_literal(matrix_value):
    if not isinstance(matrix_value, list) or not matrix_value:
        raise UnsafeExpressionError("Matrix requires a non-empty list of rows")
    if len(matrix_value) > MAX_MATRIX_DIMENSION:
        raise UnsafeExpressionError("Matrix has too many rows")

    normalized_rows = []
    row_length = None
    for row in matrix_value:
        if not isinstance(row, list) or not row:
            raise UnsafeExpressionError("Matrix rows must be non-empty lists")
        if len(row) > MAX_MATRIX_DIMENSION:
            raise UnsafeExpressionError("Matrix row is too wide")
        if row_length is None:
            row_length = len(row)
        elif len(row) != row_length:
            raise UnsafeExpressionError("Matrix rows must have equal length")
        normalized_rows.append(row)

    return sp.Matrix(normalized_rows)


def parse_call_arguments(call_node):
    evaluator = SafeExpressionEvaluator(SAFE_NAMESPACE)
    if call_node.keywords:
        raise UnsafeExpressionError("Keyword arguments are not supported")
    return [evaluator.visit(arg) for arg in call_node.args]


def handle_complex_integration(expression: str) -> str:
    """Handle integration using explicit parsing."""
    try:
        tree = validate_expression(expression)
        call_node = tree.body
        if not (
            isinstance(call_node, ast.Call)
            and isinstance(call_node.func, ast.Name)
            and call_node.func.id == "integrate"
        ):
            raise UnsafeExpressionError("Unsupported integration expression")

        args = parse_call_arguments(call_node)
        result = sp.integrate(*args)
        if isinstance(result, sp.Integral):
            result = result.doit()
        return format_result(result)
    except Exception as exc:
        return f"Error: {exc}"


def handle_equation_solving(expression: str) -> str:
    """Handle equation solving using explicit parsing."""
    try:
        tree = validate_expression(expression)
        call_node = tree.body
        if not (
            isinstance(call_node, ast.Call)
            and isinstance(call_node.func, ast.Name)
            and call_node.func.id == "solve"
        ):
            raise UnsafeExpressionError("Unsupported solve expression")

        args = parse_call_arguments(call_node)
        result = sp.solve(*args)
        return format_result(result)
    except Exception as exc:
        return f"Error: {exc}"


def handle_matrix_operation(expression: str) -> str:
    """Handle matrix operations using explicit parsing."""
    try:
        tree = validate_expression(expression)
        call_node = tree.body
        if not (
            isinstance(call_node, ast.Call)
            and isinstance(call_node.func, ast.Attribute)
            and isinstance(call_node.func.value, ast.Call)
            and isinstance(call_node.func.value.func, ast.Name)
            and call_node.func.value.func.id == "Matrix"
        ):
            raise UnsafeExpressionError("Unsupported matrix expression")

        matrix_args = parse_call_arguments(call_node.func.value)
        if len(matrix_args) != 1:
            raise UnsafeExpressionError("Matrix expects a single data argument")
        matrix = evaluate_matrix_literal(matrix_args[0])
        method_name = call_node.func.attr
        if method_name not in ALLOWED_MATRIX_METHODS:
            raise UnsafeExpressionError(f"Unsupported matrix method: {method_name}")
        result = getattr(matrix, method_name)()
        return format_result(result)
    except Exception as exc:
        return f"Error: {exc}"


def render_scalar(value, numeric=True):
    if numeric and isinstance(value, sp.MatrixBase):
        try:
            return str(value.evalf())
        except Exception:
            return str(value)

    if numeric and isinstance(value, sp.Basic):
        try:
            return str(value.evalf())
        except Exception:
            return str(value)

    return str(value)


def ensure_result_size(result_text: str) -> str:
    """Reject outputs that are too large to return safely."""
    if len(result_text) > MAX_RESULT_LENGTH:
        raise UnsafeExpressionError("Result is too large")
    return result_text


def format_result(result):
    """Format output based on result type."""
    try:
        if isinstance(result, dict):
            parts = [
                f"{render_scalar(key, numeric=False)}: {render_scalar(value, numeric=False)}"
                for key, value in result.items()
            ]
            return ensure_result_size("{" + ", ".join(parts) + "}")

        if isinstance(result, list):
            parts = []
            for item in result:
                if isinstance(item, tuple):
                    coords = ", ".join(render_scalar(value) for value in item)
                    parts.append(f"({coords})")
                elif isinstance(item, dict):
                    parts.append(format_result(item))
                else:
                    parts.append(render_scalar(item))
            return ensure_result_size("[" + ", ".join(parts) + "]")

        if isinstance(result, tuple):
            return ensure_result_size(
                "(" + ", ".join(render_scalar(item) for item in result) + ")"
            )

        return ensure_result_size(render_scalar(result))
    except UnsafeExpressionError:
        raise
    except Exception as exc:
        return f"Result formatting error: {exc}, original result: {result}"


# Add tool for calculating expressions
@mcp.tool()
def calculate_expression(expression: str) -> str:
    """
calculate mathematical expressions using a restricted SymPy parser and a curated namespace of safe math operations.
Parameters:
    expression (str): Mathematical expression, e.g., "223 - 344 * 6" or "sin(pi/2) + log(10)". Replace special symbols with approximate values, e.g., pi → 3.1415.
Example expressions:
    "2 + 3*5"                          # Basic arithmetic → 17
    "expand((x + 1)**2)"               # Expand → x² + 2x + 1
    "diff(sin(x), x)"                  # Derivative → cos(x)
    "integrate(exp(x), (x, 0, 1))"     # Definite integral → E - 1
    "solve(x**2 - 4, x)"               # Solve equation → [-2, 2]
    "limit(tan(x)/x, x, 0)"            # Limit → 1
    "Sum(k, (k, 1, 10)).doit()"        # Summation → 55
    "Matrix([[1, 2], [3, 4]]).inv()"   # Matrix inverse
    "simplify((x**2 - 1)/(x + 1))"     # Simplify → x - 1
    "factor(x**2 - 2*x - 15)"          # Factorize → (x - 5)(x + 3)
    "series(cos(x), x, 0, 4)"          # Taylor series
    "integrate(exp(-x**2)*sin(x), (x, -oo, oo))"  # Complex integral
    "solve([x**2 + y**2 - 1, x + y - 1], [x, y])"  # Solve system of equations
    "Matrix([[1, 2], [3, 4]]).eigenvals()"  # Matrix eigenvalues
Returns:
    str: Calculation result. If the expression cannot be parsed or computed, returns an error message.
"""
    try:
        expression = expression.strip()
        if expression.startswith("integrate("):
            return handle_complex_integration(expression)
        if expression.startswith("solve("):
            return handle_equation_solving(expression)
        if expression.startswith("Matrix(") and any(
            token in expression for token in (".det()", ".eigenvals()", ".eigenvects()", ".inv()")
        ):
            return handle_matrix_operation(expression)

        result = evaluate_expression(expression)
        return format_result(result)
    except Exception as exc:
        return f"Error: {exc}"


if __name__ == "__main__":
    mcp.run()
