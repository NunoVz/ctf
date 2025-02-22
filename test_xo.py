import requests

XO_URL = "http://xo-cslab.dei.uc.pt"

# admin user
# token = "cjnN9r5i88ZXzB-ffZXxh0uqpo4mSZ4Vj39GuFXZ4H4"

# ctf user
token = "Aty79-OVxXiGY40-eCnWqq0YpeBsMZG-lZn73yec4H0"
cookies = {'authenticationToken': token}

# Get VMs
response = requests.get(f"{XO_URL}/rest/v0/vms", cookies=cookies)
vm_list = response.json()
for vm in vm_list:
    print(f"VM ID: {vm.get('id')}")
    print(f"Name: {vm.get('name_label')}")
    print(f"Description: {vm.get('name_description')}")
    print("-" * 20)
