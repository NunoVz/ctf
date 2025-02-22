import requests
from tabulate import tabulate

XO_URL = "http://xo-cslab.dei.uc.pt"
TEMPLATES_ENDPOINT = "/rest/v0/vm-templates"
NETWORKS_ENDPOINT = "/rest/v0/networks"
token = "Aty79-OVxXiGY40-eCnWqq0YpeBsMZG-lZn73yec4H0"
cookies = {'authenticationToken': token}

# Function to fetch and process data from API
def fetch_data(url):
    response = requests.get(url, cookies=cookies)
    try:
        return response.json()
    except Exception as e:
        print(f"Error decoding JSON from {url}:", response.text)
        return None

# Fetch VM Templates
templates_url = XO_URL + TEMPLATES_ENDPOINT
templates_data = fetch_data(templates_url)
template_table = []

if isinstance(templates_data, list):
    for template_path in templates_data:
        detail_url = XO_URL + template_path
        details = fetch_data(detail_url)
        if details:
            name = details.get("name_label", "N/A")
            template_uuid = template_path.split('/')[-1]
            template_table.append([template_uuid, name])
elif isinstance(templates_data, dict):
    for template_uuid, details in templates_data.items():
        name = details.get("name_label", "N/A")
        template_table.append([template_uuid, name])

# Fetch Networks
networks_url = XO_URL + NETWORKS_ENDPOINT
networks_data = fetch_data(networks_url)
network_table = []

if isinstance(networks_data, dict):
    for network_uuid, details in networks_data.items():
        name = details.get("name_label", "N/A")
        description = details.get("description", "N/A")
        network_table.append([network_uuid, name, description])

# Print results
if template_table:
    print("VM Templates:")
    print(tabulate(template_table, headers=["Template UUID", "Name"], tablefmt="pretty"))
else:
    print("No VM templates found.")

if network_table:
    print("\nNetworks:")
    print(tabulate(network_table, headers=["Network UUID", "Name", "Description"], tablefmt="pretty"))
else:
    print("No networks found.")
