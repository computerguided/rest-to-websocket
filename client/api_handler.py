import websockets
import json

class APIHandler:
    def __init__(self, uri, token, message_handler):
        self.uri = uri
        self.token = token
        self.message_handler = message_handler

        # Check if message_handler is callable
        if not callable(self.message_handler):
            raise Exception("Message handler is not callable")
    
    async def start(self):
        uri = f"{self.uri}?token={self.token}"
        try:
            async with websockets.connect(uri) as websocket:
                print(f"Connected to server with token: {self.token}")
                while True:
                    message = await websocket.recv()
                    if message == "keep_alive":
                        continue
                    message = json.loads(message)
                    self.message_handler(message)
        except websockets.InvalidStatusCode as e:
            print(f"Connection rejected with status code: {e.status_code}")
        except websockets.ConnectionClosed as e:
            print(f"Connection closed: {e}")
