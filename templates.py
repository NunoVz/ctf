import requests
from tabulate import tabulate

XO_URL = "http://xo-cslab.dei.uc.pt"
endpoint = "/rest/v0/vm-templates"
url = XO_URL + endpoint
token = "Aty79-OVxXiGY40-eCnWqq0YpeBsMZG-lZn73yec4H0"
cookies = {'authenticationToken': token}

response = requests.get(url, cookies=cookies)
try:
    data = response.json()
except Exception as e:
    print("Error decoding JSON:", response.text)
    exit(1)

table_data = []

if isinstance(data, list):
    for template_uuid in data:
        detail_url = f"{XO_URL}/rest/v0/vm-templates/{template_uuid}"
        detail_response = requests.get(detail_url, cookies=cookies)
        if detail_response.status_code != 200:
            print(f"Failed to get details for template {template_uuid}: {detail_response.status_code}")
            continue
        try:
            details = detail_response.json()
        except Exception as e:
            print(f"Error decoding details for template {template_uuid}: {detail_response.text}")
            continue
        name = details.get("name_label", "N/A")
        table_data.append([template_uuid, name])
elif isinstance(data, dict):
    for template_uuid, details in data.items():
        name = details.get("name_label", "N/A")
        table_data.append([template_uuid, name])
else:
    print("Unexpected data structure:", type(data))
    exit(1)

if table_data:
    print(tabulate(table_data, headers=["Template UUID", "Name"], tablefmt="pretty"))
else:
    print("No templates found.")
