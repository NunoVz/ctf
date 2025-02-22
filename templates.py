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

# Assuming the endpoint returns a dictionary where each key is the template UUID
if isinstance(data, dict):
    for template_uuid, details in data.items():
        name = details.get("name_label", "N/A")
        table_data.append([template_uuid, name])
elif isinstance(data, list):
    # Alternatively, if the endpoint returns a list of template objects
    for item in data:
        uuid = item.get("id", "N/A")
        name = item.get("name_label", "N/A")
        table_data.append([uuid, name])
else:
    print("Unexpected data structure:", type(data))
    exit(1)

if table_data:
    print(tabulate(table_data, headers=["Template UUID", "Name"], tablefmt="pretty"))
else:
    print("No templates found.")
