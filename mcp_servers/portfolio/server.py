"""Portfolio MCP Server Assembly."""

from mcp_servers.portfolio.prompts import (
    prompt_answer_screening_question,
    prompt_summarize_portfolio_evidence,
)
from mcp_servers.portfolio.resources import read_case_resource, read_proposal_resource
from mcp_servers.portfolio.tools import get_case_study, list_skills, search_evidence
from mcp_servers.protocol import (
    BaseMCPServer,
    MCPPromptArgument,
    MCPToolAnnotation,
)


def create_portfolio_mcp_server() -> BaseMCPServer:
    server = BaseMCPServer(name="portfolio-mcp-server", version="1.0.0")

    # 1. Tools
    server.register_tool(
        name="search_evidence",
        description="Search candidate portfolio case studies for verified proof points and metrics.",
        input_schema={
            "type": "object",
            "properties": {
                "requirement": {"type": "string", "description": "Client requirement or keyword"},
                "k": {"type": "integer", "default": 3, "description": "Number of results"},
                "filters": {"type": "object", "description": "Optional filters such as persona or industry"},
            },
            "required": ["requirement"],
        },
        handler=search_evidence,
        annotations=MCPToolAnnotation(readOnlyHint=True, idempotentHint=True),
    )

    server.register_tool(
        name="get_case_study",
        description="Retrieve full case study text, architectural solution, and outcome metrics by ID.",
        input_schema={
            "type": "object",
            "properties": {"id": {"type": "string", "description": "Case study ID (e.g., cs_ai_ml_engineer_01)"}},
            "required": ["id"],
        },
        handler=get_case_study,
        annotations=MCPToolAnnotation(readOnlyHint=True, idempotentHint=True),
    )

    server.register_tool(
        name="list_skills",
        description="List verified technical skills and proficiencies for a given persona.",
        input_schema={
            "type": "object",
            "properties": {"persona": {"type": "string", "description": "Persona identifier"}},
            "required": ["persona"],
        },
        handler=list_skills,
        annotations=MCPToolAnnotation(readOnlyHint=True, idempotentHint=True),
    )

    # 2. Resources
    server.register_resource(
        uri_pattern="portfolio://case/{id}",
        name="Case Study Resource",
        description="Access full markdown case study by ID",
        handler=read_case_resource,
    )

    server.register_resource(
        uri_pattern="portfolio://proposal/{id}",
        name="Past Proposal Resource",
        description="Access historical labeled proposal and outcome by ID",
        handler=read_proposal_resource,
    )

    # 3. Prompts
    server.register_prompt(
        name="Answer a screening question from my portfolio",
        description="Generates grounded answers to job screening questions using verified case studies.",
        arguments=[
            MCPPromptArgument(name="question", description="The job screening question", required=True),
            MCPPromptArgument(name="persona", description="The target persona key", required=False),
        ],
        handler=prompt_answer_screening_question,
    )

    server.register_prompt(
        name="Summarize relevant portfolio evidence",
        description="Summarizes verified technical evidence matching a specific skill or requirement.",
        arguments=[
            MCPPromptArgument(name="skill_or_requirement", description="Skill or requirement to match", required=True),
            MCPPromptArgument(name="persona", description="The target persona key", required=False),
        ],
        handler=prompt_summarize_portfolio_evidence,
    )

    return server


if __name__ == "__main__":
    import json
    import sys

    srv = create_portfolio_mcp_server()
    for line in sys.stdin:
        if not line.strip():
            continue
        req = json.loads(line)
        res = srv.handle_mcp_message(req)
        sys.stdout.write(json.dumps(res) + "\n")
        sys.stdout.flush()
