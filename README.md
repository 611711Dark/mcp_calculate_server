# MCP Calculate Server

A Python-based server for calculating mathematical expressions using `mcp` and `sympy`.

## Prerequisites

- Python >= 3.11
- Docker (optional, for containerized deployment)

## Installation

### Local Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/611711Dark/mcp-calculate-server.git
   cd mcp-calculate-server
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
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "/path/to/mcp_calculate_server",
        "server.py"
      ],
    }
   ```


## Dependencies

- mcp>=1.5.0
- sympy>=1.13.3
- fastapi>=0.95.0
- uvicorn>=0.21.0

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
