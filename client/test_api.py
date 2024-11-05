import requests
import argparse

def send_post_request(url, token, data):
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    response = requests.post(url, json=data, headers=headers, params=data)
    return response

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Send POST requests to different endpoints.")
    parser.add_argument("base_url", type=str, help="Base URL of the server")
    parser.add_argument("token", type=str, help="Bearer token for authorization")
    args = parser.parse_args()

    base_url = args.base_url
    token = args.token

    # Test POST request to octoprintapi endpoint
    octo_print_api_url = f"{base_url}/octoprintapi/startprint"
    octo_print_api_data = {
        "filename": "test_print.gcode",
        "temperature": 200,
        "bedtemperature": 60,
        "layerheight": 0.2,
        "printspeed": 100
    }

    response = send_post_request(octo_print_api_url, token, octo_print_api_data)
    print(f"Response from OctoPrintAPI: {response.status_code}, {response.text}")