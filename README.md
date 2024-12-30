# Cheshire Cat API Client

A Python-based client for interacting with the Cheshire Cat API, an AI-powered conversational model. This script establishes a WebSocket connection to send messages and retrieve responses in real-time. Additionally, it supports optional history management and saving responses to a JSON file.

## Features

- **Send Messages**: Communicate with the Cheshire Cat AI server via WebSocket.
- **History Management**: Option to maintain or clear conversation history before sending messages.
- **Save Responses**: Store server responses in a JSON file.
- **Configurable**: Set user ID, authentication key, server URL, and other parameters via command-line arguments.

## Requirements

- Python 3.10 or higher
- `cheshire_cat_api` library
- `requests` library (for HTTP operations)

## Installation

1. Clone this repository:
    ```bash
    git clone https://github.com/rmoscetti/cheshire-cat-client.git
    cd cheshire-cat-client
    ```

2. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3. Ensure the Cheshire Cat AI server is running and accessible at the specified `--base_url` and `--port`.

## Usage

Run the script with the following command:
```bash
python cat_ws_client.py "your message" --user_id YOUR_USER_ID --auth_key YOUR_AUTH_KEY [OPTIONS]

| Argument      | Description                                                     | Default    | Required |
|---------------|-----------------------------------------------------------------|------------|----------|
| `message`     | The message to send to the Cheshire Cat server.                | N/A        | Yes      |
| `--user_id`   | The user ID for authentication.                                | N/A        | Yes      |
| `--auth_key`  | The authentication key for the Cheshire Cat server.            | N/A        | Yes      |
| `--base_url`  | The base URL of the Cheshire Cat server.                       | 127.0.0.1  | No       |
| `--port`      | The port of the Cheshire Cat server.                           | 1865       | No       |
| `--history`   | Set to false to clear the conversation history before sending the message. | true       | No       |
| `--filename`  | The filename to save the JSON response from the server.        | N/A        | No       |
