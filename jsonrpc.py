import requests
import json
from tabulate import tabulate

# Use the JSON-RPC endpoint.
# Adjust the scheme (http or https) depending on your XO configuration.
JSON_RPC_URL = "https://xo-cslab.dei.uc.pt/jsonrpc"

# Your credentials
USERNAME = "cslab"
PASSWORD = "cslabctf2024"

def rpc_call(method, params, rpc_id, headers=None):
    payload = {
        "jsonrpc": "2.0",
        "method": method,
        "params": params,
        "id": rpc_id
    }
    data = json.dumps(payload)
    response = requests.post(JSON_RPC_URL, data=data, headers=headers)
    print(f"Response for {method}:", response.text)
    try:
        result = response.json()
    except ValueError as e:
        raise Exception(f"Invalid JSON response: {e}")
    if "error" in result:
        raise Exception(f"Error calling {method}: {result['error']}")
    return result["result"]

def login():
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    # Call the JSON-RPC login method.
    token = rpc_call("session.login_with_password", {"username": USERNAME, "password": PASSWORD}, rpc_id=1, headers=headers)
    return token

def get_vms(auth_token):
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        # Send the auth token as a cookie.
        "Cookie": f"authenticationToken={auth_token}"
    }
    # Call vm.getAll to retrieve the list of VMs (using rpc_id 2 as an example).
    vms = rpc_call("vm.getAll", {}, rpc_id=2, headers=headers)
    return vms

def show_vms(vms):
    table_data = []
    if isinstance(vms, list):
        for vm in vms:
            vm_uuid = vm.get("uuid", "N/A")
            name = vm.get("name_label", "N/A")
            description = vm.get("name_description", "N/A")
            table_data.append([vm_uuid, name, description])
    else:
        print("Unexpected VM data structure:", vms)
        return

    if table_data:
        print(tabulate(table_data, headers=["VM UUID", "Name", "Description"], tablefmt="pretty"))
    else:
        print("No VMs found.")

if __name__ == "__main__":
    try:
        # Log in and get a session token.
        token = login()
        print("Login successful. Token:", token)
        # Use the token to retrieve the VMs.
        vms = get_vms(token)
        print("\nExisting VMs:")
        show_vms(vms)
    except Exception as e:
        print("Error:", e)
