import requests
from tabulate import tabulate

XO_URL = "http://xo-cslab.dei.uc.pt"
token = "Aty79-OVxXiGY40-eCnWqq0YpeBsMZG-lZn73yec4H0"
cookies = {'authenticationToken': token}

# Get the VM details
response = requests.get(f"{XO_URL}/rest/v0/vms", cookies=cookies)

try:
    data = response.json()
except Exception as e:
    print("Error decoding JSON:", e)
    data = {}

table_data = []

# If the response is a dictionary, iterate over its keys (VM IDs) and values (details)
if isinstance(data, dict):
    for vm_id, details in data.items():
        name = details.get('name_label', 'N/A')
        description = details.get('name_description', 'N/A')
        is_template = details.get('is_a_template', False)
        template_status = "Yes" if is_template else "No"
        table_data.append([vm_id, name, description, template_status])
# In case the response is a list (unlikely), fetch each detail individually.
elif isinstance(data, list):
    for vm_id in data:
        # Construct detail URL (adjust if needed)
        if isinstance(vm_id, str) and vm_id.startswith("/"):
            detail_url = XO_URL + vm_id
        else:
            detail_url = f"{XO_URL}/rest/v0/vms/{vm_id}"
        detail_response = requests.get(detail_url, cookies=cookies)
        if detail_response.status_code != 200:
            print(f"Failed to get details for VM ID {vm_id}. Status code: {detail_response.status_code}")
            continue
        details = detail_response.json()
        name = details.get('name_label', 'N/A')
        description = details.get('name_description', 'N/A')
        is_template = details.get('is_a_template', False)
        template_status = "Yes" if is_template else "No"
        table_data.append([vm_id, name, description, template_status])
else:
    print("Unexpected data structure:", type(data))

if table_data:
    print(tabulate(table_data, headers=["VM ID", "Name", "Description", "Template"], tablefmt="pretty"))
else:
    print("No VM details available.")
