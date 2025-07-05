# Multi-MCP Agent Service

This project demonstrates a simple FastAPI service that implements a reasoning and acting agent. The agent integrates multiple MCP (Multi-Coupled Process) services using the hub-spoke/adaptor pattern, leveraging the `fast-mcp` library.

## Project Structure

- `app/`: Main application directory.
  - `main.py`: FastAPI application setup, agent endpoint, and MCP hub registration.
  - `core/`: Core business logic.
    - `agent.py`: Defines the `Agent` class responsible for reasoning and dispatching tasks to MCPs.
  - `mcp_integrations/`: Contains MCP adaptors and example MCP implementations.
    - `simple_mcp.py`: An example of a simple MCP service.
    - `adaptor.py`: Contains adaptors (clients) for communicating with MCP services (e.g., `SimpleMCPAdaptor`).
- `requirements.txt`: Python dependencies.
- `README.md`: This file.

## Features

- FastAPI-based web service.
- A simple agent that can decide to delegate tasks to registered MCPs.
- MCP Hub provided by `fast-mcp` to expose multiple MCP services under a common prefix (e.g., `/mcp`).
- An example `SimpleMCP` that processes data.
- An `SimpleMCPAdaptor` that allows the agent to communicate with `SimpleMCP` using the `fast-mcp` client.
- Hub-spoke architecture: The agent acts as a hub, and MCPs are spokes, communicated with via adaptors.

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
    *Note*: If `fast-mcp` is a local or private library, you might need to adjust its entry in `requirements.txt` (e.g., `pip install -e path/to/fast-mcp` or `pip install git+https://...`).

4.  **Run the FastAPI application:**
    The application includes Uvicorn for development.
    ```bash
    python app/main.py
    ```
    The service will typically be available at `http://localhost:8000`.

## API Endpoints

-   **`GET /`**: Welcome message.
-   **`GET /docs`**: FastAPI Swagger UI for API documentation.
-   **`GET /redoc`**: FastAPI ReDoc documentation.
-   **`POST /agent/process`**: Endpoint for the agent to process requests.
    -   **Request Body Example (to use SimpleMCP):**
        ```json
        {
            "use_mcp": "simple_mcp",
            "data": {
                "key1": "value1",
                "detail": "some information"
            }
        }
        ```
    -   **Request Body Example (agent processes directly):**
        ```json
        {
            "data": {
                "info": "process this locally"
            }
        }
        ```
    -   **Success Response Example (using SimpleMCP):**
        ```json
        {
            "agent_response": "Data processed by simple_mcp",
            "mcp_response": {
                "message": "Data processed successfully by SimpleMCP",
                "processed_data": {
                    "processed_key1": "value1",
                    "processed_detail": "some information"
                }
            },
            "error": null
        }
        ```

-   **MCP Services (via `fast-mcp` hub):**
    -   The `SimpleMCP` is exposed under the `/mcp` prefix.
    -   **`POST /mcp/simple_mcp/process`**: The endpoint for the `SimpleMCP` itself.
        -   **Request Body Example:**
            ```json
            {
                "data": {"raw_key": "raw_value"}
            }
            ```
        -   **Response Example:**
            ```json
            {
                "message": "Data processed successfully by SimpleMCP",
                "processed_data": {
                    "processed_raw_key": "raw_value"
                }
            }
            ```

## How it Works

1.  The `FastAPI` app is initialized in `app/main.py`.
2.  An `MCPHub` instance from `fast-mcp` is created.
3.  The `SimpleMCP` (defined in `app/mcp_integrations/simple_mcp.py` with its own FastAPI router) is registered with the `MCPHub` under the name `simple_mcp`. This makes it available at `http://localhost:8000/mcp/simple_mcp`.
4.  An `Agent` instance (from `app/core/agent.py`) is created.
5.  A `SimpleMCPAdaptor` (from `app/mcp_integrations/adaptor.py`) is instantiated. This adaptor is a client specifically designed to talk to the `SimpleMCP`. It's configured with the URL where `SimpleMCP` is exposed (`http://localhost:8000/mcp/simple_mcp`).
6.  The `SimpleMCPAdaptor` instance is registered with the `Agent` under the name `simple_mcp`.
7.  When a request comes to the `/agent/process` endpoint:
    -   The request data is passed to the `agent_instance.process_request` method.
    -   The agent's logic checks if the `use_mcp` field specifies a known MCP (e.g., `simple_mcp`).
    -   If so, it retrieves the corresponding adaptor (e.g., `SimpleMCPAdaptor`) and uses it to call the `process` method of the `SimpleMCP`. The adaptor handles the HTTP call to `http://localhost:8000/mcp/simple_mcp/process`.
    -   The response from the MCP (via the adaptor) is then returned as part of the agent's response.
    -   If no MCP is specified or found, the agent handles the request with a default response.

This setup demonstrates how an agent can act as a central controller, delegating tasks to various specialized MCP services, which can be part of the same application or external services, as long as they adhere to the MCP communication contract facilitated by `fast-mcp`.
```
