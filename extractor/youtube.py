#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 2019/6/20
# IDE: PyCharm

import jmespath
import traceback
# from aioVextractor.extractor import common
from scrapy import Selector
# from aioVextractor.utils.requests_retry import RequestRetry
import asyncio
import platform

if platform.system() in {"Linux", "Darwin"}:
    import ujson as json
else:
    import json


# async def entrance(webpage_url, session):
#     webpage_url = webpage_url.split('&')[0]
#     try:
#         gather_results = await asyncio.gather(*[
#             common.extract_info(webpage_url=webpage_url),
#             extract_author(webpage_url=webpage_url, session=session)
#         ])
#         if all(gather_results):
#             return {**gather_results[0], **gather_results[1]}
#         else:
#             return False
#     except:
#         traceback.print_exc()
#         return False
#
#
# @RequestRetry
# async def extract_author(webpage_url, session):
#     headers = {'authority': 'www.youtube.com',
#                'upgrade-insecure-requests': '1',
#                'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36',
#                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
#                'accept-encoding': 'gzip, deflate, br',
#                'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
#                }
#
#     async with session.get(webpage_url, headers=headers) as response:
#         text = await response.text(encoding='utf8', errors='ignore')
#         try:
#             selector = Selector(text=text)
#             try:
#                 ytInitialData = json.loads(json.
#                                            loads(selector.
#                                                  css('script').
#                                                  re_first('window\["ytInitialData"] = JSON.parse\((.*?)\);')))
#             except TypeError:
#                 ytInitialData = json.loads(selector.css('script').re_first(
#                     'window\["ytInitialData"\] = ({[\s|\S]*?});[\s|\S]*?window\["ytInitialPlayerResponse"\]'))
#         except TypeError:
#             traceback.print_exc()
#             return False
#         else:
#             author_avatar = jmespath.search('contents.'
#                                             'twoColumnWatchNextResults.'
#                                             'results.'
#                                             'results.'
#                                             'contents[1].'
#                                             'videoSecondaryInfoRenderer.'
#                                             'owner.'
#                                             'videoOwnerRenderer.'
#                                             'thumbnail.'
#                                             'thumbnails[-1].'
#                                             'url',
#                                             ytInitialData)
#
#             author_avatar = 'http:' + author_avatar if (author_avatar and author_avatar.startswith('//')) else None
#         return {"author_avatar": author_avatar,
#                 'from': "youtube"
#                 }


TEST_CASE = [
    "https://www.youtube.com/watch?v=tofSaLB9kwE",
    "https://www.youtube.com/watch?v=pgN-vvVVxMA",
    "https://www.youtube.com/watch?v=iAeYPfrXwk4",
    "https://www.youtube.com/watch?v=jDO2YPGv9fw&list=PLNHZSfaJJc25zChky2JaM99ba8I2bVUza&index=15&t=0s",
    "https://www.youtube.com/watch?v=JGwWNGJdvx8&list=PLDcnymzs18LU4Kexrs91TVdfnplU3I5zs&index=28&t=0s",
]

from aioVextractor.extractor.base_extractor import (BaseExtractor, validate, RequestRetry)


class Extractor(BaseExtractor):
    target_website = [
        "www\.youtube\.com/watch\?v=[\w-]{5,15}"
    ]

    def __init__(self, *args, **kwargs):
        BaseExtractor.__init__(self, *args, **kwargs)
        self.from_ = "youtube"

    @validate
    @RequestRetry
    async def entrance(self, webpage_url, session):

        try:
            gather_results = await asyncio.gather(*[
                self.extract_info(webpage_url=webpage_url),
                self.extract_author(webpage_url=webpage_url, session=session)
            ])
            if all(gather_results):
                return {**gather_results[0], **gather_results[1]}
            else:
                return False
        except:
            traceback.print_exc()
            return False

    @RequestRetry
    async def extract_author(self, webpage_url, session):
        headers = {'authority': 'www.youtube.com',
                   'upgrade-insecure-requests': '1',
                   'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36',
                   'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
                   'accept-encoding': 'gzip, deflate, br',
                   'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
                   }
        async with session.get(webpage_url, headers=headers) as response:
            text = await response.text(encoding='utf8', errors='ignore')
            selector = Selector(text=text)
            try:
                ytInitialData = json.loads(json.
                                           loads(selector.
                                                 css('script').
                                                 re_first('window\["ytInitialData"] = JSON.parse\((.*?)\);')))
            except TypeError:
                ytInitialData = json.loads(selector.css('script').re_first(
                    'window\["ytInitialData"\] = ({[\s|\S]*?});[\s|\S]*?window\["ytInitialPlayerResponse"\]'))
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
            return {
                "author_avatar": author_avatar,
                'from': self.from_
            }


if __name__ == '__main__':
    from pprint import pprint

    with Extractor() as extractor:
        # print(extractor.target_website)
        ress = extractor.sync_entrance(webpage_url="https://www.youtube.com/watch?v=tofSaLB9kwE")
        pprint(ress)

    # import aiohttp
    # from pprint import pprint
    #
    #
    # async def test():
    #     async with aiohttp.ClientSession() as session_:
    #         return await entrance(
    #             webpage_url="https://www.youtube.com/watch?v=JGwWNGJdvx8&list=PLDcnymzs18LU4Kexrs91TVdfnplU3I5zs&index=28&t=0s",
    #             session=session_)
    #
    #
    # loop = asyncio.get_event_loop()
    # pprint(loop.run_until_complete(test()))
