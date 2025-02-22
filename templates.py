import requests
from tabulate import tabulate

XO_URL = "http://xo-cslab.dei.uc.pt"
endpoint = "/rest/v0/vm-templates"
url = XO_URL + endpoint
token = "Aty79-OVxXiGY40-eCnWqq0YpeBsMZG-lZn73yec4H0"
cookies = {'authenticationToken': token}

# Request the list of VM templates
response = requests.get(url, cookies=cookies)
try:
    data = response.json()
except Exception as e:
    print("Error decoding JSON:", response.text)
    exit(1)

table_data = []

# If data is a list of paths, process each template
if isinstance(data, list):
    for template_path in data:
        detail_url = XO_URL + template_path  # Full URL to get template details
        detail_response = requests.get(detail_url, cookies=cookies)
        if detail_response.status_code != 200:
            print(f"Failed to get details for template {template_path}: {detail_response.status_code}")
            continue
        try:
            details = detail_response.json()
        except Exception as e:
            print(f"Error decoding details for template {template_path}: {detail_response.text}")
            continue
        # Get the name and extract the UUID from the path
        name = details.get("name_label", "N/A")
        template_uuid = template_path.split('/')[-1]
        table_data.append([template_uuid, name])
# Alternatively, if data is a dict, iterate over key-value pairs
elif isinstance(data, dict):
    for template_uuid, details in data.items():
        name = details.get("name_label", "N/A")
        table_data.append([template_uuid, name])
else:
    print("Unexpected data structure:", type(data))
    exit(1)

# Print the results in a formatted table
if table_data:
    print(tabulate(table_data, headers=["Template UUID", "Name"], tablefmt="pretty"))
else:
    print("No templates found.")
