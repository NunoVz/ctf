import requests
from tabulate import tabulate 
XO_URL = "http://xo-cslab.dei.uc.pt"

# admin user
# token = "cjnN9r5i88ZXzB-ffZXxh0uqpo4mSZ4Vj39GuFXZ4H4"

# ctf user
token = "Aty79-OVxXiGY40-eCnWqq0YpeBsMZG-lZn73yec4H0"
cookies = {'authenticationToken': token}


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