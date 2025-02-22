import requests
from tabulate import tabulate 
XO_URL = "http://xo-cslab.dei.uc.pt"

# admin user
# token = "cjnN9r5i88ZXzB-ffZXxh0uqpo4mSZ4Vj39GuFXZ4H4"

# ctf user
token = "Aty79-OVxXiGY40-eCnWqq0YpeBsMZG-lZn73yec4H0"
cookies = {'authenticationToken': token}

# Get VMs from Xen Orchestra
response = requests.get(f"{XO_URL}/rest/v0/vms", cookies=cookies)
vms = response.json()

table_data = []
for vm in vms:
    vm_id = vm.get('id', 'N/A')
    name = vm.get('name_label', 'N/A')
    description = vm.get('name_description', 'N/A')
    table_data.append([vm_id, name, description])


print(tabulate(table_data, headers=["VM ID", "Name", "Description"], tablefmt="pretty"))