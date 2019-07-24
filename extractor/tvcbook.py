#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 2019/6/20
# IDE: PyCharm


import jmespath
from aioVextractor.utils.user_agent import UserAgent
from aioVextractor.utils.requests_retry import RequestRetry
from random import choice
import time
from os.path import splitext
from scrapy.selector import Selector
import asyncio
import html
import emoji
import dateutil.parser
import traceback
from urllib.parse import urlparse
import os

@RequestRetry
async def entrance(webpage_url, session):
    vid = webpage_url.split("vid=")[1]
    video = await extract_video_info(vid=vid, session=session)
    # print(video)
    video['webpage_url'] = webpage_url
    return video


async def extract_video_info( vid, session):
    extract_video_info_url = f'https://api.tvcbook.com/video/{vid}?access-token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJodHRwczpcL1wvYXBpeC50dmNib29rLmNvbVwvYXBpXC9hY2NvdW50XC9sb2dpbiIsImlhdCI6MTU2MzQyMDk3MCwiZXhwIjoxNTY0MDI1NzcwLCJuYmYiOjE1NjM0MjA5NzAsImp0aSI6IkcyTkFaNEtQTVJLUE0wNjciLCJzdWIiOjQ5MywicHJ2IjoiZmZmNjVkZGQ1NzJmZTQyOGIwMzg0MmVlNTI1NGE3OWVmYWJhNTk1MiJ9.cxIaxwdaVvG7JmGDa4Oq12CSQuzPdnGm8HfIpW_n8Ys&expand=media,user,tags,type_id&code=e877ETnlT03MmzcoDHuw0zAiBpmQn5aErZMpG4r50GPvjO_P0gLn'
    # print(extract_video_info_url)
    headers = {
        'authority': 'api.tvcbook.com',
        'cache-control': 'max-age=0',
        'upgrade-insecure-requests': '1',
        'user-agent': 'PostmanRuntime/7.15.2',
        # 'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,ko;q=0.7',
    }
    async with session.get(extract_video_info_url, headers=headers) as response:
        response_json = await response.json()
        result = dict()
        videoitem = response_json.get('data',{}).get('data')
        result['title'] = videoitem.get('title','')
        result['vid'] = vid
        result['created_at'] = videoitem.get('created_at','')
        result['duration'] = int(str(str(videoitem.get('duration',0))+".").split(".")[0])
        result['width'] = 16
        result['height'] = 9#videoitem.get('title','')
        result['play_addr'] = "https://api.tvcbook.com/video/tvindownload/{}".format(vid)
        result['author'] = videoitem.get('user',{}).get('name','')
        result['cover'] = videoitem.get('cover_url','')
        result['desc'] = videoitem.get('introduction','')
        result['upload_ts'] = time.time()
        result['from'] = 'tvcbook'
        return result


if __name__ == '__main__':
    import asyncio
    import aiohttp
    from pprint import pprint

    "https://www.tvcbook.com/showVideo.html?vid=544444"


    async def test():
        async with aiohttp.ClientSession() as session_:
            return await entrance(
                "https://www.tvcbook.com/showVideo.html?vid=748919",session_)


    loop = asyncio.get_event_loop()
    pprint(loop.run_until_complete(test()))