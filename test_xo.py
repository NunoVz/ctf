import requests
import time
from tabulate import tabulate

XO_URL = "http://xo-cslab.dei.uc.pt"
pool_id = "6ddb8190-651e-f8ed-7fab-5e5a225857b7"
token = "Aty79-OVxXiGY40-eCnWqq0YpeBsMZG-lZn73yec4H0"
cookies = {'authenticationToken': token}

# Endpoint to create a VM in the pool
create_vm_url = f"{XO_URL}/rest/v0/pools/{pool_id}/actions/create_vm"

payload = {
    "name_label": "My Custom VM",
    "name_description": "This VM was created via API with a custom name and description",
    "template": "f13f9f69-28e4-43bf-a01a-ef9cd2fbae17"  # Replace with your Ubuntu template UUID
}

def create_vm():
    # Send the create VM request
    create_response = requests.post(create_vm_url, json=payload, cookies=cookies)
    print("Create VM Status Code:", create_response.status_code)

    # The response returns a task URL (e.g., "/rest/v0/tasks/0m7gd9bte")
    task_url = create_response.text.strip()
    print("Task URL:", task_url)

    # Poll the task endpoint until completion
    vm_id = None
    full_task_url = XO_URL + task_url  # Build full URL for the task
    while True:
        r = requests.get(full_task_url, cookies=cookies)
        if r.status_code != 200:
            print("Error polling task:", r.status_code)
            break
        task_data = r.json()
        print("Task data:", task_data)
        if task_data.get("status") == "Failure":
            print("Task failed with error:", task_data.get("error"))
            break
        elif task_data.get("status") == "Success":
            # The 'result' field should contain the new VM's ID
            vm_id = task_data.get("result")
            print("Task succeeded. VM ID:", vm_id)
            break
        else:
            time.sleep(2)

    if not vm_id:
        print("VM was not created successfully; cannot start VM.")
    else:
        # Start the newly created VM
        start_url = f"{XO_URL}/rest/v0/vms/{vm_id}/start"
        start_response = requests.post(start_url, cookies=cookies)
        print("Start VM Status Code:", start_response.status_code)
        try:
            print("Start VM Response:", start_response.json())
        except Exception as e:
            print("Error starting VM:", start_response.text)

def show_vms():
    response = requests.get(f"{XO_URL}/rest/v0/vms", cookies=cookies)
    try:
        data = response.json()
    except requests.exceptions.JSONDecodeError:
        print("Failed to decode JSON from the VM list response.")
        print("Response content:", response.text)
        data = {}
    
    table_data = []
    if isinstance(data, dict):
        for vm_id, details in data.items():
            name = details.get('name_label', 'N/A')
            description = details.get('name_description', 'N/A')
            table_data.append([vm_id, name, description])
    elif isinstance(data, list):
        for vm_id in data:
            if isinstance(vm_id, str) and vm_id.startswith("/"):
                detail_url = XO_URL + vm_id
            else:
                detail_url = f"{XO_URL}/rest/v0/vms/{vm_id}"
            detail_response = requests.get(detail_url, cookies=cookies)
            if detail_response.status_code != 200:
                continue
            try:
                details = detail_response.json()
            except requests.exceptions.JSONDecodeError:
                continue
            name = details.get('name_label', 'N/A')
            description = details.get('name_description', 'N/A')
            table_data.append([vm_id, name, description])
    else:
        print("Unexpected data structure:", type(data))
    
    if table_data:
        print(tabulate(table_data, headers=["VM ID", "Name", "Description"], tablefmt="pretty"))
    else:
        print("No VM details available.")

if __name__ == '__main__':
    print("Creating a custom VM...")
    create_vm()
    print("\nCurrent VMs:")
    show_vms()
