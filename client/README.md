# REST to WebSocket client  

_The [`client.py`](client.py) file contains a simple script that connects to the REST-to-WebSocket WebApp and receives and processes forwarded commands from the CS and EV APIs._

## Running the script

To run the script, run the following command from the root directory of the project:

```bash
python3 client.py ws://127.0.0.1:8000/ws your_token_here
```

The script takes two arguments:
- The WebSocket URI
- The token

## Used libraries

The script uses the `asyncio` library to run in an asynchronous loop.

```python
import asyncio
```

Because the script uses is started with command line arguments, the `argparse` library is used to parse these arguments.

```python
import argparse
```

The script is also going to use the `APIHandler` and `CommandHandler` classes, which are defined in the [`api_handler.py`](api_handler.md) and [`command_handler.py`](command_handler.md) files.

```python
from octt_api_handler import OCTTAPIHandler
from command_handler import CommandHandler
```

## Using the command handlers

In order to be able to create a command handler for the REST-to-WebSocket WebApp, an instance of the `CommandHandler` class must be created with the API name as the argument.

```python
api_handler = APIHandler("octoprintapi")
```

The `CommandHandler` instance then is used to register a handler for each command that needs to be handled. These handler is defined using decorator functions as given below for the `startprint` command.

```python
@octo_print_handler.startprint
def start_print_handler(filename, temperature, bedtemperature, layerheight, printspeed):
    print(f"Received CS start print command: filename={filename}, temperature={temperature}, bedtemperature={bedtemperature}, layerheight={layerheight}, printspeed={printspeed}")
```

## Using the message handler

After the command handlers have been defined, the message handler must be defined. This message handler is used to parse the incoming messages and call the appropriate command handler.

```python
def message_handler(message)
```

The message is then parsed to extract the API, command name and parameters.

```python
api = message['api']
command = message['command']
parameters = message['parameters']
```

The command handler is then called with the command name and parameters.

```python
if api == "octoprintapi":
    octo_print_handler.parse_command(command, **parameters)
else:
    print(f"Unknown API: {api}")
```

## Main function

The main function takes the `uri` and `token` as arguments.

```python
async def main(uri, token)
```

Together with the reference to the `message_handler`, the arguments are then used to create an instance of the `OCTTAPIHandler` class.

```python
api_handler = APIHandler(uri, token, message_handler)
```

Finally, the `start` method of the `APIHandler` instance is called to start the WebSocket connection.

```python
await api_handler.start()
```

## Script start

The execution of the script starts by first parsing the command line arguments.

```python
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="WebSocket Client")
    parser.add_argument("uri", type=str, help="The WebSocket server URI")
    parser.add_argument("token", type=str, help="The token for authentication")
    args = parser.parse_args()
```

Next the `main` function is called with the URI and token as arguments. This is done as an argument of the `asyncio.run` function to run the main function in an asynchronous loop. This statement is inside a `try` block to catch the `KeyboardInterrupt` exception, which is raised when the user interrupts the program (e.g. by pressing Ctrl+C), and print an appropriate termination message.

```python
    try:
        asyncio.run(main(args.uri, args.token))
    except KeyboardInterrupt:
        print("\nProgram terminated.")
```

## Installation

### Create virtual environment

```bash
python3 -m venv client_env
source client_env/bin/activate
```

### Install dependencies

To install the dependencies, run the following command:

```bash
pip install -r requirements.txt
```