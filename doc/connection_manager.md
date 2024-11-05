# WebSocket Connection Manager

_The connection manager is used to store the active WebSocket connections and to send messages to these connections._

## Class Definition

To store the active WebSocket connections, we’re defining the `ConnectionManager` class which manages a dictionary of WebSockets with the bearer token used as the key.

```python
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.lock = Lock()
```

The connection manager is instantiated  globally.

```python
manager = ConnectionManager()
```

The line `self.lock = Lock()` creates an instance of an `asyncio.Lock` in the `ConnectionManager` class. This lock is required because the `manager` is defined globally andwill be used in several threads. The lock is then used to ensure that access to the `active_connections` dictionary is thread-safe when threads need to modify or access it. By using the lock (`async` with s`elf.lock:`), only one thread can interact with `active_connections` at a time, which helps to prevent race conditions and maintain data integrity in an asynchronous environment.

The `ConnectionManager` class has the following methods:

| Method | Description |
| --- | --- |
| [`connect()`](#connect) | Adds a WebSocket to the `active_connections` dictionary. |
| [`disconnect()`](#disconnect) | Removes a WebSocket from the `active_connections` dictionary. |
| [`extract_bearer_token()`](#extract-bearer-token) | Extracts the bearer token from the HTTP POST request. |
| [`send_message()`](#sending-messages) | Sends a message to a specific WebSocket connection. |

## Connect

When a new WebSocket connection is established, the `connect()` method is called to store the connection in the `active_connections` dictionary. The access to the `active_connections` dictionary is protected by the `lock`.

```python
async def connect(self, websocket: WebSocket, token: str):
    await websocket.accept()
    async with self.lock:
        self.active_connections[token] = websocket
```

## Disconnect

When a WebSocket connection is closed, the `disconnect()` method is called to remove the connection from the `active_connections` dictionary. The access to the `active_connections` dictionary is protected by the `lock`.

```python
async def disconnect(self, token: str):
    async with self.lock:
        if token in self.active_connections:
            del self.active_connections[token]
```

## Extract Bearer Token

The `extract_bearer_token()` method extracts the bearer token from the HTTP POST request.

```python
def extract_bearer_token(self, request: Request) -> str
```

The bearer token is part of the HTTP POST request header and stored in the `Authorization` field.

```python
auth_header = request.headers.get("Authorization")
```

If the `Authorization` field is not found, or does not start with `Bearer `, the method returns `None`.

```python
if not auth_header or not auth_header.startswith("Bearer "):
    return None
```

If the `Authorization` field is found and starts with `Bearer `, the token is extracted from the field.

```python
token = auth_header.split(" ")[1]
```

With the token found, it needs to be checked if there is an active connection with the token. This means that it needs to be checked if the `active_connections` dictionary contains the token as a key. Since the access to the `active_connections` dictionary needs to be thread-safe, the `lock` is used.

```python
async with self.lock:
    if token not in self.active_connections:
        return None
```

If there is an active connection with the token, the method returns the token.

```python
return token
```

## Sending messages

To send a message to a WebSocket connection, the `send_message()` method is called.

```python
async def send_message(self, token: str, message: str)
```

The first step is to retrieve the connection, i.e. the reference to the WebSocket.

```python
async with self.lock:
    connection = self.active_connections.get(token)
```

If the token is not found, an HTTPException can be raised which is defined in the FastAPI framework.

```python
if not connection:
    raise HTTPException(status_code=401, detail="Unauthorized")
```

If the connection was found, its `send_text()` method can be called.

```python
await connection.send_text(message)
```

## 
