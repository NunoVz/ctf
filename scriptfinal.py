import asyncio
import json
import uuid
import aiohttp
import re

# Constants
XO_WS_URL = "ws://xo-cslab.dei.uc.pt/api/"
USERNAME = "ctf"
PASSWORD = "cslabctf2024"
DEFAULT_VM_DESCRIPTION = "Created for Shift CTF! Make the flag (h)appen"
CONFIG_FILE = "config.json"
OUTPUT_FILE = "output.json"

async def send_rpc(ws, method, params):
    request_id = str(uuid.uuid4())
    request = {"jsonrpc": "2.0", "method": method, "params": params, "id": request_id}
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
    params = {"username": USERNAME, "password": PASSWORD}
    return await send_rpc(ws, "session.signIn", params)

async def get_existing_teams(ws):
    response = await send_rpc(ws, "xo.getAllObjects", {"filter": {"type": "VM"}})

    if "result" not in response:
        print("Failed to fetch VMs.")
        return 0  

    vms = response["result"]
    max_team_number = 0

    for vm in vms.values():
        name = vm.get("name_label", "")
        match = re.match(r"CTF-TEAM-(\d+)", name)
        if match:
            team_number = int(match.group(1))
            max_team_number = max(max_team_number, team_number)

    return max_team_number

async def create_vm(ws, vm_name, ip, template_uuid, network_uuid, description=DEFAULT_VM_DESCRIPTION):
    cloud_config = {
        "hostname": vm_name,
        "manage_etc_hosts": True,
        "network": {
            "version": 2,
            "ethernets": {
                "eth0": {
                    "addresses": [f"{ip}/24"],
                    "gateway4": "192.168.1.1",
                    "nameservers": {"addresses": ["8.8.8.8", "8.8.4.4"]}
                }
            }
        }
    }

    params = {
        "name_label": vm_name,
        "name_description": description,
        "template": template_uuid,
        "bootAfterCreate": True,
        "VIFs": [{"network": network_uuid, "allowedIpv4Addresses": [ip]}],
        "cloudConfig": json.dumps(cloud_config)
    }

    response = await send_rpc(ws, "vm.create", params)
    return response.get("result") if "result" in response else None

async def process_challenges(config):
    async with aiohttp.ClientSession() as session:
        async with session.ws_connect(XO_WS_URL) as ws:
            await sign_in(ws)
            max_team_number = await get_existing_teams(ws)
            new_team_number = max_team_number + 1 

            results = []
            subnet_base = config.get("subnet_base", "192.168.1")

            for challenge in config.get("challenges", []):
                challenge_name = challenge.get("name")
                vm_name = f"CTF-TEAM-{new_team_number}-{challenge_name}"
                ip = f"{subnet_base}.{challenge.get('ip_suffix', new_team_number)}"
                template_uuid = challenge.get("template_uuid")
                network_uuid = challenge.get("network_uuid")
                description = challenge.get("description", DEFAULT_VM_DESCRIPTION)

                vm_id = await create_vm(ws, vm_name, ip, template_uuid, network_uuid, description)

                if vm_id:
                    results.append({"team": new_team_number, "name": vm_name, "ip": ip, "vm_id": vm_id})
                else:
                    print(f"Failed to create VM for challenge: {vm_name}")

            return results

if __name__ == "__main__":
    # Load JSON config
    with open(CONFIG_FILE, "r") as file:
        config = json.load(file)

    # Process challenges and store results
    result = asyncio.run(process_challenges(config))
    
    with open(OUTPUT_FILE, "w") as file:
        json.dump(result, file, indent=4)

    print("Generated challenge VMs stored in:", OUTPUT_FILE)
