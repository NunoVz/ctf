import requests
from tabulate import tabulate

# JSON-RPC endpoint and credentials
JSON_RPC_URL = "http://xo-cslab.dei.uc.pt/jsonrpc"
token = "Aty79-OVxXiGY40-eCnWqq0YpeBsMZG-lZn73yec4H0"
headers = {
    "Content-Type": "application/json",
    "Cookie": f"authenticationToken={token}"
}

def rpc_call(method, params, rpc_id):
    payload = {
        "jsonrpc": "2.0",
        "method": method,
        "params": params,
        "id": rpc_id
    }
    response = requests.post(JSON_RPC_URL, json=payload, headers=headers)
    # Debug: print the raw response text to help diagnose issues.
    print("Response text:", response.text)
    try:
        result = response.json()
    except ValueError as ve:
        raise Exception(f"Invalid JSON response: {ve}")
    if "error" in result:
        raise Exception(f"Error calling {method}: {result['error']}")
    return result["result"]

def show_vms():
    try:
        # Use vm.getAll to retrieve the list of VMs.
        vms = rpc_call("vm.getAll", {}, 6)
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
    print("Existing VMs:")
    show_vms()
