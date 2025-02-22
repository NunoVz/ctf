import requests
from tabulate import tabulate 
XO_URL = "http://xo-cslab.dei.uc.pt"

# admin user
# token = "cjnN9r5i88ZXzB-ffZXxh0uqpo4mSZ4Vj39GuFXZ4H4"

# ctf user
token = "Aty79-OVxXiGY40-eCnWqq0YpeBsMZG-lZn73yec4H0"
cookies = {'authenticationToken': token}


response = requests.get(f"{XO_URL}/rest/v0/vms", cookies=cookies)
vm_ids = response.json()

table_data = []

for vm_id in vm_ids:
    detail_response = requests.get(f"{XO_URL}/rest/v0/vms/{vm_id}", cookies=cookies)
    vm_details = detail_response.json()
    name = vm_details.get('name_label', 'N/A')
    description = vm_details.get('name_description', 'N/A')
    table_data.append([vm_id, name, description])

print(tabulate(table_data, headers=["VM ID", "Name", "Description"], tablefmt="pretty"))