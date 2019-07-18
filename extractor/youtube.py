#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 2019/6/20
# IDE: PyCharm

import jmespath
import traceback
import ujson as json
from aioVextractor.extractor import common
from scrapy import Selector
from aioVextractor.utils.requests_retry import RequestRetry
import asyncio


async def entrance(webpage_url, session):
    webpage_url = webpage_url.split('&')[0]
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
    headers = {'authority': 'www.youtube.com',
               'upgrade-insecure-requests': '1',
               'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36',
               'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
               'accept-encoding': 'gzip, deflate, br',
               'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
               }

    async with session.get(webpage_url, headers=headers) as response:
        text = await response.text(encoding='utf8', errors='ignore')
        try:
            selector = Selector(text=text)
            try:
                ytInitialData = json.loads(json.
                                           loads(selector.
                                                 css('script').
                                                 re_first('window\["ytInitialData"] = JSON.parse\((.*?)\);')))
            except TypeError:
                ytInitialData = json.loads(selector.css('script').re_first(
                    'window\["ytInitialData"\] = ({[\s|\S]*?});[\s|\S]*?window\["ytInitialPlayerResponse"\]'))
        except TypeError:
            traceback.print_exc()
            return False
        else:
            author_avatar = jmespath.search('contents.'
                                            'twoColumnWatchNextResults.'
                                            'results.'
                                            'results.'
                                            'contents[1].'
                                            'videoSecondaryInfoRenderer.'
                                            'owner.'
                                            'videoOwnerRenderer.'
                                            'thumbnail.'
                                            'thumbnails[-1].'
                                            'url',
                ytInitialData)

            author_avatar = 'http:' + author_avatar if (author_avatar and author_avatar.startswith('//')) else None
        return {"author_avatar": author_avatar,
                'from' : "youtube"
        }


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
    "https://www.youtube.com/watch?v=tofSaLB9kwE"
    "https://www.youtube.com/watch?v=pgN-vvVVxMA"
    "https://www.youtube.com/watch?v=iAeYPfrXwk4"


    async def test():
        async with aiohttp.ClientSession() as session_:
            return await entrance(
                webpage_url="https://www.youtube.com/watch?v=iAeYPfrXwk4",
                session=session_)


    loop = asyncio.get_event_loop()
    pprint(loop.run_until_complete(test()))