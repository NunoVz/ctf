import requests
import time
from tabulate import tabulate

XO_URL = "http://xo-cslab.dei.uc.pt"
pool_id = "6ddb8190-651e-f8ed-7fab-5e5a225857b7"
token = "Aty79-OVxXiGY40-eCnWqq0YpeBsMZG-lZn73yec4H0"
cookies = {'authenticationToken': token}

# Endpoint to create a VM in the pool
create_vm_url = f"{XO_URL}/rest/v0/pools/{pool_id}/actions/create_vm"

# Basic payload with allowed properties
payload = {
    "name_label": "CTF_Script_Testing",
    "name_description": "A VM created via API in a specific pool",
    "template": "f13f9f69-28e4-43bf-a01a-ef9cd2fbae17"  # Ubuntu template UUID
}

# Create the VM
create_response = requests.post(create_vm_url, json=payload, cookies=cookies)
print("Create VM Status Code:", create_response.status_code)

# The response should be a task URL (e.g., "/rest/v0/tasks/0m7gd63lh")
task_url = create_response.text.strip()
print("Task URL:", task_url)

# Poll the task endpoint until the task completes
vm_id = None
full_task_url = XO_URL + task_url  # Ensure we build the full URL

while True:
    task_response = requests.get(full_task_url, cookies=cookies)
    if task_response.status_code != 200:
        print("Error polling task:", task_response.status_code)
        break
    try:
        task_data = task_response.json()
    except Exception as e:
        print("Error decoding task JSON:")
        print(task_response.text)
        break

    status = task_data.get("status")
    print("Task status:", status)
    if status == "Success":
        vm_id = task_data.get("result")
        print("Task completed successfully. VM ID:", vm_id)
        break
    elif status == "Failure":
        print("Task failed:", task_data)
        break
    else:
        # Task is still running; wait a bit before polling again
        time.sleep(2)

if not vm_id:
    print("VM was not created successfully; cannot start VM.")
else:
    # Start the VM if creation was successful
    start_url = f"{XO_URL}/rest/v0/vms/{vm_id}/start"
    start_response = requests.post(start_url, cookies=cookies)
    print("Start VM Status Code:", start_response.status_code)
    try:
        print("Start VM Response:", start_response.json())
    except Exception as e:
        print("Error starting VM:", start_response.text)

# Retrieve and display the list of VMs for verification
response = requests.get(f"{XO_URL}/rest/v0/vms", cookies=cookies)
try:
    vm_ids = response.json()
except requests.exceptions.JSONDecodeError:
    print("Failed to decode JSON from the VM list response.")
    print("Response content:", response.text)
    vm_ids = []

table_data = []
for vm_id in vm_ids:
    if isinstance(vm_id, str) and vm_id.startswith("/"):
        detail_url = XO_URL + vm_id
    else:
        detail_url = f"{XO_URL}/rest/v0/vms/{vm_id}"
    
    detail_response = requests.get(detail_url, cookies=cookies)
    if detail_response.status_code != 200:
        print(f"Failed to get details for VM ID {vm_id}. Status code: {detail_response.status_code}")
        print("Response content:", detail_response.text)
        continue
    try:
        vm_details = detail_response.json()
    except requests.exceptions.JSONDecodeError:
        print(f"Error decoding JSON for VM ID {vm_id}.")
        print("Response content:", detail_response.text)
        continue

    name = vm_details.get('name_label', 'N/A')
    description = vm_details.get('name_description', 'N/A')
    table_data.append([vm_id, name, description])

if table_data:
    print(tabulate(table_data, headers=["VM ID", "Name", "Description"], tablefmt="pretty"))
else:
    print("No VM details available.")
