class CommandHandler:
    def __init__(self, api_name, commands):
        self.api_name = api_name
        self.handlers = {}
        self.commands = commands

        for command in self.commands:
            # Dynamically create a decorator method for each command
            setattr(self, command, self._create_decorator(command))

    def _create_decorator(self, command_name):
        """Return a decorator that registers a handler for the given command."""

        def decorator(func):
            self.handlers[command_name] = func
            return func
        return decorator

    def handle_command(self, command, **kwargs):
        """Invoke the handler for the given command."""

        handler = self.handlers.get(command)
        if handler:
            return handler(**kwargs)
        print(f"Warning: No handler found for '{self.api_name}' command '{command}'")
    
    def parse_command(self, command, **parameters):
        """Parse the incoming data and handle the command."""

        valid_params = {key: parameters[key] for key in self.commands[command] if key in parameters}
        return self.handle_command(command, **valid_params)
