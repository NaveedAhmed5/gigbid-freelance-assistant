# Portfolio MCP Server

A standalone Model Context Protocol (MCP) server exposing candidate portfolios, verified enterprise case studies, past proposal outcomes, and prompt templates.

## Capabilities

### Tools
- `search_evidence(requirement, k, filters)`: Searches verified case studies for quantitative proof points.
- `get_case_study(id)`: Fetches complete architectural writeups and outcome metrics.
- `list_skills(persona)`: Enumerates verified competencies.

### Resources
- `portfolio://case/{id}`: Returns individual case study contents.
- `portfolio://proposal/{id}`: Returns labeled past proposals (`won`, `replied`, `ignored`).

### Prompts
- `"Answer a screening question from my portfolio"`
- `"Summarize relevant portfolio evidence"`

## Standalone Usage
Run as a standard MCP stdio server:
```bash
python -m mcp_servers.portfolio.server
```

Or configure in your MCP host (e.g. Claude Desktop / Antigravity MCP config):
```json
{
  "mcpServers": {
    "portfolio": {
      "command": "python",
      "args": ["-m", "mcp_servers.portfolio.server"],
      "env": {}
    }
  }
}
```
