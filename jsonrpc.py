import asyncio
import json
import uuid
import aiohttp
from tabulate import tabulate

# Configuration values
XO_WS_URL = "ws://xo-cslab.dei.uc.pt/api/"
pool_id = "6ddb8190-651e-f8ed-7fab-5e5a225857b7"
template_id = "2efd48d2-b12d-8f3e-56e6-5ed41c02118b"  # CentOS template
vm_name = "CAPTURE_THE_FLAG_TEST_SCRIPT"
vm_description = "HEllo world!"
username = "ctf"
password = "cslabctf2024"

async def send_rpc(ws, method, params):
    """
    Build and send a JSON-RPC request and wait for the response.
    """
    request_id = str(uuid.uuid4())
    request = {
        "jsonrpc": "2.0",
        "method": method,
        "params": params,
        "id": request_id
    }
    # Send the JSON-RPC message
    await ws.send_str(json.dumps(request))
    
    # Wait for a matching response
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
    # Build the sign-in call like your Java snippet
    params = {
        "username": username,
        "password": password
    }
    print("Signing in...")
    response = await send_rpc(ws, "session.signIn", params)
    print("Sign in response:", response)
    return response

async def create_vm(ws):
    # Build the vm.create call, with parameters similar to:
    # signIn.getParams().put("name_label", "CAPTURE_THE_FLAG_TEST_SCRIPT");
    # signIn.getParams().put("template", "template_id"); etc.
    params = {
        "pool": pool_id,
        "name_label": vm_name,
        "name_description": vm_description,
        "template": template_id
        # Add additional vm.create parameters here as needed.
    }
    print("Creating a new VM using vm.create...")
    response = await send_rpc(ws, "vm.create", params)
    print("Create VM response:", response)
    return response.get("result")

async def start_vm(ws, vm_id):
    print("Starting VM with ID:", vm_id)
    response = await send_rpc(ws, "vm.start", {"vm": vm_id})
    print("Start VM response:", response)

async def get_all_vms(ws):
    print("Fetching list of VMs...")
    # Here we assume xo.getAllObjects returns a dict of objects
    response = await send_rpc(ws, "xo.getAllObjects", {"filter": {"type": "VM"}})
    if "result" in response:
        vms = response["result"]
        table_data = []
        for vm_id, details in vms.items():
            name = details.get("name_label", "N/A")
            description = details.get("name_description", "N/A")
            table_data.append([vm_id, name, description])
        if table_data:
            print(tabulate(table_data, headers=["VM ID", "Name", "Description"], tablefmt="pretty"))
        else:
            print("No VMs found.")
    else:
        print("Failed to fetch VMs. Response:", response)

async def main():
    async with aiohttp.ClientSession() as session:
        async with session.ws_connect(XO_WS_URL) as ws:
            # Sign in
            await sign_in(ws)
            
            # Show existing VMs
            print("\nExisting VMs:")
            await get_all_vms(ws)
            
            # Create a new VM
            vm_id = await create_vm(ws)
            if vm_id:
                # Start the VM
                await start_vm(ws, vm_id)
            else:
                print("VM creation failed.")
            
            # Show updated VMs
            print("\nUpdated VM List:")
            await get_all_vms(ws)

if __name__ == '__main__':
    asyncio.run(main())
