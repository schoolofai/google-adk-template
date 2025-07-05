from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from typing import Any

from app.core.agent import agent_instance
from app.mcp_integrations.adaptor import SimpleMCPAdaptor
from app.mcp_integrations.simple_mcp import get_simple_mcp_router

from fast_mcp.hub import MCPHub
from fast_mcp.service_config import MCPServiceConfig

# Initialize FastAPI app
app = FastAPI(title="Multi-MCP Agent Service")

# --- MCP Hub Setup ---
# Define the base URL for MCP services from environment or default
# In a real deployment, this would come from configuration
MCP_BASE_URL = "http://localhost:8000/mcp" # This service's own MCP endpoint

mcp_hub = MCPHub()

# Register SimpleMCP
simple_mcp_service_name = "simple_mcp"
simple_mcp_router = get_simple_mcp_router()
mcp_hub.register_service(
    MCPServiceConfig(
        name=simple_mcp_service_name,
        router=simple_mcp_router,
        # No client needed here as this is the service being exposed
    )
)

# Include the MCP Hub router
# All registered MCP services will be available under /mcp/{service_name}
app.include_router(mcp_hub.router, prefix="/mcp")

# --- Agent Setup ---
# Instantiate and register the adaptor for SimpleMCP with the agent
# The agent will use this client adaptor to *call* the SimpleMCP.
# Even though SimpleMCP is hosted in this same application, the agent interacts with it
# via the MCP standard, so it needs a client configured to its own /mcp/simple_mcp endpoint.
simple_mcp_client_adaptor = SimpleMCPAdaptor(base_url=MCP_BASE_URL, service_name=simple_mcp_service_name)
agent_instance.register_mcp_client(simple_mcp_service_name, simple_mcp_client_adaptor)


# --- API Endpoints ---
class AgentRequest(BaseModel):
    use_mcp: str | None = None # Name of the MCP to use
    data: dict | None = {}       # Data to be processed by agent or passed to MCP

class AgentResponse(BaseModel):
    agent_response: str | dict
    mcp_response: Any | None = None
    error: str | None = None

@app.post("/agent/process", response_model=AgentResponse)
async def process_agent_request(request: AgentRequest):
    """
    Endpoint for the agent to process requests.
    The agent might decide to use one of its registered MCPs.
    """
    try:
        result = await agent_instance.process_request(request.model_dump()) # Use model_dump() for Pydantic v2
        return AgentResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def read_root():
    return {"message": "Welcome to the Multi-MCP Agent Service. Visit /docs for API documentation."}

# --- Main block for running with Uvicorn (for development) ---
if __name__ == "__main__":
    import uvicorn
    # It's important that the reload flag is False or that you use a production ASGI server
    # if you have background tasks or state that should not be re-initialized on every reload.
    uvicorn.run(app, host="0.0.0.0", port=8000)
