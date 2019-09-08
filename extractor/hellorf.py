#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 1/28/19
# IDE: PyCharm

import ujson as json
import jmespath
from aioVextractor.utils.user_agent import UserAgent
from aioVextractor.utils.requests_retry import RequestRetry
from random import choice
from scrapy.selector import Selector
import asyncio


@RequestRetry
async def entrance(webpage_url, session):
    headers = {'Connection': 'keep-alive',
               'Upgrade-Insecure-Requests': '1',
               'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.109 Safari/537.36',
               'Accept': choice(UserAgent),
               'Accept-Encoding': 'gzip, deflate, br',
               'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,ko;q=0.7'}
    async with session.get(webpage_url, headers=headers) as response:
        response_text = await response.text(encoding='utf8', errors='ignore')
        print(response_text)
        selector = Selector(text=response_text)
        result = dict()
        video_json = json.loads(selector.css('script::text').re_first('__NEXT_DATA__ = (\{[\s|\S]*\});'))
        result['author'] = jmespath.search('props.pageProps.initialProps.detail.contributor.display_name', video_json)
        result['play_addr'] = jmespath.search('props.pageProps.initialProps.detail.video.preview_mp4_url', video_json)
        result['title'] = jmespath.search('props.pageProps.initialProps.detail.video.description', video_json)
        result['vid'] = jmespath.search('props.pageProps.initialProps.detail.video.id', video_json)
        video_category = jmespath.search('props.pageProps.initialProps.detail.video.categories[].name', video_json)
        result['category'] = ','.join(video_category)
        result['cover'] = jmespath.search('props.pageProps.initialProps.detail.video.preview_jpg_url', video_json)
        result['duration'] = jmespath.search('props.pageProps.initialProps.detail.video.duration', video_json)
        result['tag'] = jmespath.search('props.pageProps.initialProps.detail.video.keywords', video_json)
        result['from'] = "广告门"
        result['webpage_url'] = webpage_url
        return result


TEST_CASE = [
    "https://www.hellorf.com/video/show/15148543",
    "https://www.hellorf.com/video/show/11995691",
]
if __name__ == '__main__':
    import aiohttp
    from pprint import pprint


    async def test():
        async with aiohttp.ClientSession() as session_:
            return await entrance(
                webpage_url="https://www.hellorf.com/video/show/15148543",
                session=session_)


    loop = asyncio.get_event_loop()
    pprint(loop.run_until_complete(test()))
