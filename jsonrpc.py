import requests
from tabulate import tabulate

# JSON-RPC endpoint
JSON_RPC_URL = "http://xo-cslab.dei.uc.pt/jsonrpc"

# Replace these with your actual credentials
USERNAME = "cslab"
PASSWORD = "cslabctf2024"

def rpc_call(method, params, rpc_id, headers):
    payload = {
        "jsonrpc": "2.0",
        "method": method,
        "params": params,
        "id": rpc_id
    }
    response = requests.post(JSON_RPC_URL, json=payload, headers=headers)
    # Print the raw response to help debug authentication issues.
    print(f"Response for {method}:", response.text)
    try:
        result = response.json()
    except ValueError as ve:
        raise Exception(f"Invalid JSON response: {ve}")
    if "error" in result:
        raise Exception(f"Error calling {method}: {result['error']}")
    return result["result"]

def login():
    # Build the login payload for JSON-RPC.
    payload = {
        "jsonrpc": "2.0",
        "method": "session.login_with_password",
        "params": {
            "username": USERNAME,
            "password": PASSWORD
        },
        "id": 1
    }
    headers = {"Content-Type": "application/json"}
    response = requests.post(JSON_RPC_URL, json=payload, headers=headers)
    print("Login response:", response.text)
    try:
        result = response.json()
    except ValueError as ve:
        raise Exception(f"Invalid JSON during login: {ve}")
    if "error" in result:
        raise Exception(f"Login error: {result['error']}")
    return result["result"]

def show_vms(headers):
    try:
        # Use vm.getAll to retrieve VMs.
        vms = rpc_call("vm.getAll", {}, 6, headers)
    except Exception as e:
        print("Error retrieving VM list:", e)
        return

    table_data = []
    if isinstance(vms, list):
        for vm in vms:
            vm_uuid = vm.get("uuid", "N/A")
            name = vm.get("name_label", "N/A")
            description = vm.get("name_description", "N/A")
            table_data.append([vm_uuid, name, description])
    else:
        print("Unexpected data structure:", type(vms))
        return

    if table_data:
        print(tabulate(table_data, headers=["VM UUID", "Name", "Description"], tablefmt="pretty"))
    else:
        print("No VMs found.")

if __name__ == '__main__':
    try:
        # Login to obtain a session token.
        token = login()
        # Now set up headers with the valid authentication token.
        headers = {
            "Content-Type": "application/json",
            "Cookie": f"authenticationToken={token}"
        }
        print("\nExisting VMs:")
        show_vms(headers)
    except Exception as e:
        print("Error:", e)
