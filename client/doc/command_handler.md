# Command Handler

_The `CommandHandler` class is used to handle the commands from the REST-to-WebSocket API to the WebApp._

## Description

The `CommandHandler` class is used to handle the commands from the REST-to-WebSocket API to the WebApp.

The class is instantiated with the name of the API and the commands for the API.

```python   
handler = CommandHandler(api_name, commands)
```

After instantiation, for each command, a decorator can be created for the instance which registers a handler for the command. The following example shows the `startprint` command for the OctoPrint API.

```python
@octo_print_handler.startprint      
def startprint_handler(filename, temperature, bedtemperature, layerheight, printspeed):
    print(f"Received startprint message: '{filename}', {temperature}, {bedtemperature}, {layerheight}, {printspeed}")
```

**The user of the `CommandHandler` class must call the [`parse_command`](#parse-command) method for each command.**

It works together with the [`api_handler.py`](../api_handler.py) file which is used to actually receive the commands from the REST-to-WebSocket API to the WebApp. As illustrated in the following code snippet:

```python
def message_handler(message):

    api = message['api']
    command = message['command']
    parameters = message['parameters']

    octo_print_handler.parse_command(command, **parameters)
```

Although the functionality could be integrated in one class, splitting the reception and handling of the commands in this way allows for more flexibility, for example when some logging is required or additional checks are needed.

## Class Definition

The `CommandHandler` class is defined in the [`command_handler.py`](../command_handler.py) file. It is initialized with the name of the API.

```python
class CommandHandler:
    def __init__(self, api_name, commands):
```

The class has the following attributes:

| Attribute | Type | Description |
| --- | --- | --- |
| `api_name` | `str` | The name of the API. |
| `handlers` | `dict` | A dictionary that maps the command name to the handler function. |
| `commands` | `dict` | The commands for the API. |

These attributes are initialized in the `__init__` method.

```python
self.api_name = api_name
self.handlers = {}
self.commands = commands
```

To create the decorators for the commands, the [`_create_decorator` method](#create-decorator) is called for each command.

```python
for command, params in self.commands.items():
    setattr(self, command, self._create_decorator(command, params))
```

## Create Decorator

To create a decorator for a command, the `_create_decorator` method is called.

```python
def _create_decorator(self, command_name, params)
```

The function returns a decorator that registers a handler for the given command. This decorator function is defined inside the `_create_decorator` method.

```python
def decorator(func):
    self.handlers[command_name] = func
    return func
return decorator
```

## Parsing the commands

The incoming data containing the command and its parameters are parsed in the `parse_command` method. This is the method that must be called by the user of the `CommandHandler` class.

```python
def parse_command(self, data):
```

Note that there will be a `CommandHandler` instance for each API, so no need to specify which API is used.

The `data` is expected to have a `command` key with the name of the command and a `parameters` key with the parameters for the command. To ensure that the `data` contains the required keys and that the handling of the command is successful, parsing is enclosed in a try-except block.


```python
try:
    command = data['command']
    parameters = data['parameters']
except KeyError as e:
    raise ValueError(f"Missing key in JSON data: {e}")
```

Next, the parameters are filtered to only include those that are expected for the command.

```python
valid_params = {key: parameters[key] for key in self.commands[command] if key in parameters}
```

After this, the command is handled by calling the [`handle_command` method](#handle-command) with the valid parameters unpacking the dictionary by using `**`.

```python
return self.handle_command(command, **parameters)
```

Note that the `handle_command` method is not a method of the `CommandHandler` class but a method of the `CommandHandler` instance as specified in ["Description"](#description).

## Handle Command

To handle a command, the `handle_command` method is called.

```python
def handle_command(self, command, **kwargs):
```
