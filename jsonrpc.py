import json
import websocket

USERNAME = "cslab"
PASSWORD = "cslabctf2024"

ws_instance = None

def send_rpc(method, params, rpc_id):
    payload = {
        "jsonrpc": "2.0",
        "method": method,
        "params": params,
        "id": rpc_id
    }
    message = json.dumps(payload)
    print("Sending:", message)
    ws_instance.send(message)

def on_message(ws, message):
    print("Received:", message)
    try:
        response = json.loads(message)
    except Exception as e:
        print("Error parsing JSON:", e)
        return

    rpc_id = response.get("id")
    if rpc_id == 1:
        token = response.get("result")
        if token:
            print("Login successful, token:", token)
            # Now request the list of VMs.
            send_rpc("vm.getAll", {}, 2)
        else:
            print("Login failed, response:", response)
    elif rpc_id == 2:
        vms = response.get("result")
        print("\nList of VMs:")
        if isinstance(vms, list):
            for vm in vms:
                vm_uuid = vm.get("uuid", "N/A")
                name = vm.get("name_label", "N/A")
                description = vm.get("name_description", "N/A")
                print(f"VM UUID: {vm_uuid}\nName: {name}\nDescription: {description}\n")
        else:
            print("Unexpected VM data structure:", vms)
    else:
        print("Other response:", response)

def on_error(ws, error):
    print("Error:", error)

def on_close(ws, close_status_code, close_msg):
    print("### WebSocket closed ###")

def on_open(ws):
    print("WebSocket connection opened.")
    # Send the login request.
    send_rpc("session.login_with_password", {"username": USERNAME, "password": PASSWORD}, 1)

if __name__ == "__main__":
    # Optionally enable trace for debugging.
    try:
        websocket.enableTrace(True)
    except AttributeError:
        print("Trace not available; ensure 'websocket-client' is installed.")

    # Try the endpoint as suggested by the tutorial.
    # If wss://xo-cslab.dei.uc.pt/jsonrpc fails (connection refused),
    # try the socket.io endpoint.
    WS_URL = "wss://xo-cslab.dei.uc.pt/socket.io/?EIO=3&transport=websocket"
    ws_instance = websocket.WebSocketApp(WS_URL,
                                          on_open=on_open,
                                          on_message=on_message,
                                          on_error=on_error,
                                          on_close=on_close)
    ws_instance.run_forever()
