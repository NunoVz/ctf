import asyncio
import json
import uuid
import aiohttp
from tabulate import tabulate

# Configuration values – replace these with your actual values
XO_WS_URL = "ws://xo-cslab.dei.uc.pt/api/"
username = "ctf"
password = "cslabctf2024"
template_id = "2efd48d2-b12d-8f3e-56e6-5ed41c02118b"  # Must be a template that supports Cloud‑Init
network_uuid = "ea5aca40-b7d2-b896-5efd-dce07151d4ba"   # Replace with your valid network UUID
default_vm_description = "Created via CLI with static IP via Cloud-Init"

def generate_cloud_config(ip, hostname):
    """
    Generate a Cloud‑Init configuration (as a JSON string) using the given IP and hostname.
    """
    config = {
        "hostname": hostname,
        "manage_etc_hosts": True,
        "network": {
            "version": 2,
            "ethernets": {
                "eth0": {
                    "addresses": [f"{ip}/24"],
                    "gateway4": "192.168.1.1",
                    "nameservers": {
                        "addresses": ["8.8.8.8", "8.8.4.4"]
                    }
                }
            }
        }
    }
    return json.dumps(config)

async def send_rpc(ws, method, params):
    """
    Build and send a JSON‑RPC request with a unique ID and wait for the matching response.
    """
    request_id = str(uuid.uuid4())
    request = {
        "jsonrpc": "2.0",
        "method": method,
        "params": params,
        "id": request_id
    }
    await ws.send_str(json.dumps(request))
    
    while True:
        msg = await ws.receive()
        if msg.type == aiohttp.WSMsgType.TEXT:
            response = json.loads(msg.data)
            if response.get("id") == request_id:
                return response
        elif msg.type == aiohttp.WSMsgType.ERROR:
            break
    return None

async def sign_in(ws):
    params = {"username": username, "password": password}
    response = await send_rpc(ws, "session.signIn", params)
    print("Sign in response:", response)
    return response

async def get_all(ws, object_type):
    """
    List objects using xo.getAllObjects filtered by type.
    """
    print(f"\nFetching list of {object_type}s...")
    response = await send_rpc(ws, "xo.getAllObjects", {"filter": {"type": object_type}})
    if "result" in response:
        objs = response["result"]
        table_data = []
        for obj_id, details in objs.items():
            name = details.get("name_label", "N/A")
            table_data.append([obj_id, name])
        if table_data:
            print(tabulate(table_data, headers=["ID", "Name"], tablefmt="pretty"))
        else:
            print(f"No {object_type}s found.")
    else:
        print("Failed to fetch objects. Response:", response)

async def create_vm_static(ws, vm_name, ip, description=default_vm_description):
    """
    Create a VM with static IP configuration via Cloud‑Init.
    """
    cloud_config_str = generate_cloud_config(ip, vm_name)
    params = {
        "name_label": vm_name,
        "name_description": description,
        "template": template_id,
        "VIFs": [
            {
                "network": network_uuid,
                # Remove "mac" to let XO assign one automatically.
                "allowedIpv4Addresses": [ip]
            }
        ],
        "cloudConfig": cloud_config_str
    }
    print(f"\nCreating VM '{vm_name}' with static IP {ip}...")
    response = await send_rpc(ws, "vm.create", params)
    print("Create VM response:", response)
    if "result" in response:
        return response["result"]
    return None

async def run_list_interactive(object_type):
    async with aiohttp.ClientSession() as session:
        async with session.ws_connect(XO_WS_URL) as ws:
            await sign_in(ws)
            await get_all(ws, object_type)

async def run_create_team_interactive(num_teams):
    async with aiohttp.ClientSession() as session:
        async with session.ws_connect(XO_WS_URL) as ws:
            await sign_in(ws)
            for team in range(1, num_teams + 1):
                # Create 5 VMs per team.
                for i in range(2):
                    vm_name = f"CTF-TEAM-{team}-TEST-{i+1}"
                    ip = f"192.168.{team}.{100 + i}"
                    vm_id = await create_vm_static(ws, vm_name, ip)
                    if vm_id:
                        print(f"Created VM for team {team}: {vm_name} with IP {ip} (ID: {vm_id})")
                    else:
                        print(f"Failed to create VM for team {team}: {vm_name} with IP {ip}")

async def run_create_vm_interactive(name, ip):
    async with aiohttp.ClientSession() as session:
        async with session.ws_connect(XO_WS_URL) as ws:
            await sign_in(ws)
            vm_id = await create_vm_static(ws, name, ip)
            if vm_id:
                print(f"Created VM '{name}' with IP {ip} (ID: {vm_id})")
            else:
                print("VM creation failed.")

def interactive_cli():
    print("Welcome to XO CLI")
    print("Select an option:")
    print("1. List objects (e.g., VM, host, network)")
    print("2. Create team VMs (ex:5 teams creates 2 VMs per team = 10 VMs)")
    print("3. Create a single VM")
    choice = input("Enter your choice (1/2/3): ").strip()

    if choice == "1":
        obj_type = input("Enter the type of object to list (e.g., VM, host, network): ").strip()
        asyncio.run(run_list_interactive(obj_type))
    elif choice == "2":
        try:
            num_teams = int(input("Enter the number of teams: ").strip())
            asyncio.run(run_create_team_interactive(num_teams))
        except ValueError:
            print("Invalid number entered.")
    elif choice == "3":
        vm_name = input("Enter the VM name: ").strip()
        ip = input("Enter the static IP address (e.g., 192.168.2.200): ").strip()
        asyncio.run(run_create_vm_interactive(vm_name, ip))
    else:
        print("Invalid choice. Exiting.")

if __name__ == "__main__":
    interactive_cli()
