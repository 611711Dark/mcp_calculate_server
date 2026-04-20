# MCP Calculate Server

[![smithery badge](https://smithery.ai/badge/@611711Dark/mcp_calculate_server)](https://smithery.ai/server/@611711Dark/mcp_calculate_server)

A mathematical calculation service based on MCP protocol and SymPy library, providing powerful symbolic computation capabilities.

## Security

As of version `0.1.1`, the server parses expressions through a restricted SymPy-only evaluator. It does not execute arbitrary Python code, and only a curated set of mathematical symbols, functions, and matrix methods are supported.

This release also adds validation for oversized expressions and large results to reduce denial-of-service risk from expensive symbolic computations.

## Key Features

- **Basic Operations**: Addition, subtraction, multiplication, division, exponentiation
- **Algebraic Operations**: Expression expansion, factorization, simplification
- **Calculus**: Differentiation, integration (definite/indefinite), limit calculation
- **Equation Solving**: Algebraic equations, systems of equations
- **Matrix Operations**: Matrix inversion, eigenvalues/eigenvectors calculation
- **Series Expansion**: Taylor series expansion
- **Special Functions**: Trigonometric, logarithmic, exponential functions

## Usage Examples

```python
# Basic operations
"2 + 3*5" → 17

# Algebraic operations
"expand((x + 1)**2)" → x² + 2x + 1
"factor(x**2 - 2*x - 15)" → (x - 5)(x + 3)

# Calculus
"diff(sin(x), x)" → cos(x)
"integrate(exp(x), (x, 0, 1))" → E - 1
"integrate(exp(-x**2)*sin(x), (x, -oo, oo))" → 0
"limit(tan(x)/x, x, 0)" → 1

# Equation solving
"solve(x**2 - 4, x)" → [-2, 2]
"solve([x**2 + y**2 - 1, x + y - 1], [x, y])" → [(0, 1), (1, 0)]

# Matrix operations
"Matrix([[1, 2], [3, 4]]).inv()" → [[-2, 1], [3/2, -1/2]]
"Matrix([[1, 2, 3], [4, 5, 6]]).eigenvals()" → {9/2 - sqrt(33)/2: 1, 9/2 + sqrt(33)/2: 1}
"Sum(k, (k, 1, 10)).doit()" → 55
"series(cos(x), x, 0, 4)" → 1 - x²/2 + O(x⁴)
```

## Installation

### Installing via Smithery

To install Calculate Server for Claude Desktop automatically via [Smithery](https://smithery.ai/server/@611711Dark/mcp_calculate_server):

```bash
npx -y @smithery/cli install @611711Dark/mcp_sympy_calculate_server --client claude
```

### Local Installation

1. Clone repository:
   ```bash
   git clone https://github.com/611711Dark/mcp_calculate_server.git
   cd mcp_calculate_server
   ```

2. Create virtual environment and install dependencies:
   ```bash
   uv venv
   source .venv/bin/activate
   uv pip install -e .
   ```

3. Configuration:
   ```json
   "calculate_expression1": {
      "isActive": false,
      "command": "python",
      "args": [
        "server.py"
      ],
      "cwd": "/path/to/mcp_calculate_server"
    }
   ```

## API Usage

Call `calculate_expression` tool via MCP protocol by passing a mathematical expression string. The parser accepts a restricted set of SymPy expressions such as arithmetic, `expand`, `factor`, `simplify`, `diff`, `integrate`, `limit`, `series`, `solve`, `Matrix(...).det()/inv()/eigenvals()/eigenvects()`, and `Sum(...).doit()`.

### Supported Names

- Symbols: lowercase variables such as `x`, `y`, `z`, and `k`
- Constants: `pi`, `E`, `oo`, `I`
- Functions: `Abs`, `sin`, `cos`, `tan`, `log`, `exp`, `sqrt`, `expand`, `factor`, `simplify`, `diff`, `integrate`, `limit`, `series`, `solve`, `Sum`, `Matrix`
- Matrix methods: `.det()`, `.inv()`, `.eigenvals()`, `.eigenvects()`
- SymPy method: `.doit()` on supported objects such as `Sum(...)`

### Validation Rules

Expressions that rely on arbitrary Python features, imports, filesystem access, or other non-mathematical constructs are intentionally rejected.
Very large expansions, high-complexity solves, and oversized results may also be rejected to reduce denial-of-service risk.
Keyword arguments, private attributes, unsupported matrix methods, malformed matrices, and unsupported names are rejected with an error message.

## Dependencies

- mcp>=1.5.0
- sympy>=1.13.3

## Acknowledgements
Thanks to [this blog post](https://skywork.ai/skypage/en/unlocking-ai-math-sympy-calculator/1981544716917862400) for the introduction, and to [Stefano](https://www.linkedin.com/in/stefano--di-santo/) for his help and responsible disclosure.

## License

This project is licensed under MIT License. See [LICENSE](LICENSE) file.

[中文版本](README_CN.md)
