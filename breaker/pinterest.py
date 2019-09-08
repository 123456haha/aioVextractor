#!/usr/bin/env python
# -*- coding: utf-8 -*-
# IDE: PyCharm

import asyncio
import aiohttp
from ..utils.requests_retry import RequestRetry
import json, base64
import traceback
import emoji
import time


async def breakdown(webpage_url,
                    page=1,
                    params=None):
    """
    cursor is the current place of the video
    offset can only be the integer multiple of 10
    :return: list of title and cover
    """
    if "video_pins" not in webpage_url:
        return [], False, None
    conn = aiohttp.TCPConnector(ssl=False)
    async with aiohttp.ClientSession(connector=conn) as session:
        all_data = await extractUser(webpage_url, session, params)
        return all_data

@RequestRetry
async def extractUser(webpageurl, session, thisparams):
    userparm = webpageurl.split("/video_pins")[0].split("/")[-1]
    source_url = "/" + userparm + "/video_pins"
    _ = str(int(time.time() * 1000))
    if not thisparams:
        data = '{"options":{"isPrefetch":false,"exclude_add_pin_rep":true,"username":"' + userparm + '","field_set_key":"grid_item"},"context":{}}'
    else:
        data = thisparams['clickTrackingParams']
        data = str(base64.b64decode(data), 'utf-8')
        # data = json.loads(data)
    tagurl = "https://www.pinterest.com/_ngjs/resource/UserVideoPinsFeedResource/get/?source_url" + source_url + "&data=" + data + "&_=" + _
    all_data = []
    hasNext = False
    params = None
    async with session.get(tagurl, verify_ssl=False) as resp:
        jsondata = await resp.json()
        try:
            video_data = jsondata.get("resource_response", {}).get("data")
            for video in video_data:
                try:
                    v = video.get("videos")
                    item = dict()
                    item['from'] = 'pinterest'
                    item['vid'] = video.get('id')
                    item['webpage_url'] = "https://www.pinterest.com/pin/" + video.get('id')
                    item['playlist_url'] = webpageurl
                    iname = ["orig", "736x", "564x", "474x", "600x315"]
                    for inn in iname:
                        if item.get("cover"):
                            break
                        item['cover'] = item.get("images", {}).get(inn, {}).get("url")
                    pn = ["V_HLSV3_MOBILE", "V_HLSV3_WEB", "V_HLSV4"]
                    for n in pn:
                        if item.get("duration"):
                            break
                        item['play_addr'] = v.get("video_list", {}).get(n, {}).get("url")
                        if not item.get('cover'):
                            item['cover'] = v.get("video_list", {}).get(n, {}).get("thumbnail")
                        item['duration'] = v.get("video_list", {}).get(n, {}).get("duration") // 1000
                        item['width'] = v.get("video_list", {}).get(n, {}).get("width")
                        item['height'] = v.get("video_list", {}).get(n, {}).get("height")
                    item['title'] = video.get("grid_title")
                    rich_summary = video.get("rich_summary", {})
                    if rich_summary:
                        item['description'] = emoji.demojize(rich_summary.get("display_description"))
                        item['ad_link'] = rich_summary.get("url")
                    else:
                        item['description'] = ''
                    pinner = video.get("pinner")
                    if pinner:
                        item['author'] = pinner.get("full_name")
                        item['author_id'] = pinner.get("id")
                        item['author_avatar'] = pinner.get("image_large_url")
                        item['author_url'] = webpageurl
                    item['comment_count'] = video.get("comment_count", 0)
                    all_data.append(item)
                    bookmarks = jsondata.get("resource", {}).get("options", {}).get("bookmarks")
                    if not bookmarks or bookmarks[0] == '-end-':
                        hasNext = False
                    else:
                        resource = jsondata.get("resource", {}).get("options", {})
                        if resource:
                            hasNext = True
                            rrrdata = {
                                "options": resource, "context": {}
                            }
                            returnparams = json.dumps(rrrdata)
                            returnparams = base64.b64encode(returnparams.encode('utf-8'))
                            params = returnparams
                except Exception as e:
                    print("解析pinterest出错",e)
        except:
            traceback.print_exc()
            pass
    if params:
        return all_data, hasNext, {"continuation": "True", "clickTrackingParams": str(params, 'utf-8')}
    else:
        return all_data, hasNext, None


if __name__ == '__main__':
    from pprint import pprint


    # user = 'losangeles_eats'
    # tag = fetch_items(user)
    async def test():
        return await breakdown("https://www.pinterest.com/luvbridal/video_pins/")


    loop = asyncio.get_event_loop()
    res = loop.run_until_complete(test())
    pprint(res)
