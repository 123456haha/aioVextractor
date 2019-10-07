#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 10/07/19
# IDE: PyCharm

# import asyncio
# import aiohttp, json ,time
# from aioVextractor.utils.requests_retry import *
# import emoji
# import re

# @RequestRetry
# async def ExtractOne(webpage_url, session):
#     headers = {
#         "Host":"www.pinterest.com",
#         "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36"
#     }
#     async with session.get(webpage_url, verify_ssl=False,headers=headers) as resp:
#         html = await resp.text()
#         try:
#             jsonstr = re.findall("<script type='application/json' id='jsInit1'>(.*?)</script>",html)
#             if not jsonstr:
#                 return []
#             jsondata = json.loads(jsonstr[0])
#             # print(jsondata)
#             resourceDataCache = jsondata.get("resourceDataCache")
#             video = resourceDataCache[0].get("data")
#             v = video.get("videos")
#             item = dict()
#             item['vid'] = video.get('id')
#             item['webpage_url'] = "https://www.pinterest.com/pin/"+video.get('id')
#             iname = ["orig","736x","564x","474x","600x315"]
#             for inn in iname:
#                 if item.get("cover"):
#                     break
#                 item['cover'] = video.get("images",{}).get(inn,{}).get("url")
#             pn = ["V_720P","V_HLSV3_MOBILE","V_HLSV3_WEB","V_HLSV4"]
#             for n in pn:
#                 if item.get("duration"):
#                     break
#                 item['play_addr'] = v.get("video_list",{}).get(n,{}).get("url")
#                 if not item.get('cover'):
#                     item['cover'] = v.get("video_list",{}).get(n,{}).get("thumbnail")
#                 item['duration'] = v.get("video_list",{}).get(n,{}).get("duration")//1000
#                 item['width'] = v.get("video_list",{}).get(n,{}).get("width")
#                 item['height'] = v.get("video_list",{}).get(n,{}).get("height")
#             item['title'] = video.get("grid_title")
#             rich_summary = video.get("rich_summary",{})
#             if rich_summary:
#                 item['description'] = emoji.demojize(rich_summary.get("display_description"))
#             else:
#                 item['description'] = ''
#             if not item['description']:
#                 item['description'] = video.get("description")
#             item['ad_link'] = video.get("tracked_link")
#             pinner = video.get("pinner")
#             if pinner:
#                 item['author'] = pinner.get("full_name")
#                 item['author_id'] = pinner.get("id")
#                 item['author_avatar'] = pinner.get("image_large_url")
#                 if not item['author_avatar']:
#                     item['author_avatar'] = pinner.get("image_small_url")
#                 item['author_url'] = webpage_url
#             item['comment_count'] = video.get("comment_count",0)
#             item['from'] ='pinterest'
#             return item
#         except Exception as e:
#             import traceback
#             print(traceback.format_exc())
#             print(e)
#             return None
#
# @RequestRetry
# async def entrance(webpage_url, session,retry=0):
#     if retry>=5:
#         return None
#     videolist = await ExtractOne(webpage_url,session)
#     if not videolist:
#         return await entrance(webpage_url,session,retry=retry+1)
#     return videolist


TEST_CASE = [
    "https://www.pinterest.com/pin/457256168416688731",
]

from aioVextractor.extractor.base_extractor import (BaseExtractor, validate, RequestRetry)
import jmespath
import platform
from scrapy import Selector

if platform.system() in {"Linux", "Darwin"}:
    import ujson as json
else:
    import json

class Extractor(BaseExtractor):
    target_website = [
        "www\.pinterest\.com/pin/\d{15,23}",
    ]

    def __init__(self, *args, **kwargs):
        BaseExtractor.__init__(self, *args, **kwargs)
        self.from_ = "pinterest"

    @validate
    @RequestRetry
    async def entrance(self, webpage_url, session):
        headers = self.general_headers(user_agent=self.random_ua())
        headers["Host"] = "www.pinterest.com"
        async with session.get(webpage_url, verify_ssl=False, headers=headers) as resp:
            html = await resp.text()
            selector = Selector(text=html)
            jsonstr = selector.css("#initial-state::text").extract_first()
            if not jsonstr:
                return None
            jsondata = json.loads(jsonstr)
            item = dict()
            data = jmespath.search("resourceResponses[0].response.data", jsondata)
            videos = jmespath.search("videos", data)
            item['vid'] = data.get('id')
            item['webpage_url'] = "https://www.pinterest.com/pin/" + item['vid']
            iname = ["orig", "736x", "564x", "474x", "600x315"]
            for inn in iname:
                if item.get("cover"):
                    break
                item['cover'] = jmespath.search(f"images.{inn}.url", data)
            pn = ["V_720P", "V_HLSV3_MOBILE", "V_HLSV3_WEB", "V_HLSV4"]
            for n in pn:
                if item.get("duration"):
                    break
                item['play_addr'] = jmespath.search(f"video_list.{n}.url", videos)
                if not item.get('cover'):
                    item['cover'] = jmespath.search(f"video_list.{n}.thumbnail", videos)
                item['duration'] = jmespath.search(f"video_list.{n}.duration", videos) // 1000
                item['width'] = jmespath.search(f"video_list.{n}.width", videos)
                item['height'] = jmespath.search(f"video_list.{n}.height", videos)

            item['title'] = data.get("grid_title")
            item['description'] = jmespath.search("rich_summary.display_description", data)
            item['description'] = data.get("description") if not item['description'] else None
            item['ad_link'] = data.get("tracked_link")
            pinner = data.get("pinner")
            if pinner:
                item['author'] = pinner.get("full_name")
                item['author_id'] = pinner.get("id")
                item['author_avatar'] = pinner.get("image_large_url")
                item['author_avatar'] = pinner.get("image_small_url") if not item['author_avatar'] else None
                # item['author_url'] = webpage_url
            item['comment_count'] = data.get("comment_count", 0)
            item['from'] = self.from_
            return item

if __name__ == '__main__':
    from pprint import pprint
    with Extractor() as extractor:
        res = extractor.sync_entrance(webpage_url="https://www.pinterest.com/pin/785667097477427570/?nic=1")
        pprint(res)




    # async def test():
    #     async with aiohttp.ClientSession() as session_:
    #         return await entrance("https://www.pinterest.com/pin/457256168416688731", session_)
    #
    #
    # loop = asyncio.get_event_loop()
    # res = loop.run_until_complete(test())
    # print(res)
