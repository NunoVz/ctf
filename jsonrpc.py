import requests
import time
from tabulate import tabulate

# JSON-RPC endpoint and credentials
JSON_RPC_URL = "http://xo-cslab.dei.uc.pt/jsonrpc"
pool_id = "6ddb8190-651e-f8ed-7fab-5e5a225857b7"
token = "Aty79-OVxXiGY40-eCnWqq0YpeBsMZG-lZn73yec4H0"
headers = {
    "Content-Type": "application/json",
    "Cookie": f"authenticationToken={token}"
}

def rpc_call(method, **params):
    payload = {
       "jsonrpc": "2.0",
       "id": 1,
       "method": method,
       "params": params
    }
    response = requests.post(JSON_RPC_URL, json=payload, headers=headers)
    result = response.json()
    if "error" in result:
        raise Exception(f"Error calling {method}: {result['error']}")
    return result["result"]

def show_vms():
    try:
        vms = rpc_call("vm.list")
    except Exception as e:
        print("Error retrieving VM list:", e)
        return

    table_data = []
    if isinstance(vms, list):
        for vm in vms:
            vm_id = vm.get("id", "N/A")
            name = vm.get("name_label", "N/A")
            description = vm.get("name_description", "N/A")
            table_data.append([vm_id, name, description])
    elif isinstance(vms, dict):
        for vm_id, details in vms.items():
            name = details.get("name_label", "N/A")
            description = details.get("name_description", "N/A")
            table_data.append([vm_id, name, description])
    else:
        print("Unexpected data structure:", type(vms))
        return

    if table_data:
        print(tabulate(table_data, headers=["VM ID", "Name", "Description"], tablefmt="pretty"))
    else:
        print("No VMs found.")

def poll_task(task_id):
    vm_id = None
    while True:
        try:
            task_data = rpc_call("task.status", id=task_id)
        except Exception as e:
            print("Error polling task:", e)
            break

        status = task_data.get("status", "").lower()
        print("Task status:", status)
        if status == "failure":
            print("Task failed with error:", task_data.get("error"))
            break
        elif status == "success":
            vm_id = task_data.get("result")
            print("Task succeeded. Result:", vm_id)
            break
        else:
            time.sleep(2)
    return vm_id

def create_vm():
    params = {
        "pool": pool_id,
        "name_label": "CAPTURE_THE_FLAG_TEST_SCRIPT",
        "name_description": "Hello world!",
        "template": "2efd48d2-b12d-8f3e-56e6-5ed41c02118b"
    }
    try:
        task_id = rpc_call("vm.create", **params)
        print("Create VM task ID:", task_id)
    except Exception as e:
        print("Error creating VM:", e)
        return None

    vm_id = poll_task(task_id)
    return vm_id

def start_vm(vm_id):
    params = {"vm": vm_id}
    try:
        task_id = rpc_call("vm.start", **params)
        print("Start VM task ID:", task_id)
    except Exception as e:
        print("Error starting VM:", e)
        return

    result = poll_task(task_id)
    if result:
        print("VM started successfully!")
    else:
        print("VM start failed.")

if __name__ == '__main__':
    print("Existing VMs:")
    show_vms()

    print("\nCreating a new VM based on the template...")
    vm_id = create_vm()

    if vm_id:
        print("\nStarting the VM...")
        start_vm(vm_id)
    else:
        print("VM creation failed.")

    print("\nUpdated VM List:")
    show_vms()
