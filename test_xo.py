import requests

XO_URL = "http://xo-cslab.dei.uc.pt"

# admin user
# token = "cjnN9r5i88ZXzB-ffZXxh0uqpo4mSZ4Vj39GuFXZ4H4"

# ctf user
token = "Aty79-OVxXiGY40-eCnWqq0YpeBsMZG-lZn73yec4H0"
cookies = {'authenticationToken': token}

# Get VMs
vm_response = requests.get(f"{XO_URL}/rest/v0/vms", cookies=cookies)
print(vm_response.content)
