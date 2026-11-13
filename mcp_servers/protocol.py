"""Model Context Protocol (MCP) Core Protocol Schemas and Base Server."""

from typing import Any, Callable, Dict, List, Optional

from pydantic import BaseModel, Field


class MCPToolAnnotation(BaseModel):
    readOnlyHint: bool = False
    destructiveHint: bool = False
    idempotentHint: bool = False


class MCPToolDefinition(BaseModel):
    name: str
    description: str
    inputSchema: Dict[str, Any]
    outputSchema: Optional[Dict[str, Any]] = None
    annotations: MCPToolAnnotation = Field(default_factory=MCPToolAnnotation)


class MCPResourceDefinition(BaseModel):
    uri: str
    name: str
    description: Optional[str] = None
    mimeType: str = "text/plain"


class MCPPromptArgument(BaseModel):
    name: str
    description: Optional[str] = None
    required: bool = False


class MCPPromptDefinition(BaseModel):
    name: str
    description: Optional[str] = None
    arguments: List[MCPPromptArgument] = Field(default_factory=list)


class MCPRequest(BaseModel):
    jsonrpc: str = "2.0"
    id: Optional[str | int] = None
    method: str
    params: Optional[Dict[str, Any]] = Field(default_factory=dict)


class MCPResponse(BaseModel):
    jsonrpc: str = "2.0"
    id: Optional[str | int] = None
    result: Optional[Any] = None
    error: Optional[Dict[str, Any]] = None


class BaseMCPServer:
    def __init__(self, name: str, version: str = "1.0.0"):
        self.name = name
        self.version = version
        self.tools: Dict[str, MCPToolDefinition] = {}
        self.tool_handlers: Dict[str, Callable[..., Any]] = {}
        self.resources: Dict[str, MCPResourceDefinition] = {}
        self.resource_handlers: Dict[str, Callable[[str], Any]] = {}
        self.prompts: Dict[str, MCPPromptDefinition] = {}
        self.prompt_handlers: Dict[str, Callable[..., str]] = {}

    def register_tool(
        self,
        name: str,
        description: str,
        input_schema: Dict[str, Any],
        handler: Callable[..., Any],
        annotations: Optional[MCPToolAnnotation] = None,
        output_schema: Optional[Dict[str, Any]] = None,
    ):
        tool_def = MCPToolDefinition(
            name=name,
            description=description,
            inputSchema=input_schema,
            outputSchema=output_schema,
            annotations=annotations or MCPToolAnnotation(),
        )
        self.tools[name] = tool_def
        self.tool_handlers[name] = handler

    def register_resource(
        self,
        uri_pattern: str,
        name: str,
        description: str,
        handler: Callable[[str], Any],
        mime_type: str = "text/plain",
    ):
        res_def = MCPResourceDefinition(
            uri=uri_pattern, name=name, description=description, mimeType=mime_type
        )
        self.resources[uri_pattern] = res_def
        self.resource_handlers[uri_pattern] = handler

    def register_prompt(
        self,
        name: str,
        description: str,
        arguments: List[MCPPromptArgument],
        handler: Callable[..., str],
    ):
        prompt_def = MCPPromptDefinition(
            name=name, description=description, arguments=arguments
        )
        self.prompts[name] = prompt_def
        self.prompt_handlers[name] = handler

    def list_tools(self) -> List[Dict[str, Any]]:
        return [t.model_dump() for t in self.tools.values()]

    def call_tool(self, tool_name: str, arguments: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Any:
        if tool_name not in self.tool_handlers:
            raise KeyError(f"Tool '{tool_name}' not registered on server '{self.name}'.")
        handler = self.tool_handlers[tool_name]
        return handler(**arguments)

    def list_resources(self) -> List[Dict[str, Any]]:
        return [r.model_dump() for r in self.resources.values()]

    def read_resource(self, uri: str) -> Any:
        # Match exact or prefix
        for pattern, handler in self.resource_handlers.items():
            if uri == pattern or uri.startswith(pattern.replace("{id}", "")):
                return handler(uri)
        raise KeyError(f"Resource uri '{uri}' not found on server '{self.name}'.")

    def list_prompts(self) -> List[Dict[str, Any]]:
        return [p.model_dump() for p in self.prompts.values()]

    def get_prompt(self, name: str, arguments: Dict[str, Any]) -> str:
        if name not in self.prompt_handlers:
            raise KeyError(f"Prompt '{name}' not registered on server '{self.name}'.")
        return self.prompt_handlers[name](**arguments)

    def handle_mcp_message(self, request_data: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Dispatch JSON-RPC message."""
        method = request_data.get("method")
        params = request_data.get("params", {})
        msg_id = request_data.get("id")

        try:
            if method == "initialize":
                res = {
                    "protocolVersion": "2024-11-05",
                    "serverInfo": {"name": self.name, "version": self.version},
                    "capabilities": {"tools": {}, "resources": {}, "prompts": {}},
                }
            elif method == "tools/list":
                res = {"tools": self.list_tools()}
            elif method == "tools/call":
                name = params.get("name")
                args = params.get("arguments", {})
                tool_result = self.call_tool(name, args, context=context)
                res = {"content": [{"type": "text", "text": str(tool_result)}], "result": tool_result}
            elif method == "resources/list":
                res = {"resources": self.list_resources()}
            elif method == "resources/read":
                uri = params.get("uri")
                content = self.read_resource(uri)
                res = {"contents": [{"uri": uri, "mimeType": "text/plain", "text": str(content)}]}
            elif method == "prompts/list":
                res = {"prompts": self.list_prompts()}
            elif method == "prompts/get":
                name = params.get("name")
                args = params.get("arguments", {})
                prompt_text = self.get_prompt(name, args)
                res = {"description": name, "messages": [{"role": "user", "content": {"type": "text", "text": prompt_text}}]}
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "error": {"code": -32601, "message": f"Method '{method}' not found"},
                }
            return {"jsonrpc": "2.0", "id": msg_id, "result": res}
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "error": {"code": -32000, "message": str(e)},
            }
