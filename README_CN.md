# MCP计算服务器

[![smithery徽章](https://smithery.ai/badge/@611711Dark/mcp_calculate_server)](https://smithery.ai/server/@611711Dark/mcp_calculate_server)

基于MCP协议和SymPy库的数学计算服务，提供强大的符号计算能力。

## 安全说明

从 `0.1.1` 版本开始，服务使用受限的 SymPy 解析器处理表达式，不再执行任意 Python 代码。服务仅支持经过白名单控制的数学符号、函数和矩阵方法。

该版本还增加了对超大表达式和超长结果的校验，用于降低高成本符号计算带来的拒绝服务风险。

## 核心功能

- **基础运算**：加减乘除、幂运算
- **代数运算**：表达式展开、因式分解、化简
- **微积分**：求导、积分（定积分/不定积分）、极限计算
- **方程求解**：代数方程、方程组
- **矩阵运算**：矩阵求逆、特征值/特征向量计算
- **级数展开**：泰勒级数展开
- **特殊函数**：三角函数、对数函数、指数函数

## 使用示例

```python
# 基础运算
"2 + 3*5" → 17

# 代数运算
"expand((x + 1)**2)" → x² + 2x + 1
"factor(x**2 - 2*x - 15)" → (x - 5)(x + 3)

# 微积分
"diff(sin(x), x)" → cos(x)
"integrate(exp(x), (x, 0, 1))" → E - 1
"integrate(exp(-x**2)*sin(x), (x, -oo, oo))" → 0
"limit(tan(x)/x, x, 0)" → 1

# 方程求解
"solve(x**2 - 4, x)" → [-2, 2]
"solve([x**2 + y**2 - 1, x + y - 1], [x, y])" → [(0, 1), (1, 0)]

# 矩阵运算
"Matrix([[1, 2], [3, 4]]).inv()" → [[-2, 1], [3/2, -1/2]]
"Matrix([[1, 2, 3], [4, 5, 6]]).eigenvals()" → {9/2 - sqrt(33)/2: 1, 9/2 + sqrt(33)/2: 1}
"Sum(k, (k, 1, 10)).doit()" → 55
"series(cos(x), x, 0, 4)" → 1 - x²/2 + O(x⁴)
```

## 安装指南

### 通过Smithery安装

通过[Smithery](https://smithery.ai/server/@611711Dark/mcp_calculate_server)为Claude Desktop自动安装计算服务器：

```bash
npx -y @smithery/cli install @611711Dark/mcp_sympy_calculate_server --client claude
```

### 本地安装

1. 克隆仓库：
   ```bash
   git clone https://github.com/611711Dark/mcp_calculate_server.git
   cd mcp_calculate_server
   ```

2. 创建虚拟环境并安装依赖：
   ```bash
   uv venv
   source .venv/bin/activate
   uv pip install -e .
   ```

3. 配置：
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

## API使用

通过MCP协议调用`calculate_expression`工具，传入数学表达式字符串，返回计算结果。当前支持的受限 SymPy 表达式包括基础运算，以及 `expand`、`factor`、`simplify`、`diff`、`integrate`、`limit`、`series`、`solve`、`Matrix(...).det()/inv()/eigenvals()/eigenvects()`、`Sum(...).doit()` 等。

### 支持的名称

- 符号：`x`、`y`、`z`、`k` 等小写变量
- 常量：`pi`、`E`、`oo`、`I`
- 函数：`Abs`、`sin`、`cos`、`tan`、`log`、`exp`、`sqrt`、`expand`、`factor`、`simplify`、`diff`、`integrate`、`limit`、`series`、`solve`、`Sum`、`Matrix`
- 矩阵方法：`.det()`、`.inv()`、`.eigenvals()`、`.eigenvects()`
- SymPy 方法：适用于 `Sum(...)` 等对象的 `.doit()`

### 校验规则

依赖任意 Python 特性、导入、文件访问或其他非数学行为的表达式会被明确拒绝。
为降低拒绝服务风险，超大展开、高复杂度求解以及过长结果也可能被拒绝。
关键字参数、私有属性、不支持的矩阵方法、非法矩阵结构以及未允许的名称也会返回错误。

## 依赖项

- mcp>=1.5.0
- sympy>=1.13.3

## 许可证

本项目采用MIT许可证，详见[LICENSE](LICENSE)文件。

[English Version](README.md)
