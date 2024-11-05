# WebSocket endpoint

The `@app.websocket("/ws")` registers `websocket_endpoint()` as a handler for WebSocket connections to `/ws`.

```python
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: str)
```

This method is called when a new WebSocket connection is established. To add the connection to the list of active connections, the [`connect()`](./connection_manager.md#connect) method of the connection manager is called.

```python
await manager.connect(websocket, token)
```

If the WebSocket connection is closed, the WebSocketDisconnect exception is raised

```python
try:
    while True:
        await asyncio.sleep(30)
        await websocket.send_text("keep_alive")
except WebSocketDisconnect:
    manager.disconnect(token)
```

To keep the connection open, regular messages need to be sent. This is achieved by using an asynchronous timer and sending a “keep_alive” message. The WebSocket client does not need to respond to this message as the underlying networking layers already acknowledge the reception of the message.

In the `websocket_endpoint()` function, the token is retrieved as a URL parameter. This means that the client connecting to the WebSocket needs to include the token in the URL when initiating the connection.

For example, the client would connect to the WebSocket endpoint like this:

`wss://<server_address>/ws?token=your_token_here`

FastAPI automatically extracts the token parameter from the URL and passes it as an argument to the `websocket_endpoint()` function. In this case, token is a query parameter specified in the WebSocket URL.
