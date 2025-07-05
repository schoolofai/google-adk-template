from fast_mcp.client import MCPClient

class SimpleMCPAdaptor:
    def __init__(self, base_url: str, service_name: str = "simple_mcp"):
        """
        Adaptor for the SimpleMCP.
        :param base_url: The base URL where the SimpleMCP is hosted (e.g., http://localhost:8000/mcp)
        :param service_name: The name under which the SimpleMCP is registered in the fast-mcp hub.
        """
        # The MCPClient from fast-mcp will handle the actual communication.
        # The full URL to the service will be base_url + / + service_name
        self.client = MCPClient(service_url=f"{base_url}/{service_name}")

    async def call(self, method_name: str, data: dict):
        """
        Calls a method on the SimpleMCP.
        :param method_name: The name of the method to call (e.g., "process").
        :param data: The data to send to the MCP method.
        """
        try:
            # fast-mcp client's call method takes the method name and keyword arguments for the Pydantic model
            response = await self.client.call(method_name, **data)
            return response
        except Exception as e:
            # Handle or log the exception appropriately
            print(f"Error calling MCP method {method_name} on {self.client.service_url}: {e}")
            raise

# Example usage (not part of the class, just for illustration)
async def example_adaptor_usage():
    # This assumes the main FastAPI app is running and has the simple_mcp registered
    # at /mcp/simple_mcp
    adaptor = SimpleMCPAdaptor(base_url="http://localhost:8000/mcp", service_name="simple_mcp")
    try:
        response = await adaptor.call(method_name="process", data={"data": {"key": "value"}})
        print("Response from SimpleMCP via adaptor:", response)
    except Exception as e:
        print(f"Adaptor usage example failed: {e}")

if __name__ == "__main__":
    import asyncio
    # To run this example, you'd need the main FastAPI service running with the MCP.
    # This is just to show how the adaptor would be instantiated and used.
    # asyncio.run(example_adaptor_usage())
    print("SimpleMCPAdaptor defined. Run the main FastAPI application to test it.")
