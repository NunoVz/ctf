import asyncio
import json
import uuid
import aiohttp

# Configuration values – replace these with your actual values
XO_WS_URL = "ws://xo-cslab.dei.uc.pt/api/"
username = "ctf"
password = "cslabctf2024"

# VM creation parameters
pool_id = "6ddb8190-651e-f8ed-7fab-5e5a225857b7"
template_id = "17a818b5-20a6-4d34-a7ef-320da9ef4c14 "   # Must be a template that supports Cloud‑Init
host_uuid = "8cc792b1-d2c1-4a23-bd33-291d006cf7f5"         # Replace with the actual host UUID
network_uuid = "ea5aca40-b7d2-b896-5efd-dce07151d4ba"   
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
    Create a VM with a static IP configuration via Cloud‑Init.
    Note: According to your accepted parameters, the 'cloudConfig' property must be a string.
    """
    params = {
        "name_label": vm_name,
        "name_description": vm_description,
        "template": template_id,
        "affinityHost": host_uuid,  
        "VIFs": [
            {
                "network": network_uuid,
                "mac": "auto",
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
async def get_all_vms(ws):
    print("Fetching list of VMs...")
    response = await send_rpc(ws, "xo.getAllObjects", {"filter": {"type": "host"}})
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

            get_all_vms(ws)
            # Create the VM with static IP settings
#            vm_id = await create_vm_static(ws)
 #           if vm_id:
  #              print("VM created with id:", vm_id)
   #         else:
    #            print("VM creation failed.")

if __name__ == "__main__":
    asyncio.run(main())
