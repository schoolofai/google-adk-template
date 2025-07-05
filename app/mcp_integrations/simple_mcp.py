from fastapi import FastAPI, APIRouter
from pydantic import BaseModel

# Define a request model for the MCP
class SimpleMCPRequest(BaseModel):
    data: dict

# Define a response model for the MCP
class SimpleMCPResponse(BaseModel):
    message: str
    processed_data: dict

# Create a router for this MCP
simple_mcp_router = APIRouter()

@simple_mcp_router.post("/process", response_model=SimpleMCPResponse)
async def process_data(request: SimpleMCPRequest):
    """
    A simple MCP method that processes data.
    """
    # In a real MCP, this would involve more complex logic
    processed_data = {f"processed_{k}": v for k, v in request.data.items()}
    return SimpleMCPResponse(
        message="Data processed successfully by SimpleMCP",
        processed_data=processed_data
    )

# This function will be used by fast-mcp to get the router
def get_simple_mcp_router():
    return simple_mcp_router

# For standalone testing of this MCP (optional)
if __name__ == "__main__":
    import uvicorn
    app = FastAPI()
    app.include_router(simple_mcp_router, prefix="/simple_mcp")
    uvicorn.run(app, host="0.0.0.0", port=8001)
