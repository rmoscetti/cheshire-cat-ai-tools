"""
Client Cat that allows to send messages thanks to proper handling of the websockets
"""
from typing import Optional
from cheshire_cat_api.config import Config
from cheshire_cat_api import CatClient
import time
from queue import Queue
import json

class SuperCatClient:
    """
    A Wrapper around the official client for sane handling of the websockets connections

    Uses a queue to communite with the websocket thread and blocks until a response is received.
    This is needed as there is a bug in the cat that results in tools not being executed if we make a simple POST request
    """
    
    def __init__(self, config: Optional[Config] = None):
        self.cat_client = CatClient(config, on_message=self.on_message)
        self.cat_client.connect_ws()
        self.wait_for_connection()
        self.queue = Queue()


    def on_message(self, message):
        # this run on the websocket thread
        try:
            message = json.loads(message)
            if message.get('type') == 'chat_token':
                return
            self.queue.put(message)

        except json.JSONDecodeError as e:
            print(f"Failed to decode message: {e}")

    def wait_for_connection(self, timeout=10):
        start_time = time.time()
        while not self.cat_client.is_ws_connected:
            time.sleep(1)
            if time.time() - start_time > timeout:
                raise TimeoutError(f"Failed to connect to WebSocket within timeout ({timeout} sec).")

    def send(self, message):
        self.cat_client.send(message)
        return self.queue.get(10)


    def __getattr__(self, name):
        # forward all the other calls to the official client
        if hasattr(self, "cat_client"):
            return getattr(self.cat_client, name)
        
    def close(self):
        self.cat_client.close()
    
    def __del__(self):
        self.cat_client.close()
    
    def __enter__(self):
        """Enter the runtime context related to this object."""
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Exit the runtime context and clean up resources."""
        self.close()

