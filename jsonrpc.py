import json
import aiohttp
import asyncio

from jsonrpc_websocket import Server

async def routine():
  async with aiohttp.ClientSession() as client:
    server = Server('ws://xo-cslab.dei.uc.pt/api/', client)

    await server.ws_connect()

    # No signIn required
    methodsInfoResult = await server.system.getMethodsInfo()
    print('\n'.join([str(e) for e in methodsInfoResult.keys()]))

    # signIn required
    result = await server.session.signIn(username='ctf', password='cslabctf2024')
    result = await server.xo.getAllObjects(filter={"type": "VIF"}, limit=10)

    print('[')
    print(', \n'.join([str(json.dumps(e, indent=4)) for e in result.values()]))
    print(']')

asyncio.get_event_loop().run_until_complete(routine())