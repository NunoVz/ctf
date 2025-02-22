import requests

XO_URL = "http://xo-cslab.dei.uc.pt"
token = "Aty79-OVxXiGY40-eCnWqq0YpeBsMZG-lZn73yec4H0"
cookies = {'authenticationToken': token}

def make_vm_template(vm_id):
    url = f"{XO_URL}/rest/v0/vms/{vm_id}/actions/make_template"
    response = requests.post(url, cookies=cookies)
    print("Make Template Status Code:", response.status_code)
    try:
        print("Response:", response.json())
    except Exception as e:
        print("Error parsing response:", response.text)

vm_id = "6365ed62-0c96-2465-ea9c-a70ed9832200"  
make_vm_template(vm_id)
