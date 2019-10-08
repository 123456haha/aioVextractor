#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 2019/6/20
# IDE: PyCharm

# from aioVextractor.utils.requests_retry import RequestRetry
# from aioVextractor.utils.user_agent import UserAgent
import time
# from random import choice
from scrapy.selector import Selector
import os
from urllib.parse import urlparse
import jmespath
import asyncio
import platform
if platform.system() in {"Linux", "Darwin"}:
    import ujson as json
else:
    import json

# @RequestRetry
# async def entrance(webpage_url, session):
#     if 'code' in webpage_url.lower():  ## old version http://www.tvcf.co.kr/YCf/V.asp?Code=A000363280
#         ParseResult = urlparse(webpage_url)
#         try:
#             code = ParseResult.query.split('=')[1]
#         except:
#             return False
#         else:
#             headers = {'User-Agent': choice(UserAgent),
#                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#                        'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
#                        'Connection': 'keep-alive',
#                        'Upgrade-Insecure-Requests': '1',
#                        'Cache-Control': 'max-age=0'}
#             params = {'Code': code}
#             async with session.get('http://www.tvcf.co.kr/YCf/V.asp', headers=headers, params=params) as response:
#                 response_text = await response.text(encoding='utf8', errors='ignore')
#                 result = dict()
#                 result['webpage_url'] = webpage_url
#                 result['from'] = "tvcf"
#                 result = await extract_old(response_text, code, result=result)
#                 return result
#     else:  ## new version https://v.tvcf.co.kr/728764
#         try:
#             idx = os.path.split(webpage_url)[-1]
#         except IndexError:
#             return False
#         else:
#             result = dict()
#             headers = {'Authorization': 'Bearer null',
#                        'Accept-Encoding': 'gzip, deflate, br',
#                        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,ko;q=0.7',
#                        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36',
#                        'Accept': 'application/json, text/plain, */*',
#                        'Referer': webpage_url,  ## https://v.tvcf.co.kr/738572
#                        'Connection': 'keep-alive'}
#             api = f'https://play.tvcf.co.kr/rest/api/player/init/{idx}'
#             async with session.get(api, headers=headers) as r_code:
#                 response_text = await r_code.text()
#                 r_code_json = json.loads(response_text)
#                 code = jmespath.search('video.code', r_code_json)
#                 result['from'] = "tvcf"
#                 result['duration'] = jmespath.search('video.duration', r_code_json)
#                 result['width'] = jmespath.search('video.width', r_code_json)
#                 result['height'] = jmespath.search('video.height', r_code_json)
#                 result['webpage_url'] = webpage_url
#                 result['vid'] = code
#                 result['cover'] = jmespath.search('video.cut', r_code_json)
#                 result['title'] = jmespath.search('video.title', r_code_json)
#                 result['description'] = jmespath.search('video.copy', r_code_json)
#                 fn = os.path.split(result['cover'])[-1].split('.')[0]
#                 fn_high_quality = fn + "_720p"
#                 play_addr_high_quality = f"http://media.tvcf.co.kr/Service/VStream/VideoStreamer.ashx?fn={fn_high_quality}.mp4"
#                 # play_addr = f"http://media.tvcf.co.kr/Service/VStream/VideoStreamer.ashx?fn={fn}.mp4"
#                 result['play_addr'] = play_addr_high_quality
#                 try:
#                     upload_date = jmespath.search('video.onair', r_code_json)
#                     result['upload_ts'] = int(
#                         time.mktime(time.strptime(upload_date, '%Y%m%d'))) if upload_date else None
#                 except:
#                     result['upload_ts'] = None
#                 result['rating'] = jmespath.search('evaluate.value', r_code_json)
#                 return await extract_new(session=session, result=result, idx=idx)
#
#
# async def extract_old(response, code, result):
#     selector = Selector(text=response)
#     title = selector.css('.player_title::text').extract_first()
#     result['vid'] = code
#     result['comment_count'] = selector.css('#replyAreaTab span span::text').extract_first()
#     result['cover'] = selector.css('.hidden link::attr(href)').extract_first()
#     create_time = selector.css('.onair::text').extract_first()
#     result['upload_ts'] = int(time.mktime(time.strptime(create_time, '%Y-%m-%d'))) if create_time else None
#     result['rating'] = selector.css('#scoreArea strong').re_first("\d{1,5}")
#     result['title'] = title.strip() if title else title
#     result['tag'] = selector.css('.tag::text').extract()
#     try:
#         fn = os.path.split(result['cover'])[-1].split('.')[0]
#     except TypeError:
#         return False
#     else:
#         fn_high_quality = fn + "_720p"
#         play_addr_high_quality = f"http://media.tvcf.co.kr/Service/VStream/VideoStreamer.ashx?fn={fn_high_quality}.mp4"
#         # play_addr = f"http://media.tvcf.co.kr/Service/VStream/VideoStreamer.ashx?fn={fn}.mp4"
#         result['play_addr'] = play_addr_high_quality
#         return result
#
#
# async def extract_new(session, result, idx):
#     """
#     :param session:
#     :param result:
#     :param idx:
#     :return:
#     """
#     result['title'], result['tag'], result['comment_count'] = await asyncio.gather(
#         *[get_title(session=session, idx=idx),
#           get_tags(session=session, idx=idx),
#           get_comment_num(session=session, idx=idx),
#           ])
#     return result
#
#
# # def get_ext(url_):
# #     """Return the filename extension from url, or ''."""
# #     if url_ is None:
# #         return False
# #     parsed = urlparse(url_)
# #     root, ext_ = splitext(parsed.query)
# #     ext = ext_[1:]  # or ext[1:] if you don't want the leading '.'
# #     ## ext = 'jpeg@80w_80h_1e_1c'
# #     return ext.split('@')[0]
#
#
# @RequestRetry(default_exception_return=[],
#               default_other_exception_return=[])
# async def get_tags(session, idx):
#     headers = {
#         'Authorization': 'Bearer null',
#         'Accept-Encoding': 'gzip, deflate, br',
#         'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
#         'User-Agent': choice(UserAgent),
#         'Accept': 'application/json, text/plain, */*',
#         'Referer': f'https://play.tvcf.co.kr/{idx}',
#         'Connection': 'keep-alive',
#     }
#     async  with session.get(f'https://play.tvcf.co.kr/rest/api/player/tag/{idx}', headers=headers) as response:
#         response_text = await response.text()
#         response_json = json.loads(response_text)
#         return response_json
#
#
# @RequestRetry(default_exception_return='',
#               default_other_exception_return='')
# async def get_title(session, idx):
#     headers = {
#         'Authorization': 'Bearer null',
#         'Accept-Encoding': 'gzip, deflate, br',
#         'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
#         'User-Agent': choice(UserAgent),
#         'Accept': 'application/json, text/plain, */*',
#         'Referer': f'https://play.tvcf.co.kr/{idx}',
#         'Connection': 'keep-alive',
#     }
#     async with session.get(f'https://play.tvcf.co.kr/rest/api/player/init2/{idx}', headers=headers) as response:
#         response_text = await response.text()
#         response_json = json.loads(response_text)
#         title = jmespath.search('search.list[0].[title, chapter]', response_json)
#         try:
#             title = ':'.join(title)
#         except TypeError:  ## TypeError: sequence item 1: expected str instance, NoneType found
#             title = title[0]
#         finally:
#             return title
#
#
# @RequestRetry
# async def get_comment_num(idx, session):
#     headers = {'Authorization': 'Bearer null',
#                'Accept-Encoding': 'gzip, deflate, br',
#                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
#                'User-Agent': choice(UserAgent),
#                'Accept': 'application/json, text/plain, */*'}
#     params = {'skip': '0',
#               'take': '5'}
#     url = f'https://play.tvcf.co.kr/rest/api/player/ReplyMore/{idx}'
#     async with session.get(url, headers=headers, params=params) as resp:
#         html = await resp.text(encoding='utf-8')
#         try:
#             data = json.loads(html)
#             return data.get('total', 0)
#         except:
#             return None



TEST_CASE = [
    "http://www.tvcf.co.kr/YCf/V.asp?Code=A000363280",
    "https://play.tvcf.co.kr/750556",
    "https://play.tvcf.co.kr/755843",
]
from aioVextractor.extractor.base_extractor import (BaseExtractor, validate, RequestRetry)


class Extractor(BaseExtractor):
    target_website = [
        "www\.tvcf\.co\.kr/YCF/V.asp\?Code=\w{7,15}",
        "https://play\.tvcf\.co\.kr/\d{3,10}",
    ]

    def __init__(self, *args, **kwargs):
        BaseExtractor.__init__(self, *args, **kwargs)
        self.from_ = "tvcf"

    @validate
    @RequestRetry
    async def entrance(self, webpage_url, session):
        if 'code' in webpage_url.lower():  ## old version http://www.tvcf.co.kr/YCf/V.asp?Code=A000363280
            ParseResult = urlparse(webpage_url)
            try:
                code = ParseResult.query.split('=')[1]
            except:
                return False
            else:
                headers = self.general_headers(user_agent=self.random_ua())
                params = {'Code': code}
                async with session.get('http://www.tvcf.co.kr/YCf/V.asp', headers=headers, params=params) as response:
                    response_text = await response.text(encoding='utf8', errors='ignore')
                    result = dict()
                    result['webpage_url'] = webpage_url
                    result['from'] = self.from_
                    result = await self.extract_old(response_text, code, result=result)
                    return result
        else:  ## new version https://v.tvcf.co.kr/728764
            try:
                idx = os.path.split(webpage_url)[-1]
            except IndexError:
                return False
            else:
                result = dict()
                headers = {'Authorization': 'Bearer null',
                           'Accept-Encoding': 'gzip, deflate, br',
                           'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,ko;q=0.7',
                           'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36',
                           'Accept': 'application/json, text/plain, */*',
                           'Referer': webpage_url,  ## https://v.tvcf.co.kr/738572
                           'Connection': 'keep-alive'}
                api = f'https://play.tvcf.co.kr/rest/api/player/init/{idx}'
                async with session.get(api, headers=headers) as r_code:
                    response_text = await r_code.text()
                    # print(f"response_text: {response_text}")
                    r_code_json = json.loads(response_text)
                    code = jmespath.search('video.code', r_code_json)
                    result['from'] = self.from_
                    result['duration'] = jmespath.search('video.duration', r_code_json)
                    result['width'] = jmespath.search('video.width', r_code_json)
                    result['height'] = jmespath.search('video.height', r_code_json)
                    result['webpage_url'] = webpage_url
                    result['vid'] = code
                    result['cover'] = jmespath.search('video.cut', r_code_json)
                    result['title'] = jmespath.search('video.title', r_code_json)
                    result['description'] = jmespath.search('video.copy', r_code_json)
                    fn = os.path.split(result['cover'])[-1].split('.')[0]
                    fn_high_quality = fn + "_720p"
                    play_addr_high_quality = f"http://media.tvcf.co.kr/Service/VStream/VideoStreamer.ashx?fn={fn_high_quality}.mp4"
                    # play_addr = f"http://media.tvcf.co.kr/Service/VStream/VideoStreamer.ashx?fn={fn}.mp4"
                    result['play_addr'] = play_addr_high_quality
                    try:
                        upload_date = jmespath.search('video.onair', r_code_json)
                        result['upload_ts'] = int(
                            time.mktime(time.strptime(upload_date, '%Y%m%d'))) \
                            if upload_date else None
                    except:
                        result['upload_ts'] = None
                    result['rating'] = jmespath.search('evaluate.value', r_code_json)
                    return await self.extract_new(session=session, result=result, idx=idx)

    @staticmethod
    async def extract_old(response, code, result):
        selector = Selector(text=response)
        title = selector.css('.player_title::text').extract_first()
        result['vid'] = code
        result['comment_count'] = selector.css('#replyAreaTab span span::text').extract_first()
        result['cover'] = selector.css('.hidden link::attr(href)').extract_first()
        create_time = selector.css('.onair::text').extract_first()
        result['upload_ts'] = int(time.mktime(time.strptime(create_time, '%Y-%m-%d'))) if create_time else None
        result['rating'] = selector.css('#scoreArea strong').re_first("\d{1,5}")
        result['title'] = title.strip() if title else title
        result['tag'] = selector.css('.tag::text').extract()
        try:
            fn = os.path.split(result['cover'])[-1].split('.')[0]
        except TypeError:
            return False
        else:
            fn_high_quality = fn + "_720p"
            play_addr_high_quality = f"http://media.tvcf.co.kr/Service/VStream/VideoStreamer.ashx?fn={fn_high_quality}.mp4"
            # play_addr = f"http://media.tvcf.co.kr/Service/VStream/VideoStreamer.ashx?fn={fn}.mp4"
            result['play_addr'] = play_addr_high_quality
            return result

    async def extract_new(self, session, result, idx):
        result['title'], result['tag'], result['comment_count'] = await asyncio.gather(
            *[self.get_title(session=session, idx=idx),
              self.get_tags(session=session, idx=idx),
              self.get_comment_num(session=session, idx=idx),
              ])
        return result

    # def get_ext(url_):
    #     """Return the filename extension from url, or ''."""
    #     if url_ is None:
    #         return False
    #     parsed = urlparse(url_)
    #     root, ext_ = splitext(parsed.query)
    #     ext = ext_[1:]  # or ext[1:] if you don't want the leading '.'
    #     ## ext = 'jpeg@80w_80h_1e_1c'
    #     return ext.split('@')[0]

    @RequestRetry(default_exception_return=[],
                  default_other_exception_return=[])
    async def get_tags(self, session, idx):
        headers = {
            'Authorization': 'Bearer null',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'User-Agent': self.random_ua(),
            'Accept': 'application/json, text/plain, */*',
            'Referer': f'https://play.tvcf.co.kr/{idx}',
            'Connection': 'keep-alive',
        }
        async  with session.get(f'https://play.tvcf.co.kr/rest/api/player/tag/{idx}', headers=headers) as response:
            response_text = await response.text()
            response_json = json.loads(response_text)
            return response_json

    @RequestRetry(default_exception_return='',
                  default_other_exception_return='')
    async def get_title(self, session, idx):
        headers = {
            'Authorization': 'Bearer null',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'User-Agent': self.random_ua(),
            'Accept': 'application/json, text/plain, */*',
            'Referer': f'https://play.tvcf.co.kr/{idx}',
            'Connection': 'keep-alive',
        }
        async with session.get(f'https://play.tvcf.co.kr/rest/api/player/init2/{idx}', headers=headers) as response:
            response_text = await response.text()
            response_json = json.loads(response_text)
            title = jmespath.search('search.list[0].[title, chapter]', response_json)
            try:
                title = ':'.join(title)
            except TypeError:  ## TypeError: sequence item 1: expected str instance, NoneType found
                title = title[0]
            finally:
                return title

    @RequestRetry
    async def get_comment_num(self, idx, session):
        headers = {'Authorization': 'Bearer null',
                   'Accept-Encoding': 'gzip, deflate, br',
                   'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                   'User-Agent': self.random_ua(),
                   'Accept': 'application/json, text/plain, */*'}
        params = {'skip': '0',
                  'take': '5'}
        url = f'https://play.tvcf.co.kr/rest/api/player/ReplyMore/{idx}'
        async with session.get(url, headers=headers, params=params) as resp:
            html = await resp.text(encoding='utf-8')
            try:
                data = json.loads(html)
                return data.get('total', 0)
            except:
                return None


if __name__ == '__main__':
    from pprint import pprint
    with Extractor() as extractor:
        res = extractor.sync_entrance(webpage_url="https://play.tvcf.co.kr/755843")
        pprint(res)

    # import aiohttp
    # from pprint import pprint
    #
    #
    # async def test():
    #     async with aiohttp.ClientSession() as session_:
    #         return await entrance(webpage_url="https://play.tvcf.co.kr/755843",
    #                               session=session_)
    #
    #
    # loop = asyncio.get_event_loop()
    # pprint(loop.run_until_complete(test()))
