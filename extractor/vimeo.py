#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 2019/6/20
# IDE: PyCharm


import traceback
import asyncio
from aioVextractor.utils.requests_retry import RequestRetry
from aioVextractor. extractor import common
from aioVextractor.utils.user_agent import safari
from random import choice
from scrapy import Selector

async def entrance(webpage_url, session):
    try:
        gather_results = await asyncio.gather(*[
            common.extract_info(webpage_url=webpage_url),
            extract_author(webpage_url=webpage_url, session=session)
        ])
        if all(gather_results):
            return {**gather_results[0], **gather_results[1]}
        else:
            return False
    except:
        traceback.print_exc()
        return False


@RequestRetry
async def extract_author(webpage_url, session):
    headers = {
        'Connection': 'keep-alive',
        'Cache-Control': 'max-age=0',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': choice(safari),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        'Referer': 'https://vimeo.com/search?q=alita',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9',
    }
    async with session.get(webpage_url, headers=headers) as response:
        text = await response.text(encoding='utf8', errors='ignore')
        regex = '"portrait":\{"src":".*?",\s*"src_2x":"(.*?)"\},'
        selector = Selector(text=text)
        try:
            clip_page_config = selector.css('script').re_first(regex)
        except TypeError:
            return False
        else:
            avatar = clip_page_config.replace('\\/', '/')
        return {"author_avatar": avatar}


if __name__ == '__main__':
    import asyncio
    import aiohttp
    from pprint import pprint

    "https://vimeo.com/281493330"
    "https://vimeo.com/344361560"


    #
    # def test():
    #     return entrance(
    #         webpage_url="https://www.youtube.com/watch?v=tofSaLB9kwE")
    #
    #
    # pprint(test())
    #

    async def test():
        async with aiohttp.ClientSession() as session_:
            return await entrance(
                webpage_url="https://vimeo.com/344361560",
                session=session_)


    loop = asyncio.get_event_loop()
    pprint(loop.run_until_complete(test()))