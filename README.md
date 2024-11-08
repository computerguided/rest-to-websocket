# REST to WebSocket Web App

_The REST-to-WebSocket WebApp is a Python application that converts REST API commands into WebSocket messages and forwards them to a connected WebSocket client._

## Architecture

In the architecture the following components are defined.

| Component | Description |
| --- | --- |
| Local application | The local application controlled and configured by the user. It acts as a WebSocket client and connects to the REST-to-WebSocket WebApp . |
| REST-to-WebSocket WebApp | A web application that converts REST API commands into WebSocket messages and forwards them to the connected WebSocket client. |
| External application | An external application, such as one running on a server, that sends POST requests to the REST-to-WebSocket WebApp and is configured by the user. |
| User | The user who configures the external application and controls the local application. |

The component diagram is shown below.

![rest_to_websocket_web_app](https://www.plantuml.com/plantuml/png/PK-zJiCm4DxlAOxiAJCIe7Oe0ea1qI2MBeTpRQqujcLV10NnxZWcCP784D_FTz_FEWe56Ne39zqoHk70JiwU8NRQUWhKetAzTvQjxEHi60Ch8NiqIqZB1ngCDFmX6wEFjazeLEd70HQmBq1y68S7Kdpd4gF-PBp1A_W6kD1McI6Pk7QHBbkEdJW_lxS0UZx4TtxRETMn84MiNkUkMa1E8ZvlxvlcgG8efj4uHMRZVxUFOxEtvBtHYaGxMnLerg49-BpTDIXkRujQBXFFyY35vs39v9DjRlxHan8NS8WSCkeb5SbVSLN_fODIOJrv0PWyrJaXv9XrqLtmh5PP0-PL6OpVccqxzEO7)

## Problem description

The architecture is designed to address the following problem:

Some online applications can be used to control a local application or device. For example, [OctoPrint](https://octoprint.org/) can be used to control a 3D printer.

To achieve this, the local application must provide an HTTP endpoint using a REST API with the following structure:

- `https://<base-url>/<api>/<command>?<parameters>`

Where `<base-url>` is the base URL of the local application, `<api>` is the API to use, and `<command>` is the command to execute.

The `<parameters>` are optional and are formatted as key-value pairs, separated by `&`. For example:

- `https://<base-url>/<api>/<command>?param1=value1&param2=value2`

This means that the `base-url` must be accessible from the outside, such as through a fixed IP address.

For authentication, a bearer token is used. This token is configured in the external application and added to the HTTP POST request as a unique bearer token in the "Authorization" header.

There are two key challenges with this approach:

- Obtaining an IP address that is externally accessible can be challenging in an office IT infrastructure.

- Each local application has a different IP address, requiring constant updates to the external application configuration.

## Solution

To address these challenges, an [Azure Web App](https://azure.microsoft.com/en-us/products/app-service/web) is deployed with a URL such as:

`rest-to-websocket.azurewebsites.net`

Deploying an Azure Web App provides a reliable, publicly accessible endpoint with a stable URL, eliminating the need for fixed external IP addresses in the local infrastructure.

Here’s how this approach addresses each challenge:

- **External Accessibility**: With an Azure WebApp, you have a publicly accessible endpoint that doesn’t rely on office infrastructure, making it accessible from anywhere.
- **Consistency Across Test Systems**: You can deploy a single, stable URL for all test systems, simplifying configuration management by avoiding the need to update IP addresses for each system.

The REST-to-WebSocket WebApp converts HTTP POST commands into JSON messages, which are then forwarded to the connected local application over the WebSocket.

Note that the Azure WebApp is optional if a dedicated, publicly accessible local web server can be set up to host REST-to-WebSocket.

## Conversion Format

The HTTP POST request is converted to the following JSON format and then sent as a string to the connected WebSocket client:

```json
{
    "source": "<api>",
    "command": "<command>",
    "parameters": [ {"<param1>": "<value1>"}, {"<param2>": "<value2>"} ]
}
```

Where `<api>` is the API on which the command was received, `<command>` is the command to execute and `<parameters>` are the parameters of the command. The JSON schema is given below.

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "api": {
      "type": "string",
      "description": "The API on which the command was received."
    },
    "command": {
      "type": "string",
      "description": "The command to execute."
    },
    "parameters": {
      "type": "object",
      "description": "An object containing key-value pairs as parameters for the command.",
      "additionalProperties": {
        "oneOf": [
          {
            "type": "string"
          },
          {
            "type": "number"
          },
          {
            "type": "boolean"
          }
        ]
      }
    }
  },
  "required": ["api", "command", "parameters"],
  "additionalProperties": false
}
```

An example is shown below (note all the names are small caps):

```json
{
  "api": "octoprintapi",
  "command": "startprint",
  "parameters":
   {
      "filename": "test_print.gcode",
      "temperature": 200,
      "bedtemperature": 60,
      "layerheight": 0.2,
      "printspeed": 100
    }
}
```

## Multiplicity

The REST-to-WebSocket WebApp must allow multiple local applications to connect simultaneously. To distinguish between connected clients and add a layer of security, the same bearer token configured in the local application is used during connection.

The bearer token is included when connecting, resulting in the following client URL:

`wss://rest-to-websocket.azurewebsites.net/ws?token=<bearer_token>`

## Installation

To install the app locally, e.g. for testing purposes, the following steps can be followed:

### 1. Clone the repository

```bash
git clone https://github.com/computerguided/rest-to-websocket.git
```

### 2. Install python3.10-venv

To be able to create the virtual environment, python3.10-venv needs to be installed if not already available.

```bash
sudo apt install python3.10-venv
```

### 3. Create the virtual environment

For convenience, a virtual environment is created because it allows for the dependencies to be installed in an isolated environment. This is optional, but recommended and common practice.

```bash
python3 -m venv rest_to_websocket_env
source rest_to_websocket_env/bin/activate
```

This will create a directory `rest_to_websocket_env` in the current directory. In the `.gitignore` file, `*env/` directories are already added to avoid committing it.

### 4. Install the dependencies

```bash
pip install -r requirements.txt
```

This installs the dependencies defined in the `requirements.txt` file. These are the key dependencies:

- `fastapi`: The main framework.
- `uvicorn`: ASGI server used for running FastAPI applications.
- `gunicorn`: HTTP server for UNIX to run the app, which is required for Azure WebApp deployment.
- `jinja2`: Template engine for Python.
- `python-multipart`: Multipart/form-data parsing for Python.
- `requests`: HTTP library for Python.
- `websockets`: WebSocket library for Python.

### 5. Start the WebApp

To start the REST-to-WebSocket WebApp, the following command can be used:

```bash
gunicorn -w 1 -k uvicorn.workers.UvicornWorker main:app
```
When running the command locally, the console will show something like the following:

```
[2024-11-04 13:31:24 +0100] [28607] [INFO] Starting gunicorn 23.0.0
[2024-11-04 13:31:24 +0100] [28607] [INFO] Listening at: http://127.0.0.1:8000 (28607)
[2024-11-04 13:31:24 +0100] [28607] [INFO] Using worker: uvicorn.workers.UvicornWorker
[2024-11-04 13:31:24 +0100] [28608] [INFO] Booting worker with pid: 28608
[2024-11-04 13:31:25 +0100] [28608] [INFO] Started server process [28608]
[2024-11-04 13:31:25 +0100] [28608] [INFO] Waiting for application startup.
[2024-11-04 13:31:25 +0100] [28608] [INFO] Application startup complete.
```

If the REST to WebSocket WebApp is running locally, it will be available at `http://127.0.0.1:8000`.

In the following sections the start command is explained in more detail.

## Explanation of Start Command

The application is started using the following command:

```bash
gunicorn -w 1 -k uvicorn.workers.UvicornWorker main:app
```

This command runs a [FastAPI](https://fastapi.tiangolo.com/) application using [Gunicorn](https://gunicorn.org/) with [Uvicorn](https://www.uvicorn.org/) as the worker class.

The following is a breakdown of the command:

- **`gunicorn`**: Gunicorn (Green Unicorn) is a [Python WSGI HTTP Server](#what-is-a-wsgi-http-server) for running Python web applications. It's used for serving web applications in production.

- **`-w 1`**: This option specifies the number of worker processes. Here, `-w 1` means you're running only 1 worker process. Workers handle the actual web requests, and increasing the number of workers allows the server to handle more requests simultaneously. For FastAPI applications, it’s common to start with one worker and scale as needed.

- **`-k uvicorn.workers.UvicornWorker`**: The `-k` option defines the type of worker class Gunicorn should use. In this case, `uvicorn.workers.UvicornWorker` (case sensitive!) tells Gunicorn to use Uvicorn (ASGI server) as the worker. Uvicorn is used because FastAPI is an ASGI-based framework, which allows for asynchronous communication, unlike the traditional WSGI used by most web frameworks.

- **`main:app`**: This part specifies the application module and the ASGI app object that Uvicorn should serve.

- **`main`**: This refers to the Python file where your FastAPI app is defined. For example, if your FastAPI app is defined in `main.py`, this points to that file.

- **`app`**: This refers to the FastAPI application object. Inside `main.py`, the application object is defined as `app = FastAPI()`.

In summary, this command tells Gunicorn to start a server with 1 worker, using Uvicorn as the worker class, and to serve the FastAPI application located in the `main` module with the object `app`.

### What is a WSGI HTTP Server?

A **WSGI (Web Server Gateway Interface) HTTP Server** is a type of server used to handle HTTP requests and run web applications written in Python, following the WSGI specification. It acts as an intermediary between the web server (e.g., Nginx or Apache) and the Python web application, enabling them to communicate with each other.

#### Key Concepts:

1. **WSGI (Web Server Gateway Interface):**
   - WSGI is a specification for how web servers and Python web applications should interact. It defines a simple interface that web servers use to forward requests to a Python application and receive responses back.
   - The purpose of WSGI is to ensure that web applications and frameworks in Python can be compatible with different web servers.
   - A WSGI-compatible web server runs the application, processes incoming HTTP requests, and sends the response back to the client.<br><br>

2. **WSGI HTTP Server:**
   - A WSGI HTTP server implements this interface and handles requests by passing them to the WSGI-compliant Python application.
   - The server waits for HTTP requests, processes them, and forwards them to the application for handling. After processing, the application sends a response, which the server sends back to the client (e.g., a browser).
   - Popular examples of WSGI servers are **Gunicorn**, **uWSGI**, **Waitress**, and **mod_wsgi**.<br><br>

3. **How It Works:**
   - A WSGI server, like Gunicorn or uWSGI, listens for incoming HTTP requests.
   - It takes each request, wraps it in an environment (headers, method, path, etc.), and passes it to the Python application (using the WSGI interface).
   - The application processes the request (generating a response, interacting with databases, etc.) and returns the response (status code, headers, and body) to the server.
   - The WSGI server sends the response back to the client.

#### Why WSGI?
Before WSGI, web servers and Python applications interacted using non-standardized protocols, leading to compatibility issues. WSGI standardizes this interaction, ensuring that any WSGI-compliant Python application can run on any WSGI-compatible server.

### Example of WSGI in Action
A Flask application is an example of a WSGI application. When you deploy a Flask app using a WSGI HTTP server like Gunicorn, the server acts as the middleman between the web server (like Nginx) and your application, allowing the app to serve HTTP requests efficiently.

### Modern Considerations:
While WSGI is great for synchronous applications, it doesn't natively support asynchronous features. For modern asynchronous frameworks like **FastAPI**, which use **ASGI (Asynchronous Server Gateway Interface)**, you would use servers like **Uvicorn** instead of traditional WSGI servers.

In summary, a **WSGI HTTP Server** is a Python web server designed to run WSGI-compliant web applications, providing a standard interface for handling HTTP requests and responses.