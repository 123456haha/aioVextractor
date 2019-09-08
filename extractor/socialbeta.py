#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 1/21/19
# IDE: PyCharm

from aioVextractor.utils.requests_retry import RequestRetry
from random import choice
from aioVextractor.utils.user_agent import UserAgent
from aioVextractor.player import tencent
from aioVextractor.player import youku
from aioVextractor.extractor import common
from scrapy.selector import Selector
import asyncio


@RequestRetry
async def entrance(webpage_url, session):
    headers = {'Connection': 'keep-alive',
               'Cache-Control': 'max-age=0',
               'Upgrade-Insecure-Requests': '1',
               'User-Agent': choice(UserAgent),
               'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
               'Referer': webpage_url,
               'Accept-Encoding': 'gzip, deflate, br',
               'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,ko;q=0.7'}
    async with session.get(webpage_url, headers=headers) as response:
        response_text = await response.text(encoding='utf8', errors='ignore')
        selector = Selector(text=response_text)
        urls = selector.css('iframe[src*="v.qq"]::attr(src)').extract()
        if not urls:
            return False
        results = await asyncio.gather(
            *[allocate_url(iframe_url=iframe_url, session=session) for iframe_url in urls])
        for ele in results:
            if ele:
                ele['from'] = "socialbeta"
                ele['webpage_url'] = webpage_url
        return results


async def allocate_url(iframe_url, session):
    if 'v.qq.com' in iframe_url:
        return await tencent.entrance(iframe_url=iframe_url, session=session)
    elif 'player.youku.com' in iframe_url:
        return await youku.entrance(iframe_url=iframe_url, session=session)
    else:
        return await common.extract_info(webpage_url=iframe_url)


TEST_CASE = [
    "https://socialbeta.com/t/jiafangyifang-news-20190226",
    "https://socialbeta.com/t/case-collection-overseas-ad-about-superbowl-20190224",
]
if __name__ == '__main__':
    import aiohttp
    from pprint import pprint


    async def test():
        async with aiohttp.ClientSession() as session_:
            return await entrance(
                webpage_url="https://socialbeta.com/t/case-collection-overseas-ad-about-superbowl-20190224",
                session=session_)


    loop = asyncio.get_event_loop()
    pprint(loop.run_until_complete(test()))
