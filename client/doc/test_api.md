# Test octt

_The [`test_octt.py`](test_octt.py) file contains a simple python script that sends POST requests to the CS and EV APIs. It is used to test the CS and EV APIs._

## Run the script

To run the script, use the following command:
```bash
python3 test_octt.py http://127.0.0.1:8000 <bearer_token>
```

The script takes two arguments:
- The base URL of the server
- The bearer token

## Used libraries

In order for the script to send the POST requests, it uses the [`requests`](https://pypi.org/project/requests/) library. To parse the command line arguments, it uses the [`argparse`](https://docs.python.org/3/library/argparse.html) library.

```python
import requests
import argparse
```

## Send POST requests

To be able to send the POST requests, a `send_post_request` function is defined, taking the URL, token and data as arguments.

```python
def send_post_request(url, token, data):
```

In order to send the request, the headers are set with the token and the content type.

```python
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}
```

Then the request is sent with the `requests.post` function. This is done synchronously, so the result is stored in the `response` variable.

```python
response = requests.post(url, json=data, headers=headers, params=data)
```

Finally, the response is returned.

```python
return response
```

## Main function

In the main function, the first step is to parse the command line arguments.

```python
parser = argparse.ArgumentParser(description="Send POST requests to different endpoints.")
parser.add_argument("base_url", type=str, help="Base URL of the server")
parser.add_argument("token", type=str, help="Bearer token for authorization")
args = parser.parse_args()

base_url = args.base_url
token = args.token
ev_api_url = f"{base_url}/ev_api"
```
To send the `state` command as a POST request to the EV API, the URL is first set.

```python
ev_api_url = f"{base_url}/ev_api/state"
```

Next, the data is defined for the EV `state` command.

```python
ev_data = {
    "ready": True
}
```

With this set, the `send_post_request` function is called and the response is printed.

```python
response = send_post_request(ev_api_url, token, ev_data)
print(f"Response from ev_api: {response.status_code}, {response.text}")
```

This method is then repeated for the EV `plugin` and the CS `state` and `authorize` commands.

## Possible responses

Since the responses are stored and then printed, the following is possible.

### Success
When the command could be successfully sent, the following is printed:

```
Response from ev_api: 200, "OK"
```

### Unauthorized

If something is wrong with the token, the following can be printed:

```
Response from ev_api: 401, {"detail":"Unauthorized"}
```

Note that this is either because the token is invalid, or because the "Test System" is not running or connected to the Web App.

### Internal Server Error

Another possible error is when there is no connection to the server, i.e. the URL is not accessible, or the server is not running.

```
Response from ev_api: 500, Internal Server Error
```