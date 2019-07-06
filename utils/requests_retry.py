from AGGBackstage import config
from aiohttp.client_exceptions import (ServerDisconnectedError, ServerConnectionError, ClientOSError,
                                       ClientConnectorCertificateError, ServerTimeoutError, ContentTypeError,
                                       ClientConnectorError, ClientPayloadError)
from traceback import *
import aiohttp
import json
from asyncio import TimeoutError

def request_retry(func):
    async def _wrapper(*args, **kwargs):
        for _ in range(config.RETRY):
            try:
                return await func(*args, **kwargs)
            except (ServerDisconnectedError, ServerConnectionError, TimeoutError,
                    ClientConnectorError, ClientPayloadError, ServerTimeoutError,
                    ContentTypeError, ClientConnectorCertificateError, ClientOSError):
                print(format_exc())
            except Exception as e:
                print(format_exc())
                return False
        return False
    return _wrapper


@request_retry
async def req_test():
    conn = aiohttp.TCPConnector(ssl=False)
    async with aiohttp.ClientSession(connector=conn) as session:
        # async with session.get("http://www.baidu.comasd", verify_ssl=False, timeout=1) as resp:
        #     # print(await resp.text(encoding='utf-8'))
        #     pass
        json.loads('asd')
    return 1
#
#
# import asyncio
#
# f = req_test()
# loop = asyncio.get_event_loop()
# res = loop.run_until_complete(f)
# print(res)
