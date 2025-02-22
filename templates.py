import requests

XO_URL = "http://xo-cslab.dei.uc.pt"
token = "Aty79-OVxXiGY40-eCnWqq0YpeBsMZG-lZn73yec4H0"
cookies = {'authenticationToken': token}

response = requests.get(f"{XO_URL}/rest/v0/vms", cookies=cookies)
vms = response.json()
templates = [vm for vm in vms if vm.get("is_a_template")]

for tmpl in templates:
    print("Template Name:", tmpl.get("name_label"), "UUID:", tmpl.get("id"))
