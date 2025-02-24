import asyncio
import json
import uuid
import aiohttp
from tabulate import tabulate

# Configuration values – replace these with your actual values
XO_WS_URL = "ws://xo-cslab.dei.uc.pt/api/"
username = "ctf"
password = "cslabctf2024"

# VM creation parameters
template_id = "2efd48d2-b12d-8f3e-56e6-5ed41c02118b"   # Must be a template that supports Cloud‑Init
network_uuid = "ea5aca40-b7d2-b896-5efd-dce07151d4ba"    # Replace with your valid network UUID
vm_name = "CTF SCRIPT TEST NETWORK"
vm_description = "Hello Shift (Focal Fossa)"

cloud_config = {
    "hostname": "my-vm",
    "manage_etc_hosts": True,
    "network": {
        "version": 2,
        "ethernets": {
            "eth0": {
                "addresses": ["192.168.1.100/24"],
                "gateway4": "192.168.1.1",
                "nameservers": {
                    "addresses": ["8.8.8.8", "8.8.4.4"]
                }
            }
        }
    }
}
cloud_config_str = json.dumps(cloud_config)

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
    params = {
        "username": username,
        "password": password
    }
    response = await send_rpc(ws, "session.signIn", params)
    print("Sign in response:", response)
    return response

async def create_vm_static(ws):
    """
    Create a VM with static IP configuration via Cloud‑Init.
    Note: 'cloudConfig' must be a string.
    """
    params = {
        "name_label": vm_name,
        "name_description": vm_description,
        "template": template_id,
        # Removed affinityHost for simplicity.
        "VIFs": [
            {
                "network": network_uuid,
                # Removed "mac": "auto" to let XO assign a MAC address automatically.
                "allowedIpv4Addresses": ["192.168.1.100"]
            }
        ],
        "cloudConfig": cloud_config_str
    }
    print("Creating VM with static IP configuration...")
    response = await send_rpc(ws, "vm.create", params)
    print("Create VM response:", response)
    if "result" in response:
        return response["result"]
    return None


async def get_all(ws,filter):
    print("Fetching list of VMs...")
    response = await send_rpc(ws, "xo.getAllObjects", {"filter": {"type": filter}})
    if "result" in response:
        vms = response["result"]
        table_data = []
        for vm_id, details in vms.items():
            name = details.get("name_label", "N/A")
            table_data.append([vm_id, name])
        if table_data:
            print(tabulate(table_data, headers=["VM ID", "Name"], tablefmt="pretty"))
        else:
            print("No VMs found.")
    else:
        print("Failed to fetch VMs. Response:", response)

async def main():
    async with aiohttp.ClientSession() as session:
        async with session.ws_connect(XO_WS_URL) as ws:
            # Sign in to the XO server
            await sign_in(ws)
            print("\nExisting VMs:")
            await get_all(ws,"VM")
            print("\nExisting Host:")
            await get_all(ws,"host")


            # Create the VM with static IP settings
            vm_id = await create_vm_static(ws)
            if vm_id:
                print("VM created with id:", vm_id)
            else:
                print("VM creation failed.")

            print("\nUpdated VM List:")
            await get_all(ws,"VM")

if __name__ == "__main__":
    asyncio.run(main())
