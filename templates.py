import requests

XO_URL = "http://xo-cslab.dei.uc.pt"
token = "Aty79-OVxXiGY40-eCnWqq0YpeBsMZG-lZn73yec4H0"
cookies = {'authenticationToken': token}

# Get the list of VM IDs (strings)
response = requests.get(f"{XO_URL}/rest/v0/vms", cookies=cookies)
vm_ids = response.json()  # This is a list of strings

templates = []

# Iterate over each VM ID and fetch its details
for vm_id in vm_ids:
    detail_url = f"{XO_URL}/rest/v0/vms/{vm_id}"
    detail_response = requests.get(detail_url, cookies=cookies)
    if detail_response.status_code != 200:
        print(f"Failed to get details for VM ID {vm_id}: {detail_response.status_code}")
        continue

    try:
        vm_details = detail_response.json()
    except Exception as e:
        print(f"Error decoding JSON for VM ID {vm_id}: {detail_response.text}")
        continue

    # Check if the VM is a template
    if vm_details.get("is_a_template"):
        templates.append(vm_details)

# Now, print out the template names and UUIDs
for tmpl in templates:
    print(f"Template Name: {tmpl.get('name_label')}, UUID: {tmpl.get('id')}")
