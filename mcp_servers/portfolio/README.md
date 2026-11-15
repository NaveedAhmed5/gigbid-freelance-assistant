# Portfolio MCP Server (Standalone Package)

[![MCP Compliant](https://img.shields.io/badge/MCP-2024--11--05-blue.svg)](https://modelcontextprotocol.io)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A standalone **Model Context Protocol (MCP)** server providing structured access to verified technical portfolios, candidate case studies, quantitative evidence points, and past proposal outcomes.

---

## 🛠️ MCP Capabilities

### Tools
- `search_evidence(requirement: str, k: int = 3, filters: dict = None)`: Search verified case studies for quantitative proof points and architectural precedents.
- `get_case_study(id: str)`: Fetch complete architectural writeups, metrics, and implementation artifacts.
- `list_skills(persona: str)`: Retrieve verified technical skills and domain proficiencies.

### Resources
- `portfolio://case/{id}`: Real-time URI access to individual case studies.
- `portfolio://proposal/{id}`: Past proposal drafts labeled by outcome (`won`, `replied`, `ignored`).
- `portfolio://manifest`: High-level summary of all indexed candidate assets.

### Prompts
- `"Answer a screening question from my portfolio"`: Pre-structured prompt for answering client screening questions with citations.
- `"Summarize relevant portfolio evidence"`: Pre-structured prompt for extracting quantitative proof points.

---

## 🚀 Quickstart & Standalone Distribution

### 1. Run with `uvx` (Recommended)
You can run this server directly without manual installation using `uv` / `uvx`:
```bash
uvx --from . gigbid-portfolio-mcp
```
Or run directly in Python stdio mode:
```bash
uv run python -m mcp_servers.portfolio.server
```

### 2. Install with `pip`
```bash
pip install -e .
python -m mcp_servers.portfolio.server
```

### 3. Run with Docker
```bash
docker run -i --rm -v $(pwd)/data:/app/data gigbid/portfolio-mcp:latest
```

---

## 🔌 Connecting to MCP Hosts

### Claude Desktop
Add this to your Claude Desktop configuration (`claude_desktop_config.json`):

**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`  
**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "gigbid-portfolio": {
      "command": "python",
      "args": [
        "-m",
        "mcp_servers.portfolio.server"
      ],
      "cwd": "/path/to/Implementation",
      "env": {
        "PYTHONPATH": "/path/to/Implementation"
      }
    }
  }
}
```

### Cursor IDE
Add to your Cursor project settings (`.cursor/mcp.json`):
```json
{
  "mcpServers": {
    "portfolio": {
      "command": "python",
      "args": ["-m", "mcp_servers.portfolio.server"]
    }
  }
}
```

---

## 🧪 Testing the Server
Run the automated MCP test suite:
```bash
pytest mcp_servers/portfolio/tests/
```
