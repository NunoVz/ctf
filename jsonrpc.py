import asyncio
import argparse
import json
import uuid
import aiohttp
from tabulate import tabulate

XO_WS_URL = "ws://xo-cslab.dei.uc.pt/api/"
username = "ctf"
password = "cslabctf2024"
template_id = "2efd48d2-b12d-8f3e-56e6-5ed41c02118b"  
network_uuid = "ea5aca40-b7d2-b896-5efd-dce07151d4ba"   # Replace with your valid network UUID
default_vm_description = "Created via CLI with static IP via Cloud-Init"

def generate_cloud_config(ip, hostname):
    """
    Generate a Cloud-Init configuration as a JSON string using the given IP and hostname.
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
    print(f"Fetching list of {object_type}s...")
    response = await send_rpc(ws, "xo.getAllObjects", {"filter": {"type": object_type}})
    if "result" in response:
        objects = response["result"]
        table_data = []
        for obj_id, details in objects.items():
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
    Create a VM with a static IP configuration via Cloud‑Init.
    """
    cloud_config_str = generate_cloud_config(ip, vm_name)
    params = {
        "name_label": vm_name,
        "name_description": description,
        "template": template_id,
        "VIFs": [
            {
                "network": network_uuid,
                "allowedIpv4Addresses": [ ip ]
            }
        ],
        "cloudConfig": cloud_config_str
    }
    print(f"Creating VM '{vm_name}' with static IP {ip}...")
    response = await send_rpc(ws, "vm.create", params)
    print("Create VM response:", response)
    if "result" in response:
        return response["result"]
    return None

def parse_args():
    parser = argparse.ArgumentParser(
        description="XO CLI to list objects and create VMs with static IP configuration"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    list_parser = subparsers.add_parser("list", help="List objects by type (e.g., VM, host, network)")
    list_parser.add_argument("object_type", type=str, help="Type of object to list (e.g., VM, host)")

    team_parser = subparsers.add_parser("create-team", help="Create VMs for teams")
    team_parser.add_argument("num_teams", type=int, help="Number of teams")

    single_parser = subparsers.add_parser("create-vm", help="Create a single VM")
    single_parser.add_argument("name", type=str, help="Name for the VM")
    single_parser.add_argument("ip", type=str, help="Static IP address for the VM")
    
    return parser.parse_args()

async def run_cli(args):
    async with aiohttp.ClientSession() as session:
        async with session.ws_connect(XO_WS_URL) as ws:
            await sign_in(ws)

            if args.command == "list":
                await get_all(ws, args.object_type)
            elif args.command == "create-team":
                num_teams = args.num_teams
                for team in range(1, num_teams + 1):
                    for i in range(5):
                        vm_name = f"CTF-TEAM-{team}-TEST-{i+1}"
                        ip = f"192.168.{team}.{100 + i}"
                        vm_id = await create_vm_static(ws, vm_name, ip)
                        if vm_id:
                            print(f"Created VM for team {team}: {vm_name} with IP {ip} (ID: {vm_id})")
                        else:
                            print(f"Failed to create VM for team {team}: {vm_name} with IP {ip}")
            elif args.command == "create-vm":
                vm_id = await create_vm_static(ws, args.name, args.ip)
                if vm_id:
                    print(f"Created VM '{args.name}' with IP {args.ip} (ID: {vm_id})")
                else:
                    print("VM creation failed.")
            else:
                print("Unknown command.")

def main():
    args = parse_args()
    asyncio.run(run_cli(args))

if __name__ == "__main__":
    main()
