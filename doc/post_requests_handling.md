# POST requests handling

## POST request structure

As an example, consider the following command which sends the `ready` parameter to the `state` endpoint with a bearer token "bearer_token_123":

```bash
curl -X 'POST' \
  'http://example-url.com/ev_api/state?ready=true' \
  -H 'accept: */*' \
  -H 'Authorization: Bearer bearer_token_123' \
  -d ''
```

The following sections describe how the request is handled in the server.

## POST endpoints

The POST endpoint is defined in the FastAPI application.

```python 
@app.post("/{api}/{command}")
async def post_request(request: Request, api: str, command: str):
    return handle_post_request(request, api, command)
```

The `handle_post_request()` function is called with the `request`, the `api` and the `command` as arguments. This function is described in the next section.

## Common POST request handler

To handle POST requests both from the “cs_api” and “ev_api” endpoints, a common handler is created that takes the request and the source.

```python
async def handle_post_request(request: Request, api: str, command: str)
```

The first step is to retrieve the token from the request by calling the [`extract_bearer_token()`](./connection_manager.md#extract-bearer-token) method of the [connection manager](./connection_manager.md).

```python
token = manager.extract_bearer_token(request)
```

If the token was not found, or if there is no active connection associated with the request, the response code 401 must be returned as defined.

```python
if not token or token not in manager.active_connections:
    return JSONResponse(status_code=401, content={"detail": "Unauthorized"})
```

If all is well, the parameters can be retrieved of the request and placed together with the command in a data dictionary.

```python
data = { "command": command, "parameters": dict(request.query_params) } 
```

The result is then placed in a JSON string which also contains the source in order for the WebSocket client to know which endpoint was used.

```python
message = {"source": source, "data": data}
message = json.dumps(message)
```

To send the message, the [`send_message()`](./connection_manager.md#sending-messages) method of the connection manager is called. This method will raise an HTTPException in case there is something wrong. If the message was sent correctly, the response code 200 will be returned.

```python
try:
    await manager.send_message(token, message)
    return JSONResponse(status_code=200, content="OK")
except HTTPException as e:
    return JSONResponse(status_code=e.status_code, content={"detail": e.detail})
```
