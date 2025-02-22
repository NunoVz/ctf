import requests
from tabulate import tabulate 
XO_URL = "http://xo-cslab.dei.uc.pt"
pool_id = "6ddb8190-651e-f8ed-7fab-5e5a225857b7"

# admin user
# token = "cjnN9r5i88ZXzB-ffZXxh0uqpo4mSZ4Vj39GuFXZ4H4"

# ctf user
token = "Aty79-OVxXiGY40-eCnWqq0YpeBsMZG-lZn73yec4H0"
cookies = {'authenticationToken': token}



create_vm_url = f"{XO_URL}/rest/v0/pools/{pool_id}/actions/create_vm"

payload = {
    "name_label": "CTF_Script_Testing",
    "name_description": "A VM created via API in a specific pool",
    "template": "f13f9f69-28e4-43bf-a01a-ef9cd2fbae17",  # Ubuntu template UUID, for example
    "start": False,  # Create without starting immediately; we start it later
    "nics": [
        {
            "network": "ea5aca40-b7d2-b896-5efd-dce07151d4ba",  # <-- Replace with your actual subnetwork UUID
            "ip_configuration": {
                "static": True,
                "ip": "192.168.1.100",      # Customize this IP as needed
                "gateway": "192.168.1.1",     # Gateway for the subnetwork
                "netmask": "255.255.255.0"    # Netmask for the subnetwork
            }
        }
    ]
}

# Create the VM
create_response = requests.post(create_vm_url, json=payload, cookies=cookies)
print("Create VM Status Code:", create_response.status_code)

try:
    vm_data = create_response.json()
    vm_id = vm_data.get("id")
    print("Created VM ID:", vm_id)
except Exception as e:
    print("Error parsing the response:")
    print(create_response.text)
    vm_id = None

# Start the VM if it was created successfully
if vm_id:
    start_url = f"{XO_URL}/rest/v0/vms/{vm_id}/start"
    start_response = requests.post(start_url, cookies=cookies)
    print("Start VM Status Code:", start_response.status_code)
    try:
        print("Start VM Response:", start_response.json())
    except Exception as e:
        print("Error starting VM:", start_response.text)
else:
    print("VM was not created successfully; cannot start VM.")

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