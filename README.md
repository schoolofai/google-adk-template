# Google ADK-aligned Multi-MCP Agent Service

This project demonstrates a FastAPI service implementing an agent that follows Google Agent Development Kit (ADK) principles. The agent processes instructions and can leverage multiple MCP (Multi-Coupled Process) services as "tools" using the `fast-mcp` library for integration.

## Core ADK Principles Applied

-   **Instruction-Based Operation:** The agent receives tasks via natural language instructions or structured commands.
-   **Tool Usage:** The agent utilizes registered MCP services as tools to perform specific actions.
-   **Reasoning:** A simple reasoning process within the agent determines which tool to use (if any) based on the instruction.

## Project Structure

- `app/`: Main application directory.
  - `main.py`: FastAPI application setup, ADK-aligned agent endpoint (`/agent/execute`), and MCP hub registration.
  - `core/`: Core agent logic.
    - `agent.py`: Defines the `Agent` class. Its `process_instruction` method embodies the reasoning and tool dispatch logic.
  - `mcp_integrations/`: Contains MCP adaptors and example MCP implementations (tools).
    - `simple_mcp.py`: An example of a simple MCP service (a tool).
    - `adaptor.py`: Contains adaptors (clients) for communicating with MCP services (e.g., `SimpleMCPAdaptor`).
- `requirements.txt`: Python dependencies.
- `README.md`: This file.

## Features

- FastAPI-based web service.
- An agent designed around ADK principles: receives instructions, reasons, and uses tools.
- MCP Hub (`fast-mcp`) exposes MCP services (tools) under a common prefix (e.g., `/mcp`).
- An example `SimpleMCP` that processes data, acting as a sample tool.
- An `SimpleMCPAdaptor` enabling the agent to communicate with `SimpleMCP`.

## Setup and Running

1.  **Clone the repository (if applicable)**
    ```bash
    # git clone ...
    # cd project-directory
    ```

2.  **Create a virtual environment and activate it:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    *Note*: If `fast-mcp` is a local or private library, you might need to adjust its entry in `requirements.txt`.

4.  **Run the FastAPI application:**
    ```bash
    python app/main.py
    ```
    The service will typically be available at `http://localhost:8000`.

## API Endpoints

-   **`GET /`**: Welcome message.
-   **`GET /docs`**: FastAPI Swagger UI for API documentation.
-   **`GET /redoc`**: FastAPI ReDoc documentation.
-   **`POST /agent/execute`**: Endpoint for the agent to process instructions.
    -   **Request Body Example (to use SimpleMCP tool):**
        ```json
        {
            "instruction": "Please use simple_mcp to process the following details.",
            "data": {
                "mcp_data": { // This data will be passed to the simple_mcp tool
                    "key1": "value1",
                    "detail": "some information"
                }
            }
        }
        ```
    -   **Request Body Example (agent handles locally):**
        ```json
        {
            "instruction": "Perform a local task with this data.",
            "data": {
                "info": "process this locally"
            }
        }
        ```
    -   **Success Response Example (using SimpleMCP tool):**
        ```json
        {
            "agent_action": "Used tool 'simple_mcp' based on instruction.",
            "tool_response": {
                "message": "Data processed successfully by SimpleMCP",
                "processed_data": {
                    "processed_key1": "value1",
                    "processed_detail": "some information"
                }
            },
            "result": null,
            "status": "success",
            "error_message": null,
            "instruction_received": null
        }
        ```
     -   **Response Example (unclear instruction):**
        ```json
        {
            "agent_action": "No specific tool or local task identified for instruction.",
            "tool_response": null,
            "result": null,
            "status": "unclear_instruction",
            "error_message": null,
            "instruction_received": "Tell me a joke."
        }
        ```

-   **MCP Services (Tools via `fast-mcp` hub):**
    -   The `SimpleMCP` tool is exposed under the `/mcp` prefix.
    -   **`POST /mcp/simple_mcp/process`**: The endpoint for the `SimpleMCP` tool itself.
        -   **Request Body Example:**
            ```json
            {
                "data": {"raw_key": "raw_value"}
            }
            ```

## How it Works (ADK Alignment)

1.  The `FastAPI` app is initialized in `app/main.py`.
2.  An `MCPHub` instance from `fast-mcp` is created.
3.  The `SimpleMCP` (defined in `app/mcp_integrations/simple_mcp.py`) is registered with the `MCPHub` under the name `simple_mcp`. This makes it available as a tool at `http://localhost:8000/mcp/simple_mcp`.
4.  An `Agent` instance (from `app/core/agent.py`) is created. This agent is designed to follow ADK principles.
5.  A `SimpleMCPAdaptor` (from `app/mcp_integrations/adaptor.py`) is instantiated. This adaptor acts as the client for the `SimpleMCP` tool.
6.  The `SimpleMCPAdaptor` instance is registered with the `Agent` as a tool named `simple_mcp`.
7.  When a request comes to the `/agent/execute` endpoint:
    -   The `instruction` and `data` from the request are passed to the `agent_instance.process_instruction` method.
    -   The agent's logic (currently simple keyword matching on the `instruction`) attempts to understand the user's intent.
    -   If the instruction indicates the use of a known tool (e.g., "use simple_mcp"), the agent retrieves the corresponding adaptor (e.g., `SimpleMCPAdaptor`) and uses it to call the `process` method of the `SimpleMCP` tool.
    -   The response from the tool (via the adaptor) is then included in the agent's overall response.
    -   If the instruction points to a local agent capability (e.g., "local task") or is not understood, the agent responds accordingly.

This setup demonstrates how an agent, guided by ADK principles, can interpret instructions and delegate tasks to specialized tools (MCP services), all orchestrated within a FastAPI application.
```
