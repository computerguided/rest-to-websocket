import asyncio
import argparse
from api_handler import APIHandler
from command_handler import CommandHandler

# -----------------------------------------------------------------------------
# OctoPrint API command handlers
# -----------------------------------------------------------------------------
octo_print_handler = CommandHandler("octoprintapi", {
    "startprint": ["filename", "temperature", "bedtemperature", "layerheight", "printspeed"]
})

# -----------------------------------------------------------------------------
# Example message:
# -----------------------------------------------------------------------------
# {
#   "api": "octoprintapi",
#   "command": "startprint",
#   "parameters": 
#     {
#       "filename": "test_print.gcode",
#       "temperature": 200,
#       "bedtemperature": 60,
#       "layerHeight": 0.2,
#       "printSpeed": 100
#     }
#   }
# }
# -----------------------------------------------------------------------------

@octo_print_handler.startprint      
def start_print_handler(filename, temperature, bedtemperature, layerheight, printspeed):
    print(f"Received 'startprint' command: filename='{filename}', temperature={temperature}, bedtemperature={bedtemperature}, layerheight={layerheight}, printspeed={printspeed}")

# -----------------------------------------------------------------------------
# Message handler
# -----------------------------------------------------------------------------
def message_handler(message):

    api = message['api']
    command = message['command']
    parameters = message['parameters']

    if api == "octoprintapi":
        octo_print_handler.parse_command(command, **parameters)
    else:
        print(f"Unknown API: {api}")

# -----------------------------------------------------------------------------
# Main function
# -----------------------------------------------------------------------------
async def main(uri, token):
    api_handler = APIHandler(uri, token, message_handler)
    await api_handler.start()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="WebSocket Client")
    parser.add_argument("uri", type=str, help="The WebSocket server URI")
    parser.add_argument("token", type=str, help="The token for authentication")
    args = parser.parse_args()

    try:
        asyncio.run(main(args.uri, args.token))
    except KeyboardInterrupt:
        print("\nProgram terminated.")


