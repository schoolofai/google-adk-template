class Agent:
    def __init__(self):
        self.mcp_clients = {} # These are the "tools" the agent can use

    def register_mcp_client(self, tool_name, client):
        """Registers an MCP client as a tool for the agent."""
        self.mcp_clients[tool_name] = client

    async def process_instruction(self, instruction: str, data: dict | None = None):
        """
        Processes a given instruction, potentially using tools (MCPs).
        This is a simplified reasoning process. A more advanced ADK-aligned agent
        might involve more sophisticated NLP for instruction parsing, intent recognition,
        and slot filling.

        :param instruction: A textual instruction or goal for the agent.
        :param data: Additional data accompanying the instruction.
        """
        if data is None:
            data = {}

        # Simple keyword-based routing to tools.
        # In a more complex ADK, this would be an NLU/intent matching step.
        if "use simple_mcp" in instruction.lower() and "simple_mcp" in self.mcp_clients:
            tool_name = "simple_mcp"
            client = self.mcp_clients[tool_name]
            try:
                # The 'data' for the MCP call should be what the MCP expects.
                # We assume the top-level 'data' field in the agent request is meant for the MCP.
                mcp_payload = {"data": data.get("mcp_data", data)} # Allow nesting or pass directly
                response = await client.call(method_name="process", data=mcp_payload)
                return {
                    "agent_action": f"Used tool '{tool_name}' based on instruction.",
                    "tool_response": response,
                    "status": "success"
                }
            except Exception as e:
                return {
                    "agent_action": f"Attempted to use tool '{tool_name}' but failed.",
                    "error_message": str(e),
                    "status": "error"
                }
        elif "local task" in instruction.lower():
            # Example of the agent handling a task directly
            return {
                "agent_action": "Handled instruction locally.",
                "result": {"message": "Local task executed successfully.", "received_data": data},
                "status": "success"
            }
        else:
            return {
                "agent_action": "No specific tool or local task identified for instruction.",
                "instruction_received": instruction,
                "status": "unclear_instruction"
            }

# Global agent instance
agent_instance = Agent()
