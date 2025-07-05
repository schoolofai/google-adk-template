from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Any

from app.core.agent import agent_instance
from app.mcp_integrations.adaptor import SimpleMCPAdaptor
from app.mcp_integrations.simple_mcp import get_simple_mcp_router

from fast_mcp.hub import MCPHub
from fast_mcp.service_config import MCPServiceConfig

# Initialize FastAPI app
app = FastAPI(title="Google ADK-aligned Multi-MCP Agent Service")

# --- MCP Hub Setup ---
MCP_BASE_URL = "http://localhost:8000/mcp"
mcp_hub = MCPHub()

simple_mcp_service_name = "simple_mcp"
simple_mcp_router = get_simple_mcp_router()
mcp_hub.register_service(
    MCPServiceConfig(
        name=simple_mcp_service_name,
        router=simple_mcp_router,
    )
)
app.include_router(mcp_hub.router, prefix="/mcp")

# --- Agent Setup (ADK-aligned) ---
# Registering the SimpleMCPAdaptor as a "tool" for the agent.
# The agent will use this client adaptor to *call* the SimpleMCP tool.
simple_mcp_client_adaptor = SimpleMCPAdaptor(base_url=MCP_BASE_URL, service_name=simple_mcp_service_name)
agent_instance.register_mcp_client(tool_name=simple_mcp_service_name, client=simple_mcp_client_adaptor)


# --- API Endpoints (ADK-aligned) ---
class AgentInstructionRequest(BaseModel):
    instruction: str  # Primary instruction for the agent (natural language or command)
    data: dict | None = {}  # Supporting data for the instruction or for the tool

class AgentInstructionResponse(BaseModel):
    agent_action: str
    tool_response: Any | None = None
    result: Any | None = None
    status: str # e.g., "success", "error", "unclear_instruction"
    error_message: str | None = None
    instruction_received: str | None = None


@app.post("/agent/execute", response_model=AgentInstructionResponse)
async def execute_agent_instruction(request: AgentInstructionRequest):
    """
    Endpoint for the agent to execute tasks based on instructions.
    The agent processes the instruction and may use registered tools (MCPs).
    """
    try:
        # Pass instruction and data to the agent's processing method
        result = await agent_instance.process_instruction(
            instruction=request.instruction,
            data=request.data
        )
        # Ensure all fields in AgentInstructionResponse are covered by the result dict
        # or provide defaults.
        response_data = {
            "agent_action": result.get("agent_action", "No action specified"),
            "tool_response": result.get("tool_response"),
            "result": result.get("result"),
            "status": result.get("status", "unknown"),
            "error_message": result.get("error_message"),
            "instruction_received": result.get("instruction_received", request.instruction if result.get("status") == "unclear_instruction" else None)
        }
        return AgentInstructionResponse(**response_data)
    except Exception as e:
        # This is a fallback for unexpected errors in the endpoint/agent interaction logic
        # Errors from tools should ideally be caught and structured by the agent itself.
        return AgentInstructionResponse(
            agent_action="Failed to process instruction due to unexpected error.",
            status="error",
            error_message=str(e)
        )

@app.get("/")
async def read_root():
    return {"message": "Welcome to the Google ADK-aligned Multi-MCP Agent Service. Visit /docs for API."}

# --- Main block for running with Uvicorn (for development) ---
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
