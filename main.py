from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, HTTPException
from fastapi.responses import JSONResponse
from typing import Dict
import asyncio
from asyncio import Lock
import json
import logging

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(process)d] [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S %z'
)
app = FastAPI()

# WebSocket Connection Manager [doc/connection_manager.md]
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.lock = Lock()

    async def connect(self, websocket: WebSocket, token: str):
        await websocket.accept()
        async with self.lock:
            self.active_connections[token] = websocket
            logging.info(f"Connected to client with token: '{token}'")

    async def disconnect(self, token: str):
        async with self.lock:
            if token in self.active_connections:
                del self.active_connections[token]
                logging.info(f"Disconnected client with token: '{token}'")

    async def extract_bearer_token(self, request: Request) -> str:
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return None
        token = auth_header.split(" ")[1]
        async with self.lock:
            if token not in self.active_connections:
                return None
        return token

    async def send_message(self, token: str, message: dict):
        async with self.lock:
            connection = self.active_connections.get(token)
            if not connection:
                raise HTTPException(status_code=401, detail="Unauthorized")
            await connection.send_text(str(message))

# The connection manager is instantiated globally.
manager = ConnectionManager()

# WebSocket endpoint [./doc/websocket_endpoint.md]
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: str):
    # Check if the token is already connected
    async with manager.lock:
        if token in manager.active_connections:
            await websocket.close(code=1008, reason=f"Token {token} already connected")
            return
    await manager.connect(websocket, token)
    try:
        while True:
            try:
                # Wait for a disconnection or timeout after 30 seconds
                await asyncio.wait_for(websocket.receive(), timeout=30)
            except asyncio.TimeoutError:
                # Timeout occurred, send keep-alive message
                await websocket.send_text("keep_alive")
            except WebSocketDisconnect:
                # Client disconnected
                break
            except RuntimeError as e:
                # Handle the specific RuntimeError for disconnection
                if str(e) == 'Cannot call "receive" once a disconnect message has been received.':
                    break
                else:
                    raise
    finally:
        await manager.disconnect(token)

# Common handler for POST endpoints [./doc/post_requests_handling.md]
async def handle_post_request(request: Request, api: str, command: str):
    token = await manager.extract_bearer_token(request)
    if not token:
        return JSONResponse(status_code=401, content={"detail": "Unauthorized"})
    
    message = {"api": api, "command": command, "parameters": dict(request.query_params)}
    message = json.dumps(message)

    try:
        await manager.send_message(token, message) 
        return JSONResponse(status_code=200, content="OK")
    except HTTPException as e:
        return JSONResponse(status_code=e.status_code, content={"detail": e.detail})

# POST endpoints [./doc/post_requests_handling.md]
@app.post("/{api}/{command}")
async def post_request(request: Request, api: str, command: str):
    return await handle_post_request(request, api, command)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
