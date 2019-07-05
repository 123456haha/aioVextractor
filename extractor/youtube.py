#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 2019/6/20
# IDE: PyCharm

import jmespath
import traceback
import ujson as json
from extractor import common
from aioVextractor import config
from scrapy import Selector
from aioVextractor.utils.exception import exception
import asyncio

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


async def extract_author(webpage_url, session, chance_left=config.RETRY):
    try:
        headers = {
            'authority': 'www.youtube.com',
            'cache-control': 'max-age=0',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.157 Safari/537.36',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'zh-CN,zh;q=0.9',
        }

        async with session.get(webpage_url, headers=headers) as response:
            text = await response.text(encoding='utf8', errors='ignore')
    except exception:
        if chance_left != 1:
            return await extract_author(webpage_url=webpage_url, session=session, chance_left=chance_left - 1)
        else:
            return False
    except:
        traceback.print_exc()
        return False
    else:
        regex = 'window\["ytInitialData"\] = (.*?});'
        selector = Selector(text=text)
        try:
            ytInitialData = json.loads(selector.css('script').re_first(regex))
        except TypeError:
            return False
        else:
            author_avatar = jmespath.search('contents.twoColumnWatchNextResults.results.results.contents[1].videoSecondaryInfoRenderer.owner.videoOwnerRenderer.thumbnail.thumbnails[-1].url', ytInitialData)
        return {"author_avatar":author_avatar}


if __name__ == '__main__':
    import asyncio
    import aiohttp
    from pprint import pprint

    "https://www.youtube.com/watch?v=tofSaLB9kwE"


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
                webpage_url="https://www.youtube.com/watch?v=tofSaLB9kwE",
                session=session_)


    pprint(asyncio.run(test()))
