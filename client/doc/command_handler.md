# Command Handler

_The `CommandHandler` class is used to handle the commands from the WebApp to the CS and EV side._

## Description

The `CommandHandler` class is used to handle the commands from the WebApp to the CS or EV side and is instantiated with the name of the API, for example `cs_api` or `ev_api`.

```python
cs_handler = CommandHandler('cs_api')
ev_handler = CommandHandler('ev_api')
```

After instantiation, for each command, a decorator can be created for the instance which registers a handler for the command. The following example shows the `plugin` command for the CS API.

```python
@cs_handler.plugin      
def plugin_handler(halfway, evse_id, connector_id):
    print(f"Received plugin message: {halfway}, {evse_id}, {connector_id}")
```

As such there is a handler for each command (see [`octt_cs_api.md`](octt_cs_api.md) for more details):

```python
cs_handler.plugout
cs_handler.plugin
cs_handler.authorize
cs_handler.reboot
cs_handler.state
cs_handler.parkingbay
```

Similarly for the EV API (see [`octt_ev_api.md`](octt_ev_api.md) for more details):

```python
ev_handler.end
ev_handler.plugin
ev_handler.plugout
ev_handler.state
```

**The user of the `CommandHandler` class must call the [`parse_command`](#parse-command) method for each command.**

It works together with the [`octt_api_handler.py`](../octt_api_handler.py) file which is used to actually receive the commands from the CS or EV side to the WebApp. As illustrated in the following code snippet:

```python
def message_handler(message):

    source = message['source']
    data = message['data']

    if source == "cs_api":
        cs_handler.parse_command(data)
    elif source == "ev_api":
        ev_handler.parse_command(data)
```

As described in the [`octt_api_handler.md`](octt_api_handler.md) file, the `message_handler` function is passed to the `OCTTAPIHandler` class.

Although the functionality could be integrated in one class, splitting the reception and handling of the commands in this way allows for more flexibility, for example when some logging is required or additional checks are needed.

## Class Definition

The `CommandHandler` class is defined in the [`command_handler.py`](../command_handler.py) file. It is initialized with the name of the API.

```python
class CommandHandler:
    def __init__(self, api_name):
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
self.commands = self._get_commands(api_name)
```

The [`_get_commands` method](#get-commands) is used to get the commands for the API.

To create the decorators for the commands, the [`_create_decorator` method](#create-decorator) is called for each command.

```python
for command, params in self.commands.items():
    setattr(self, command, self._create_decorator(command, params))
```

## Get Commands

To get the commands for a specific API, the `_get_commands` method is called.

```python
def _get_commands(self, api_name)
```

If the API is `cs_api`, the following commands are available:

```python
cs_commands = {
    'plugin': ['halfway', 'evse_id', 'connector_id'],
    'plugout': ['evse_id'],
    'authorize': ['id', 'type', 'evse_id', 'connector_id'],
    'reboot': [],
    'state': ['faulted', 'unlock_failed', 'refused_local_auth_list', 'evse_id', 'connector_id'],
    'parkingbay': []
}
```

If the API is `ev_api`, the following commands are available:

```python
ev_commands = {
    'plugin': [],
    'plugout': [],
    'end': [],
    'state': ['ready']
}
```

When the API name is not known, an error is raised.

```python
raise ValueError(f"Unknown API name: {self.api_name}")
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
return self.handle_command(command, **valid_params)
```

Note that the `handle_command` method is not a method of the `CommandHandler` class but a method of the `CommandHandler` instance as specified in ["Description"](#description).

## Handle Command

To handle a command, the `handle_command` method is called.

```python
def handle_command(self, command, **kwargs):
```

As an example, the following CS command is handled:

```python
# Example CS command
cs_handler.handle_command('plugin', halfway=False, evse_id='1', connector_id='1')

# Example EV command
ev_handler.handle_command('state', ready=True)
```

First the `handler` needs to be found in the `handlers` dictionary.

```python
handler = self.handlers.get(command)
```

If no handler is found, an error is raised and the function exits.

```python
if not handler:
    raise ValueError(f"No handler found for command '{command}'")
```

When the handler is found, it is called with the provided parameters.

```python
return handler(**kwargs)
```
