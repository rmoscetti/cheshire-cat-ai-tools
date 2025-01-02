"""
Author: Roberto Moscetti
Version: 1.0

Description:
This script serves as a Python client for interacting with the Cheshire Cat API (https://github.com/cheshire-cat-ai/api-client-py/tree/main),
an AI-powered conversational model. It establishes a WebSocket connection with 
the Cheshire Cat server to send messages and handle responses in real-time.

Features:
- Sends a message to the server via WebSocket and waits for a response.
- Supports clearing the conversation history using an HTTP DELETE request.
- Saves the server's response in a JSON file if a filename is provided.
- Allows configuration of user ID, authentication key, base URL, and port via command-line arguments.
- Optionally maintains or clears the conversation history based on the `--history` argument.

Dependencies:
- `cheshire_cat_api` library for interfacing with the Cheshire Cat server.
- `requests` library for sending HTTP/1.1 requests
- Standard Python libraries: `time`, `json`, `threading`, `logging`, `argparse`.

Usage:
Run the script with the required arguments. For example:
    python script.py "your message here" --base_url 127.0.0.1 --port 1865 --user_id USER123 --auth_key ABC123 --history False --filename "response.json"
"""

import time # For handling delays and timeouts
import json # For encoding and decoding JSON messages
import threading # For synchronization between WebSocket events
import logging # For logging messages and errors
import requests # For making HTTP requests (e.g., to clear conversation history)
import argparse # For parsing command-line arguments
import cheshire_cat_api as ccat # Cheshire Cat API library for WebSocket interactions

# Global variable to store the filename where the JSON response will be saved.
# It is set to None initially and will be updated when the `--filename` argument is provided.
filename = None

# Configure logging
logging.basicConfig(level=logging.INFO)

# Event for synchronization
close_event = threading.Event()

def my_custom_message_handler(message: str):
    """
    Custom handler for messages received from the WebSocket.
    
    Decodes the incoming message and, if valid, saves it as a JSON string 
    in the global variable `filename` if it is set. Signals the event to 
    indicate that a message has been processed.
    """
    global filename
    try:
        answer = json.loads(message)
        if answer.get('type') != 'chat_token': # Ignore 'chat_token' messages
            #logging.info("JSON: %s", answer)
            json_str = json.dumps(answer, indent=4)
            if filename: # Save JSON to file if filename is provided
                with open(filename, 'w') as f:
                    f.write(json_str)
            else: # Send JSON to the prompt if filename is not provided
                print(json_str)
            close_event.set()
    except json.JSONDecodeError as e:
        logging.error("Failed to decode message: %s", e)

def setup_client(base_url, port, user_id, auth_key):
    """
    Configures and returns the Cheshire Cat client.
    
    Args:
        base_url (str): The base URL of the Cheshire Cat server.
        port (int): The port number for the Cheshire Cat server.
        user_id (str): The user ID for authentication.
        auth_key (str): The authentication key.
    
    Returns:
        ccat.CatClient: The configured client instance.
    """
    config = ccat.Config(
        base_url=base_url,
        port=port,
        user_id=user_id,
        auth_key=auth_key
    )
    return ccat.CatClient(config=config, on_message=my_custom_message_handler)

def wait_for_connection(client, timeout=10):
    """
    Waits for the WebSocket to connect within the specified timeout period.
    
    Args:
        client (ccat.CatClient): The Cheshire Cat client instance.
        timeout (int): The maximum time to wait for the connection (in seconds).
    
    Raises:
        TimeoutError: If the WebSocket fails to connect within the timeout.
    """
    start_time = time.time()
    while not client.is_ws_connected:
        time.sleep(1)
        if time.time() - start_time > timeout:
            raise TimeoutError("Failed to connect to WebSocket within timeout.")

def clear_history(base_url, port, user_id):
    """
    Clears the conversation history via an HTTP DELETE request.
    
    Args:
        base_url (str): The base URL of the Cheshire Cat server.
        port (int): The port number for the Cheshire Cat server.
        user_id (str): The user ID for authentication.
    
    Logs:
        Success or failure of the history clearing operation.
    """
    url = f"http://{base_url}:{port}/memory/conversation_history"
    headers = {
        "Content-Type": "application/json",
        "User_id": user_id
    }
    try:
        response = requests.delete(url, headers=headers)
        if response.status_code == 200:
            logging.info("Episodic memory successfully cleared.")
        else:
            logging.warning("Failed to clear Episodic memory: %s", response.text)
    except requests.RequestException as e:
        logging.error("Error during Episodic memory clearing: %s", e)

def parse_history_argument(history_str):
    """
    Parses the `--history` argument string into a boolean value, handling potential errors.

    Args:
        history_str (str): The value passed for the `--history` argument.

    Returns:
        bool: True if the argument is "true" (case-insensitive), False otherwise.

    Raises:
        ValueError: If the argument is neither "true" nor "false".
    """
    history_str = history_str.lower() # Convert to lowercase for case-insensitive comparison
    if history_str == "true":
        return True
    elif history_str == "false":
        return False
    else:
        raise ValueError("--history argument must be either 'true' or 'false'.")

def main(message, user_id, auth_key, base_url, port, history, file):
    """
    Executes the WebSocket client interaction.

    Args:
        message (str): The message to send to the server.
        user_id (str): The user ID for authentication.
        auth_key (str): The authentication key.
        base_url (str): The base URL of the Cheshire Cat server.
        port (int): The port number for the Cheshire Cat server.
        history (bool): Whether to clear the conversation history.
        file (str): The filename to save the response as JSON.
    """
    global filename
    filename = file
    
    # Clear conversation history if requested
    if history == False:
        clear_history(base_url, port, user_id)
    else:
        logging.info("Episodic memory successfully maintained.")
        
    # Configure and run the WebSocket client
    cat_client = setup_client(base_url, port, user_id, auth_key)
    try:
        cat_client.connect_ws()
        wait_for_connection(cat_client)
        cat_client.send(message=message)
        if not close_event.wait(timeout=60):
            logging.warning("Timeout waiting for server response.")
    finally:
        cat_client.close()

if __name__ == "__main__":
    # Configure argparse to handle command-line arguments
    parser = argparse.ArgumentParser(description="Cheshire Cat API Chat Script")
    parser.add_argument(
        "message", 
        type=str, 
        help="The message to send to the server"
    )
    parser.add_argument(
        "--user_id", 
        type=str, 
        required=True,
        help="The user ID for authentication"
    )
    parser.add_argument(
        "--auth_key", 
        type=str, 
        required=True,
        help="The authentication key (your password)"
    )
    parser.add_argument(
        "--base_url", 
        type=str, 
        default="127.0.0.1",
        help="The base URL of the Cheshire Cat server (default: 127.0.0.1)"
    )
    parser.add_argument(
        "--port", 
        type=int, 
        default=1865,
        help="The port number of the Cheshire Cat server (default: 1865)"
    )
    parser.add_argument(
        "--history", 
        type=str, 
        default="false",
        help="Whether to maintain (true) or clear (false) the conversation history (default: false)"
    )
    parser.add_argument(
        "--filename", 
        type=str, 
        help="Filename to save the response as a JSON file (if not specified, no file is saved)"
    )
    args = parser.parse_args()
    
    try:
        history = parse_history_argument(args.history)
    except ValueError as e:
        logging.error(str(e))
        exit(1) # Exit with an error code
    
    # Pass the specified arguments to main()
    main(
        message=args.message, 
        user_id=args.user_id, 
        auth_key=args.auth_key, 
        base_url=args.base_url, 
        port=args.port,
        history=history,
        file=args.filename,
    )
