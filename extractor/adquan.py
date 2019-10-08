#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 1/21/19
# IDE: PyCharm

# from aioVextractor.utils.user_agent import UserAgent
# from aioVextractor.player import tencent
# from aioVextractor.player import youku
# from aioVextractor.extractor import common
# from aioVextractor.utils.requests_retry import RequestRetry
# from random import choice
from scrapy.selector import Selector
import asyncio



# @RequestRetry
# async def entrance(webpage_url, session):
#     headers = {'Connection': 'keep-alive',
#                'Cache-Control': 'max-age=0',
#                'Upgrade-Insecure-Requests': '1',
#                'User-Agent': choice(UserAgent),
#                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
#                'Referer': webpage_url,
#                'Accept-Encoding': 'gzip, deflate',
#                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,ko;q=0.7'
#                }
#
#     cookies = {
#         # 'acw_tc': '7b39758315657641877568512ecc9b980ab48825a784f2d2f2a49251aef406',
#         # 'acw_sc__v3': '5d53aa62a7459ecd4730e4cbcaadd8c95378a283',
#         # 'SERVERID': '235be1bfd767f5d87ef3d43a3712e539|1565764194|1565764194',
#         'acw_sc__v2': '5d53aa5bb49e0baea03a2f7ea7c2988205474261',
#     }
#     async with session.get(webpage_url, headers=headers, cookies=cookies) as response:
#         text = await response.text(errors='ignore')
#         selector = Selector(text=text)
#
#         youku_urls = selector.css("iframe[src*='player.youku.com']::attr(src)").extract()
#         tencent_urls = selector.css('iframe[src*="v.qq"]::attr(src)').extract()
#         urls = youku_urls + tencent_urls
#         if not urls:
#             return False
#         results = await asyncio.gather(
#             *[allocate_url(iframe_url=iframe_url, session=session) for iframe_url in urls])
#         for ele in results:
#             if ele:
#                 ele['from'] = "广告门"
#                 ele['webpage_url'] = webpage_url
#         return results
#
#
# async def allocate_url(iframe_url, session):
#     if 'v.qq.com' in iframe_url:
#         return await tencent.entrance(iframe_url=iframe_url, session=session)
#     elif 'player.youku.com' in iframe_url:
#         return await youku.entrance(iframe_url=iframe_url, session=session)
#     else:
#         return await common.extract_info(webpage_url=iframe_url)
#
#
TEST_CASE = [
    "https://creative.adquan.com/show/286788",
    "https://creative.adquan.com/show/286778",
    "http://www.adquan.com/post-2-49507.html",
    "http://creative.adquan.com/show/49469",
    "http://creative.adquan.com/show/49415",
]

from aioVextractor.extractor.base_extractor import (BaseExtractor, validate, RequestRetry)


class Extractor(BaseExtractor):
    target_website = [
        "https://creative\.adquan\.com/show/\d{3,7}",
        "http://creative\.adquan\.com/show/\d{3,7}",
        "http://www\.adquan\.com/post-\d-\d{3,7}\.html$",
        "https://www\.adquan\.com/post-\d-\d{3,7}\.html$",
    ]

    def __init__(self, *args, **kwargs):
        BaseExtractor.__init__(self, *args, **kwargs)
        self.from_ = "adquan"

    @validate
    @RequestRetry
    async def entrance(self, webpage_url, session):
        headers = self.general_headers(user_agent=self.random_ua())
        headers['Referer'] = webpage_url
        cookies = {
            'acw_sc__v2': '5d53aa5bb49e0baea03a2f7ea7c2988205474261',
        }
        async with session.get(webpage_url, headers=headers, cookies=cookies) as response:
            text = await response.text(errors='ignore')
            selector = Selector(text=text)
            youku_urls = selector.css("iframe[src*='player.youku.com']::attr(src)").extract()
            tencent_urls = selector.css('iframe[src*="v.qq"]::attr(src)').extract()
            urls = youku_urls + tencent_urls
            if not urls:
                return False

            results = await asyncio.gather(
                *[self.extract_iframe(
                    iframe_url=iframe_url,
                    session=session
                ) for iframe_url in urls])
            for ele in results:
                if ele:
                    ele['from'] = self.from_
                    ele['webpage_url'] = webpage_url

            return results


if __name__ == '__main__':
    from pprint import pprint
    with Extractor() as extractor:
        res = extractor.sync_entrance(webpage_url="https://creative.adquan.com/show/286808")
        pprint(res)

    # import aiohttp
    # from pprint import pprint
    #
    #
    # async def test():
    #     async with aiohttp.ClientSession() as session_:
    #         return await entrance(
    #             webpage_url="https://creative.adquan.com/show/286808",
    #             session=session_)
    #
    #
    # loop = asyncio.get_event_loop()
    # pprint(loop.run_until_complete(test()))
