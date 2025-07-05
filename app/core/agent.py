class Agent:
    def __init__(self):
        self.mcp_clients = {}

    def register_mcp_client(self, mcp_name, client):
        self.mcp_clients[mcp_name] = client

    async def process_request(self, request_data):
        """
        Simple reasoning: if the request_data contains a key 'use_mcp',
        it will try to use the MCP specified by that key.
        Otherwise, it returns a default response.
        """
        if "use_mcp" in request_data and request_data["use_mcp"] in self.mcp_clients:
            mcp_name = request_data["use_mcp"]
            client = self.mcp_clients[mcp_name]
            try:
                # Assuming the MCP client has a 'call' method
                # and the MCP expects 'data' in the request
                mcp_request_payload = {"data": request_data.get("data", {})}
                response = await client.call(method_name="process", data=mcp_request_payload) # Changed: Pass data directly
                return {"agent_response": f"Data processed by {mcp_name}", "mcp_response": response}
            except Exception as e:
                return {"error": f"Failed to call MCP {mcp_name}: {str(e)}"}
        else:
            return {"agent_response": "No specific MCP requested or MCP not found, processed by agent."}

# Global agent instance (can be managed by a dependency injection system in a real app)
agent_instance = Agent()
