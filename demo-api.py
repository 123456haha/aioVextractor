#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 10/15/19
# IDE: PyCharm

## add current path to system path temporary
import sys, os

curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)

from sanic import response as Response
from sanic import Sanic
from sanic_cors import CORS
import platform
from aioVextractor import extract
import aiohttp
from aioVextractor import config

if platform.system() in {"Linux", "Darwin"}:
    import uvloop
    uvloop.install()
else:
    pass

app = Sanic()
app.config.KEEP_ALIVE = True
app.config.KEEP_ALIVE_TIMEOUT = 500
app.config.RESPONSE_TIMEOUT = 500
CORS(app, automatic_options=True)


@app.route('/')
async def homepage(request):
    response = {k: {"method": v[1][1],
                    "url": app.url_for(k,
                                       _external=True,
                                       _server=f"http://{config.LOCAL_IP_ADDR}:{config.SANIC_PORT}"),
                    "pattern": v[1][2].pattern,
                    "parameters": v[1][3],
                    } for k, v in app.router.routes_names.items()}
    return Response.json(response)


@app.route('/extractor', methods=['GET', 'POST'], name='extractor')
async def extractor(request):
    if request.method == 'GET':
        url = request.args.get('url')
    else:  ## request.method == 'POST'
        try:
            url = request.json.get('url')
        except:
            url = request.form.get('url')
    if url:
        async with  aiohttp.ClientSession() as session:
            result = extract(webpage_url=url, session=session)
            if isinstance(result, str):
                return Response.json({"msg": result,
                                      "data": None},
                                     status=400)
            else:
                return Response.json({
                    "msg": "success",
                    "data": result
                })
    else:
        return Response.json({"msg": "There is not enough input🤯",
                              "data": None},
                             status=400)


if __name__ == '__main__':
    app.run(host='0.0.0.0',
            port=config.SANIC_PORT,
            workers=config.SANIC_WORKER,
            debug=True,
            access_log=True,
            strict_slashes=False,
            )
