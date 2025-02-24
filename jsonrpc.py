import asyncio
import json
import aiohttp
from tabulate import tabulate
from jsonrpc_websocket import Server

XO_WS_URL = "ws://xo-cslab.dei.uc.pt/api/"
pool_id = "6ddb8190-651e-f8ed-7fab-5e5a225857b7"
template_id = "2efd48d2-b12d-8f3e-56e6-5ed41c02118b"  # CentOS template
vm_name = "CAPTURE_THE_FLAG_TEST_SCRIPT"
vm_description = "HEllo world!"

async def show_vms(server):
    vms = await server.xo.getAllObjects(filter={"type": "VM"})
    table_data = []
    for vm_id, details in vms.items():
        name = details.get("name_label", "N/A")
        description = details.get("name_description", "N/A")
        table_data.append([vm_id, name, description])
    if table_data:
        print(vms)
    else:
        print("No VMs found.")

async def create_vm(server):
    payload = {"vm": 
                {
                "name_label": "...",
                "template": "...",
                "name_description": "...",
                "pool": pool_id,
                }
            }

    
    print("Creating a new VM based on the template...")

    vm_id = await server.vm.create(payload)
    print("VM creation initiated. Returned VM identifier:", vm_id)
    return vm_id

async def start_vm(server, vm_id):
    print("Starting VM:", vm_id)
    result = await server.vm.start(vm_id)
    print("VM start initiated. Result:", result)
    print("VM successfully started!")

async def main():
    async with aiohttp.ClientSession() as client:
        server = Server(XO_WS_URL, client)
        await server.ws_connect()

        sign_in_result = await server.session.signIn(username='ctf', password='cslabctf2024')
        print("Signed in:", sign_in_result)

        print("\nExisting VMs:")
        await show_vms(server)

        print("\nCreating a new VM based on the template...")
        vm_id = await create_vm(server)
        if vm_id:
            await start_vm(server, vm_id)
        else:
            print("VM creation failed.")

        print("\nUpdated VM List:")
        await show_vms(server)

if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())
