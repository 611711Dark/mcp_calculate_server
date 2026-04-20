import unittest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from server import calculate_expression

class TestCalculateExpression(unittest.TestCase):
    def test_basic_operations(self):
        """测试基础运算"""
        self.assertEqual(calculate_expression("2 + 3*5"), "17")
        self.assertEqual(calculate_expression("10 / 2"), "5.0")
        self.assertEqual(calculate_expression("2**8"), "256")

    def test_algebraic_operations(self):
        """测试代数运算"""
        self.assertEqual(calculate_expression("expand((x + 1)**2)"), "x**2 + 2.0*x + 1.0")
        self.assertEqual(calculate_expression("factor(x**2 - 2*x - 15)"), "(x - 5.0)*(x + 3.0)")
        self.assertEqual(calculate_expression("simplify((x**2 - 1)/(x + 1))"), "x - 1.0")

    def test_calculus(self):
        """测试微积分"""
        self.assertEqual(calculate_expression("diff(sin(x), x)"), "cos(x)")
        self.assertEqual(calculate_expression("cos(x)"), "cos(x)")
        self.assertEqual(calculate_expression("integrate(exp(x), x)"), "exp(x)")
        self.assertEqual(calculate_expression("limit(tan(x)/x, x, 0)"), "1.00000000000000")
        self.assertEqual(
            calculate_expression("integrate(exp(-x**2)*sin(x), (x, -oo, oo))"),
            "0"
        )
        self.assertEqual(
            calculate_expression("series(cos(x), x, 0, 4)"),
            "1.0 - 0.5*x**2 + O(x**4)"
        )

    def test_equation_solving(self):
        """测试方程求解"""
        self.assertEqual(calculate_expression("solve(x**2 - 4, x)"), "[-2.00000000000000, 2.00000000000000]")
        self.assertEqual(calculate_expression("solve([x + y - 1, x - y - 1], [x, y])"), "{x: 1, y: 0}")

    def test_matrix_operations(self):
        """测试矩阵运算"""
        self.assertEqual(calculate_expression("Matrix([[1, 2], [3, 4]]).inv()"), 
                         "Matrix([[-2.00000000000000, 1.00000000000000], [1.50000000000000, -0.500000000000000]])")
        self.assertEqual(calculate_expression("Matrix([[1, 2], [3, 4]]).det()"), "-2.00000000000000")
        self.assertEqual(
            calculate_expression("Matrix([[1, 2], [3, 4]]).eigenvals()"),
            "{5/2 - sqrt(33)/2: 1, 5/2 + sqrt(33)/2: 1}"
        )
        self.assertEqual(
            calculate_expression("Matrix([[1, 2], [3, 4]]).eigenvects()"),
            "[(-0.372281323269014, 1, [Matrix([\n[-sqrt(33)/6 - 1/2],\n[                1]])]), (5.37228132326901, 1, [Matrix([\n[-1/2 + sqrt(33)/6],\n[                1]])])]"
        )

    def test_sum_operations(self):
        """测试求和运算"""
        self.assertEqual(calculate_expression("Sum(k, (k, 1, 10)).doit()"), "55.0000000000000")

    def test_error_handling(self):
        """测试错误处理"""
        self.assertTrue(calculate_expression("1 / 0").startswith("Error:"))
        self.assertTrue(calculate_expression("invalid expression").startswith("Error:"))
        self.assertEqual(
            calculate_expression("__import__('os').system('id')"),
            "Error: Expression contains blocked content"
        )
        self.assertEqual(
            calculate_expression("open('/etc/passwd').read()"),
            "Error: Expression contains blocked content"
        )
        self.assertEqual(
            calculate_expression("expand((x + 1)**1000)"),
            "Error: Expand exponent is too large"
        )
        self.assertEqual(
            calculate_expression("solve(x**50 - 1, x)"),
            "Error: Solve expression is too complex"
        )
        self.assertEqual(
            calculate_expression("expand((x + 1)**200)"),
            "Error: Result is too large"
        )
        self.assertEqual(
            calculate_expression("series(cos(x), x, 0, 30)"),
            "Error: Series order is too large"
        )
        self.assertEqual(
            calculate_expression("Sum(k, (k, 1, 20050)).doit()"),
            "Error: Summation range is too large"
        )
        self.assertEqual(
            calculate_expression("Matrix([[1, 2], [3, 4]]).transpose()"),
            "Error: Unsupported matrix method: transpose"
        )
        self.assertEqual(
            calculate_expression("Matrix([[1, 2], [3]]).det()"),
            "Error: Matrix rows must have equal length"
        )
        self.assertEqual(
            calculate_expression(
                "Matrix([[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]]).det()"
            ),
            "Error: Matrix has too many rows"
        )
        self.assertEqual(
            calculate_expression("sin(x).__class__"),
            "Error: Expression contains blocked content"
        )

if __name__ == "__main__":
    unittest.main()
