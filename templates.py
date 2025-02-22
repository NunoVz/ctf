import requests

XO_URL = "http://xo-cslab.dei.uc.pt"
token = "Aty79-OVxXiGY40-eCnWqq0YpeBsMZG-lZn73yec4H0"
cookies = {'authenticationToken': token}

# Get the VM list from Xen Orchestra
response = requests.get(f"{XO_URL}/rest/v0/vms", cookies=cookies)
try:
    data = response.json()
except Exception as e:
    print("Error decoding JSON:", response.text)
    data = {}

templates = []

# Case 1: The API returns a dictionary with VM UUIDs as keys.
if isinstance(data, dict):
    for vm_uuid, details in data.items():
        if details.get("is_a_template"):
            templates.append({
                "uuid": vm_uuid,
                "name": details.get("name_label", "Unknown"),
                "description": details.get("name_description", "")
            })
# Case 2: The API returns a list of VM identifiers.
elif isinstance(data, list):
    for vm_id in data:
        # Build the detail URL—adjust if needed.
        if isinstance(vm_id, str) and vm_id.startswith("/"):
            detail_url = XO_URL + vm_id
        else:
            detail_url = f"{XO_URL}/rest/v0/vms/{vm_id}"
        detail_response = requests.get(detail_url, cookies=cookies)
        if detail_response.status_code != 200:
            continue
        try:
            details = detail_response.json()
        except Exception as e:
            continue
        if details.get("is_a_template"):
            templates.append({
                "uuid": vm_id,
                "name": details.get("name_label", "Unknown"),
                "description": details.get("name_description", "")
            })
else:
    print("Unexpected data structure:", type(data))

if templates:
    print("Available Templates:")
    for tmpl in templates:
        print(f"UUID: {tmpl['uuid']}  Name: {tmpl['name']}  Description: {tmpl['description']}")
else:
    print("No templates found.")
