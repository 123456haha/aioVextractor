#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 1/21/19
# IDE: PyCharm

from urllib.parse import urlparse
import jmespath
# from aioVextractor.utils.requests_retry import RequestRetry
# from random import choice
# from aioVextractor.utils.user_agent import UserAgent
from aioVextractor.player import youku
from aioVextractor.player import xinpianchang
from scrapy.selector import Selector
import asyncio
import platform

if platform.system() in {"Linux", "Darwin"}:
    import ujson as json
else:
    import json

# @RequestRetry
# async def entrance(webpage_url, session):
#     headers = {'Connection': 'keep-alive',
#                'Cache-Control': 'max-age=0',
#                'Upgrade-Insecure-Requests': '1',
#                'User-Agent': choice(UserAgent),
#                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
#                'Referer': 'http://creative.adquan.com/',
#                'Accept-Encoding': 'gzip, deflate',
#                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,ko;q=0.7'}
#     async with session.get(webpage_url, headers=headers) as response:
#         response_text = await response.text(encoding='utf8', errors='ignore')
#         selector = Selector(text=response_text)
#         xinpianchang_url = selector.css('.post-title a::attr(href)').extract()
#         openapi_url = selector.css('iframe[src*=openapi]::attr(src)').extract()
#         youku_url = list(map(lambda x: 'https://v.youku.com/v_show/id_{vid}'.format(vid=x),
#                              selector.css('script::text').re("vid: '([\s|\S]*?)'")))
#         urls = xinpianchang_url + openapi_url + youku_url
#         if not urls:
#             return False
#         results = await asyncio.gather(
#             *[allocate_url(url=url_,
#                            session=session,
#                            referer=webpage_url,
#                            selector=selector) for url_ in urls])
#
#         for ele in results:
#             if ele:
#                 ele['from'] = "场库"
#                 ele['webpage_url'] = webpage_url
#         return results
#
#
# async def allocate_url(url, session, referer=None, selector=None):
#     if 'openapi' in url:
#         return await extract_openapi_info(selector=selector, player_address=url,
#                                           referer=referer, session=session)
#     elif 'v.youku.com' in url:
#         return await youku.entrance(iframe_url=url, session=session)
#     else:
#         return await xinpianchang.entrance(webpage_url=url, session=session)
#
#
# @RequestRetry
# async def extract_openapi_info(selector, player_address, referer, session):
#     result = dict()
#     result['vid'] = urlparse(player_address).path.split('/')[2]
#     result['author'] = selector.css('.author::text').extract_first()
#     result['title'] = selector.css('meta[name*=application-name]::attr(content)').extract_first()
#     result['category'] = selector.css('.channel a::attr(title) ').extract_first()
#     result['description'] = selector.css('meta[name*=description]::attr(content)').extract_first()
#     tag = selector.css('meta[name*=keywords]::attr(content)').extract_first()
#     result['tag'] = tag.split(',') if tag else None
#     headers = {'authority': 'openapi-vtom.vmovier.com',
#                'upgrade-insecure-requests': '1',
#                'user-agent': choice(UserAgent),
#                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
#                'referer': referer,
#                'accept-encoding': 'gzip, deflate, br',
#                'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,ko;q=0.7'}
#     async with session.get(player_address, headers=headers) as player_response:
#         player_response_text = await player_response.text(encoding='utf8', errors='ignore')
#         player_selector = Selector(text=player_response_text)
#         result['cover'] = player_selector.css('#xpc_video::attr(poster)').extract_first()
#         video = json.loads(player_selector.css('script').re_first('var origins = (\[[\s|\S]*?\])'))
#         duration, result['play_addr'] = jmespath.search('max_by(@, &filesize).[duration, url]', video)
#         result['duration'] = int(duration / 1000) if duration else None
#         return result


TEST_CASE = [
    ## xpc player:
    "https://www.vmovier.com/55810?from=index_new_img",
    "https://www.vmovier.com/56000?from=index_new_img",
    ## youku player:
    "https://www.vmovier.com/56052?from=index_new_title",
    "https://www.vmovier.com/55952?from=index_new_img",
    "https://www.vmovier.com/55108",
]

from aioVextractor.extractor.base_extractor import (BaseExtractor, validate, RequestRetry)


class Extractor(BaseExtractor):
    target_website = [
        "www\.vmovier\.com/\d{2,8}",
    ]

    def __init__(self, *args, **kwargs):
        BaseExtractor.__init__(self, *args, **kwargs)
        self.from_ = "vmovier"

    @validate
    @RequestRetry
    async def entrance(self, webpage_url, session):
        headers = self.general_headers(user_agent=self.random_ua())
        headers['Referer'] = 'http://creative.adquan.com/'
        async with session.get(webpage_url, headers=headers) as response:
            response_text = await response.text(encoding='utf8', errors='ignore')
            selector = Selector(text=response_text)
            xinpianchang_url = selector.css('.post-title a::attr(href)').extract()
            openapi_url = selector.css('iframe[src*=openapi]::attr(src)').extract()
            youku_url = list(map(lambda x: 'https://v.youku.com/v_show/id_{vid}'.format(vid=x),
                                 selector.css('script::text').re("vid: '([\s|\S]*?)'")))
            urls = xinpianchang_url + openapi_url + youku_url

            if not urls:
                return False
            results = await asyncio.gather(
                *[self.allocate_url(url=url_,
                                    session=session,
                                    referer=webpage_url,
                                    selector=selector) for url_ in urls])

            for ele in results:
                if ele:
                    ele['from'] = self.from_
                    ele['webpage_url'] = webpage_url
            return results

    async def allocate_url(self, url, session, referer=None, selector=None):
        if 'openapi' in url:
            return await self.extract_openapi_info(selector=selector, player_address=url,
                                              referer=referer, session=session)
        elif 'v.youku.com' in url:
            return await youku.entrance(iframe_url=url, session=session)
        elif "xinpianchang" in url:
            return await xinpianchang.entrance(webpage_url=url, session=session)

    @RequestRetry
    async def extract_openapi_info(self, selector, player_address, referer, session):
        result = dict()
        result['vid'] = urlparse(player_address).path.split('/')[2]
        result['author'] = selector.css('.author::text').extract_first()
        result['title'] = selector.css('meta[name*=application-name]::attr(content)').extract_first()
        result['category'] = selector.css('.channel a::attr(title) ').extract_first()
        result['description'] = selector.css('meta[name*=description]::attr(content)').extract_first()
        tag = selector.css('meta[name*=keywords]::attr(content)').extract_first()
        result['tag'] = tag.split(',') if tag else None
        headers = self.general_headers(user_agent=self.random_ua())
        headers['referer'] = referer
        headers['authority'] = 'openapi-vtom.vmovier.com'
        async with session.get(player_address, headers=headers) as player_response:
            player_response_text = await player_response.text(encoding='utf8', errors='ignore')
            player_selector = Selector(text=player_response_text)
            result['cover'] = player_selector.css('#xpc_video::attr(poster)').extract_first()
            video = json.loads(player_selector.css('script').re_first('var origins = (\[[\s|\S]*?\])'))
            duration, result['play_addr'] = jmespath.search('max_by(@, &filesize).[duration, url]', video)
            result['duration'] = int(duration / 1000) if duration else None
            return result


if __name__ == '__main__':
    from pprint import pprint

    with Extractor() as extractor:
        res = extractor.sync_entrance(webpage_url="https://www.vmovier.com/56000?from=index_new_img")
        pprint(res)

    # import aiohttp
    # from pprint import pprint
    #
    #
    # async def test():
    #     async with aiohttp.ClientSession() as session_:
    #         return await entrance(
    #             webpage_url="https://www.vmovier.com/55108",
    #             session=session_)
    #
    #
    # loop = asyncio.get_event_loop()
    # pprint(loop.run_until_complete(test()))
