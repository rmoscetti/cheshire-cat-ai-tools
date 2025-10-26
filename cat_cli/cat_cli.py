"""
Author: Roberto Moscetti
Version: 1.1

Description:
This script serves as a Python client for interacting with the Cheshire Cat API (https://github.com/cheshire-cat-ai/api-client-py/tree/main),
an AI-powered conversational model. It establishes a WebSocket connection with 
the Cheshire Cat server to send messages and handle responses in real-time.

Enhancements in Version 1.1:
- **Added `--log` argument**: Enables logging for debugging and informational messages.
- **Added `--timeout` argument**: Allows customization of the maximum wait time for a response from the AI (default: 300 sec).
- **Added `--notext` argument**: Displays the full JSON response instead of only AI-generated text when enabled.
- **Added `--reasoning` argument**: Displays Deepseek AI reasoning (if available) alongside the response when enabled.
- **Updated `--history` argument**: Now uses `store_true` to simplify usage.
- **Improved argument parsing and validation**: Added boolean parsing for `--history`, `--notext`, and `--reasoning` to ensure proper handling.

Features:
- Sends a message to the server via WebSocket and waits for a response.
- Supports clearing the conversation history using an HTTP DELETE request.
- Saves the server's response in a JSON file if a filename is provided.
- Allows configuration of user ID, authentication key, base URL, and port via command-line arguments.
- Optionally maintains or clears the conversation history based on the `--history` argument.
- Provides optional reasoning output from the AI for transparency.
- Supports logging and response timeout configuration for better debugging and control.

Dependencies:
- `cheshire_cat_api` library for interfacing with the Cheshire Cat server.
- `requests` library for sending HTTP/1.1 requests.
- Standard Python libraries: `time`, `json`, `threading`, `logging`, `argparse`, `re`.

Usage:
Run the script with the required arguments. For example:
```bash
python script.py "your message here" --base_url 127.0.0.1 --port 1865 --user_id USER123 --auth_key ABC123 --log --timeout 300 --notext --reasoning --history --filename "response.json"
"""

import time # For handling delays and timeouts
import json # For encoding and decoding JSON messages
import threading # For synchronization between WebSocket events
import logging # For logging messages and errors
import requests # For making HTTP requests (e.g., to clear conversation history)
import argparse # For parsing command-line arguments
import cheshire_cat_api as ccat # Cheshire Cat API library for WebSocket interactions
import re # For regular expression operations

# Global variables 
filename = None # to store the filename where the JSON response will be saved (default = None)

# Event for synchronization
close_event = threading.Event()

def my_custom_message_handler(message: str):
    """
    Custom handler for messages received from the WebSocket.
    
    Decodes the incoming message and, if valid, saves it as a JSON string 
    in the global variable `filename` if it is set. Signals the event to 
    indicate that a message has been processed.
    """
    global filename, notext, reasoning
    
    try:
        answer = json.loads(message)
        if answer.get('type') != 'chat_token': # Ignore 'chat_token' messages
            #logging.info("JSON: %s", answer)
            json_str = json.dumps(answer, indent=4)
            if filename: # Save JSON to file if filename is provided
                with open(filename, 'w') as f:
                    f.write(json_str)
            if notext: # Display full JSON response
                print(json_str)
            else: # Display only the AI's response
                ai_think = re.findall(r"<think>\s*(.*?)\s*</think>", answer.get('text'), re.DOTALL)
                ai_text = re.sub(r"<think>\s*.*?\s*</think>", "", answer.get('text', ""), flags=re.DOTALL).strip()
                if ai_think and reasoning:
                    print("\033[95m\n**Reasoning**\n" + ai_think[0] + "\033[95m\n\033[92m\n**Answer**\n" + ai_text + "\033[0m\n")
                elif ai_think:
                    print("\033[92m\n**Answer**\n" + ai_text + "\033[0m\n")
                else:
                    print("\033[92m\n**Answer**\n" + answer.get('text') + "\033[0m\n")
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
            raise TimeoutError("Failed to connect to WebSocket within timeout (10 sec).")

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

def main(message, user_id, auth_key, base_url, port, timeout, _notext, _reasoning, history, _filename):
    """
    Establishes a WebSocket connection with the Cheshire Cat server to send a message and handle the response.

    Args:
        message (str): The message to be sent to the Cheshire Cat server.
        user_id (str): The user ID used for authentication.
        auth_key (str): The authentication key for secure access.
        base_url (str): The base URL of the Cheshire Cat server.
        port (int): The port number on which the server is running.
        timeout (int): Maximum time (in seconds) to wait for a response from the AI before timing out (default: 300 sec).
        notext (bool): If True, displays the full JSON response instead of only AI-generated text.
        reasoning (bool): If True, displays AI reasoning (if available) alongside the response.
        history (bool): If False, clears the conversation history before sending the message.
        log (bool): Enable logging for debugging and informational messages.
        filename (str or None): The filename to save the response as a JSON file; if None, the response is not saved.
    """
    global filename, notext, reasoning
    filename = _filename
    notext = _notext
    reasoning = _reasoning
    
    if notext and reasoning:
        logging.warning("\033[93m--reasoning will be ignored because of --notext\033[0m")
    
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
        if not close_event.wait(timeout=timeout):
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
        "--timeout", 
        type=int, 
        default=300,
        help="Max wait time for AI response (default: 300s)."
    )
    parser.add_argument(
        "--notext", 
        required=False,
        action="store_true",
        help="If set, displays the full JSON response instead of AI-generated text."
    )
    parser.add_argument(
        "--reasoning", 
        required=False,
        action="store_true",
        help="If set, displays AI reasoning (if available) alongside the response."
    )
    parser.add_argument(
        "--history", 
        required=False,
        action="store_true",
        help="If set, maintains the chat history."
    )
    parser.add_argument(
        "--filename", 
        type=str, 
        help="Filename to save the response as a JSON file (if not specified, no file is saved)"
    )
    parser.add_argument(
        "--log", 
        required=False,
        action="store_true",
        help="Enable logging for debugging and informational messages."
    )
    args = parser.parse_args()
    
    if args.log:
        logging.basicConfig(level=logging.INFO)
    
    # Pass the specified arguments to main()
    main(
        message=args.message, 
        user_id=args.user_id, 
        auth_key=args.auth_key, 
        base_url=args.base_url, 
        port=args.port,
        timeout=args.timeout,
        _notext=args.notext,
        _reasoning=args.reasoning,
        history=args.history,
        _filename=args.filename
    )