# Chashire Cat AI tools for Industry 4.0 projects

## Introduction
TODO

Cheshire Cat AI [[website]](https://cheshire-cat-ai.github.io/docs/)

### Requirements

- Python 3.10 or higher
- `cheshire_cat_api` library [[github]](https://github.com/cheshire-cat-ai/api-client-py/tree/main)
- `requests` library (for HTTP operations)

### Installation

1. Clone this repository:
    ```bash
    git clone https://github.com/rmoscetti/cheshire-cat-client.git
    cd cheshire-cat-ai-tools
    ```

2. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Tool 1: Cheshire Cat API Client

A Python-based client for interacting with the Cheshire Cat AI server, an AI-agnostic conversational framework. This script establishes a WebSocket connection to send messages and retrieve responses in real-time. Its primary intent is to communicate with Cheshire Cat AI servers while prioritizing the use of procedural memory. Additionally, it supports optional chat history management and saving responses to a JSON file.

### Features

- **Send Messages**: Communicate with the Cheshire Cat AI server via WebSocket.
- **History Management**: Option to maintain or clear conversation history before sending messages.
- **Save Responses**: Store server responses in a JSON file.
- **Configurable**: Set user ID, authentication key, server URL, and other parameters via command-line arguments.

### Usage

1. Ensure the Cheshire Cat AI server is running and accessible at the specified `--base_url` and `--port`.

2. Run the script with the following command:
```bash
python cat_ws_client.py "your message here" --user_id YOUR_USER_ID --auth_key YOUR_AUTH_KEY [OPTIONS]
```

### Command-Line Arguments

| Argument      | Description                                                     | Default    | Required |
|---------------|-----------------------------------------------------------------|------------|----------|
| `message`     | The message to send to the server.                | N/A        | Yes      |
| `--user_id`   | The user ID for authentication.                                | N/A        | Yes      |
| `--auth_key`  | The authentication key (password) for the server.            | N/A        | Yes      |
| `--base_url`  | The base URL (IP address) of the server.                       | `127.0.0.1`| Yes       |
| `--port`      | The port number of the server.                           | `1865`     | Yes       |
| `--history`   | Set to `false` to clear the conversation history before sending the message. | `true` | No       |
| `--filename`  | The filename to save the JSON response from the server.        | N/A        | No       |
