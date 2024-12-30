# Chashire Cat AI tools for Industry 4.0/5.0 projects

## Introduction
TODO
Cheshire Cat AI, an AI-agnostic conversational framework [[website]](https://cheshire-cat-ai.github.io/docs/)

### Requirements
- Python 3.10 or higher
- `cheshire_cat_api` library [[github]](https://github.com/cheshire-cat-ai/api-client-py/tree/main)
- `requests` library (for HTTP operations)

### Installation
1. Clone this repository:
    ```bash
    git clone https://github.com/rmoscetti/chashire-cat-ai-tools.git
    cd cheshire-cat-ai-tools
    ```
2. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Tool 1: Cheshire Cat API Client
`cat_ws_client.py` is a python-based client for interacting with the Cheshire Cat AI server. This script establishes a WebSocket connection to send messages and retrieve responses in real-time. Its primary intent is to communicate with Cheshire Cat AI servers while prioritizing the use of procedural memory by removing the history chat. Additionally, it supports optional chat history management and saving responses to a JSON file.

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
| `--history`   | Set to `false` to clear the conversation history before sending the message. | `false` | Yes       |
| `--filename`  | The filename to save the JSON response from the server.        | N/A        | No       |

### Examples
To send a message and save the response:
```bash
python cat_ws_client.py "What time is it?" --user_id USER123 --auth_key ABC123 --filename response.json
```
To send a message without clearing the chat history:
```bash
python cat_ws_client.py "What time is it?" --user_id USER123 --auth_key ABC123 --history true
```
To clear history before sending a message:
```bash
python cat_ws_client.py "What time is it?" --user_id USER123 --auth_key ABC123 --history false
```

## Contributing
Contributions are welcome! Feel free to fork this repository, make your changes, and submit a pull request.

## License
This project is licensed under the MIT License. See the [LICENSE](https://mit-license.org/) for details.

##Author
Roberto Moscetti rmoscetti@unitus.it
