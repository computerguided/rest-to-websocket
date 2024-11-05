# API Handler

_The `API Handler` is responsible for handling the connection to the REST-to-WebSocket WebApp via a WebSocket and receiving the command string. It is implemented in the `api_handler.py` file._

## Descripton

The `API Handler` can be used by the client application to create the connection to the REST-to-WebSocket WebApp via a WebSocket.

It is instantiated with the token and the WebSocket URI which is the address of the WebApp, for example:

`wss://<server_address>/ws`

It also takes a message handler function which is called when a message is received from the WebSocket. This function is defined by the user.

```python
self.api_handler = APIHandler(uri, token, message_handler)
```

After instantiation, the user needs to call the `start()` method to actually have the instantiated `API Handler` establish the connection to the WebSocket and start receiving messages.

```python
self.api_handler.start()
```

## Class Definition

The class is defined in the [`api_handler.py`](../api_handler.py) file.

```python
class APIHandler:
```

The class has the following attributes:

| Attribute | Type | Description |
| --- | --- | --- |
| `uri` | `str` | The WebSocket URI. |
| `token` | `str` | The token for authentication. |
| `message_handler` | `function` | The function to be called when a message is received from the WebSocket. |

In the constructor these attributes are set.

```python
self.uri = uri
self.token = token
self.message_handler = message_handler
```

For safety reasons, the `message_handler` is checked if it is callable.

```python
if not callable(self.message_handler):
    raise Exception("Message handler is not callable")
```

## Start

The `start()` method establishes the connection to the WebSocket and starts receiving messages.

```python
async def start(self):
```

The first step is to create the URI with the token, for example:

`wss://<server_address>/ws?token=<token>`

Then, the connection is established using the `websockets` library. This is done using an asynchronous context manager.

```python
async with websockets.connect(uri) as websocket:
```

This is a construct in Python that allows for asynchronous context management. Let me break it down step by step:

- `async with`: This statement is used to manage asynchronous context in Python. It works similarly to a regular `with` statement, which ensures that certain operations are performed automatically before and after the block of code. Specifically, it is used for setting up and then safely tearing down asynchronous resources (like network connections).

- `websockets.connect(uri)`: This is a coroutine from the `websockets` library that establishes a WebSocket connection to the given uri. It is like opening a socket to communicate with a server.

- `as websocket`: The `as` keyword assigns the resulting connection object from `websockets.connect(uri)` to the variable `websocket`. You can then use this `websocket` object to send and receive data.

Using `async with` ensures that once the code inside the block completes (or if an error occurs), the WebSocket connection is automatically closed properly, even if there are exceptions. It’s a convenient way to avoid resource leaks by making sure that any setup and teardown is handled for you.

After the connection is established, an endless loop is started to receive messages from the WebSocket.

```python
while True:
    message = await websocket.recv()
```

The `recv()` method is used to receive a message from the WebSocket.

The first step is to check if the message is a "keep_alive" message. If it is, the loop continues with the next iteration.

```python
if message == "keep_alive": continue
```

Otherwise, the message is converted from JSON to a Python dictionary.

```python
message = json.loads(message)
```

Next the message is passed to the `message_handler()` function as was defined during the instantiation of the `APIHandler` class.

```python
self.message_handler(message)
```
To handle the situation in which the connection is rejected, the code is enclosed in a try-except block.

```python
except websockets.InvalidStatusCode as e:
    print(f"Connection rejected with status code: {e.status_code}")
```

To handle the situation when the connection is closed, the code is enclosed in a try-except block.

```python
except websockets.ConnectionClosed as e:
    print(f"Connection closed: {e}")
```
