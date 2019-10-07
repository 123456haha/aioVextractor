#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 1/28/19
# IDE: PyCharm

import jmespath
from urllib.parse import urlparse, parse_qs
import time
from aioVextractor.utils.user_agent import UserAgent
from aioVextractor.utils.requests_retry import RequestRetry
from random import choice
from scrapy.selector import Selector
import asyncio
import traceback

# @RequestRetry
# async def entrance(webpage_url, session):
#     headers = {'Connection': 'keep-alive',
#                'Upgrade-Insecure-Requests': '1',
#                'User-Agent': choice(UserAgent),
#                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
#                'Accept-Encoding': 'gzip, deflate',
#                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,ko;q=0.7',
#                }
#     async with session.get(webpage_url, headers=headers) as response:
#         response_text = await response.text(encoding='utf8', errors='ignore')
#         selector = Selector(text=response_text)
#         iframe_url = selector.css('iframe[src*=vid]::attr(src)').extract_first()
#         vid = parse_qs(urlparse(iframe_url).query)['vid'][0]
#         inKey = parse_qs(urlparse(iframe_url).query)['inKey'][0]
#         result = dict()
#         result['avatar'] = selector.css('.bloger .thumb img::attr(src)').extract_first().split('?')[0]
#         author_videoNum = selector.css('.category_title::text').re('([\d|,]*)')
#         result['author_videoNum'] = sorted(author_videoNum)[-1].replace(',', '')
#         result['vid'] = vid
#         result['from'] = "naver"
#         result['upload_ts'] = format_upload_ts(selector.css("p[class*='_postAddDate']::text").extract_first())
#         result['webpage_url'] = webpage_url
#         VideoJson = await request_naver_api(iframe_url=iframe_url, inKey=inKey, session=session, vid=vid)
#         return extract(VideoJson=VideoJson, result=result)
#
#
# @RequestRetry
# async def request_naver_api(iframe_url, inKey, session, vid):
#     headers = {'Origin': 'http://serviceapi.nmv.naver.com',
#                'Accept-Encoding': 'gzip, deflate',
#                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,ko;q=0.7',
#                'User-Agent': choice(UserAgent),
#                'Accept': '*/*',
#                'Referer': iframe_url,
#                'Connection': 'keep-alive'}
#     params = {'key': inKey,
#               'pid': 'rmcPlayer_{time}'.format(time=int(time.time() * 10 ** 7)),
#               'sid': '2',
#               'ver': '2.0',
#               'devt': 'html5_mo',
#               'doct': 'json',
#               'ptc': 'http',
#               'sptc': 'http',
#               'cpt': 'vtt',
#               'ctls': '{"visible":{"fullscreen":true,"logo":false,"playbackRate":false,"scrap":true,"playCount":true,"commentCount":true,"title":true,"writer":false,"expand":false,"subtitles":true,"thumbnails":true,"quality":true,"setting":true,"script":false,"logoDimmed":true,"badge":true,"seekingTime":true,"linkCount":true,"createTime":false,"thumbnail":true},"clicked":{"expand":false,"subtitles":false}}',
#               'pv': '4.8.45',
#               'dr': '1920x1080',
#               'lc': 'ko_KR'}
#     naver_api = 'http://apis.naver.com/rmcnmv/rmcnmv/vod/play/v2.0/{vid}'.format(vid=vid)
#     async with  session.get(naver_api, headers=headers, params=params) as response:
#         VideoJson = await response.json()
#         return VideoJson
#
#
# def format_upload_ts(upload_ts):
#     """
#     input: '2018. 3. 20. 22:14'
#
#     """
#     try:
#         return int(time.mktime(time.strptime(upload_ts, '%Y. %m. %d. %H:%M'))) if upload_ts else None
#     except:
#         print(f"upload_ts: {upload_ts}")
#         traceback.print_exc()
#         return None
#
#
# def extract(VideoJson, result):
#     result['author'] = jmespath.search('meta.user.name', VideoJson)
#     result['play_addr'] = jmespath.search("max_by(videos.list, &size).source", VideoJson)
#     result['title'] = jmespath.search('meta.subject', VideoJson)
#     result['cover'] = jmespath.search('meta.cover.source', VideoJson)
#     video_duration = jmespath.search('videos.list[0].duration', VideoJson)
#     result['duration'] = int(video_duration) if video_duration else None
#     return result
#
#
# def extract_play_addr(VideoJson):
#     play_addr_list = dict()
#     for size, src in jmespath.search('videos.list[].[size, source]', VideoJson):
#         play_addr_list[size] = src
#     if len(play_addr_list) == 1:
#         play_addr = play_addr_list[max(play_addr_list)]
#     else:
#         if None in play_addr_list:
#             del play_addr_list[None]
#         play_addr = play_addr_list[max(play_addr_list)]
#     return play_addr


TEST_CASE = [
    "http://blog.naver.com/PostList.nhn?blogId=paranzui&categoryNo=0&from=postList",
    "http://blog.naver.com/PostView.nhn?blogId=paranzui&logNo=221233413302&categoryNo=0&parentCategoryNo=0&viewDate=&currentPage=11&postListTopCurrentPage=1&from=postList&userTopListOpen=true&userTopListCount=5&userTopListManageOpen=false&userTopListCurrentPage=11",
    "http://blog.naver.com/PostView.nhn?blogId=paranzui&logNo=221239676910&categoryNo=0&parentCategoryNo=0&viewDate=&currentPage=11&postListTopCurrentPage=1&from=postList&userTopListOpen=true&userTopListCount=5&userTopListManageOpen=false&userTopListCurrentPage=11",
    "http://blog.naver.com/PostView.nhn?blogId=paranzui&logNo=221227458497&categoryNo=0&parentCategoryNo=0&viewDate=&currentPage=29&postListTopCurrentPage=1&from=postList&userTopListOpen=true&userTopListCount=5&userTopListManageOpen=false&userTopListCurrentPage=29",
]

from aioVextractor.extractor.base_extractor import (BaseExtractor, validate, RequestRetry)


class Extractor(BaseExtractor):
    target_website = [
        "http://blog\.naver\.com/PostView\.nhn\?blogId=\w*?&logNo=\d{9,15}",
        "http://blog\.naver\.com/PostList\.nhn\?blogId=\w*",
    ]

    def __init__(self, *args, **kwargs):
        BaseExtractor.__init__(self, *args, **kwargs)
        self.from_ = "naver"

    @validate
    @RequestRetry
    async def entrance(self, webpage_url, session):
        async with session.get(webpage_url, headers=self.general_headers(user_agent=self.random_ua())) as response:
            response_text = await response.text(encoding='utf8', errors='ignore')
            selector = Selector(text=response_text)
            iframe_url = selector.css('iframe[src*=vid]::attr(src)').extract_first()
            vid = parse_qs(urlparse(iframe_url).query)['vid'][0]
            inKey = parse_qs(urlparse(iframe_url).query)['inKey'][0]
            result = dict()
            result['avatar'] = selector.css('.bloger .thumb img::attr(src)').extract_first().split('?')[0]
            author_videoNum = selector.css('.category_title::text').re('([\d|,]*)')
            result['author_videoNum'] = sorted(author_videoNum)[-1].replace(',', '')
            result['vid'] = vid
            result['from'] = self.from_
            result['upload_ts'] = self.format_upload_ts(selector.css("p[class*='_postAddDate']::text").extract_first())
            result['webpage_url'] = webpage_url
            VideoJson = await self.request_naver_api(iframe_url=iframe_url, in_key=inKey, session=session, vid=vid)
            return self.extract(video_json=VideoJson, result=result)

    @RequestRetry
    async def request_naver_api(self, iframe_url, in_key, session, vid):
        headers = self.general_headers(user_agent=self.random_ua())
        headers['Referer'] = iframe_url
        headers['Origin'] = "http://serviceapi.nmv.naver.com"
        params = {'key': in_key,
                  'pid': f'rmcPlayer_{int(time.time() * 10 ** 7)}',
                  'sid': '2',
                  'ver': '2.0',
                  'devt': 'html5_mo',
                  'doct': 'json',
                  'ptc': 'http',
                  'sptc': 'http',
                  'cpt': 'vtt',
                  'ctls': '{"visible":{"fullscreen":true,"logo":false,"playbackRate":false,"scrap":true,"playCount":true,"commentCount":true,"title":true,"writer":false,"expand":false,"subtitles":true,"thumbnails":true,"quality":true,"setting":true,"script":false,"logoDimmed":true,"badge":true,"seekingTime":true,"linkCount":true,"createTime":false,"thumbnail":true},"clicked":{"expand":false,"subtitles":false}}',
                  'pv': '4.8.45',
                  'dr': '1920x1080',
                  'lc': 'ko_KR'}
        naver_api = 'http://apis.naver.com/rmcnmv/rmcnmv/vod/play/v2.0/{vid}'.format(vid=vid)
        async with session.get(naver_api, headers=headers, params=params) as response:
            VideoJson = await response.json()
            return VideoJson

    @staticmethod
    def format_upload_ts(upload_ts):
        """
        input: '2018. 3. 20. 22:14'

        """
        try:
            return int(time.mktime(time.strptime(upload_ts, '%Y. %m. %d. %H:%M'))) if upload_ts else None
        except:
            traceback.print_exc()
            return None

    @staticmethod
    def extract(video_json, result):
        result['author'] = jmespath.search('meta.user.name', video_json)
        result['play_addr'] = jmespath.search("max_by(videos.list, &size).source", video_json)
        result['title'] = jmespath.search('meta.subject', video_json)
        result['cover'] = jmespath.search('meta.cover.source', video_json)
        video_duration = jmespath.search('videos.list[0].duration', video_json)
        result['duration'] = int(video_duration) if video_duration else None
        return result

    @staticmethod
    def extract_play_addr(video_json):
        play_addr_list = dict()
        for size, src in jmespath.search('videos.list[].[size, source]', video_json):
            play_addr_list[size] = src
        if len(play_addr_list) == 1:
            play_addr = play_addr_list[max(play_addr_list)]
        else:
            if None in play_addr_list:
                del play_addr_list[None]
            play_addr = play_addr_list[max(play_addr_list)]
        return play_addr


if __name__ == '__main__':
    with Extractor() as extractor:
        res = extractor.sync_entrance(webpage_url="http://blog.naver.com/PostList.nhn?blogId=paranzui&categoryNo=0&from=postList")
        print(res)

    # import aiohttp
    # from pprint import pprint
    #
    #
    # async def test():
    #     async with aiohttp.ClientSession() as session_:
    #         return await entrance(
    #             webpage_url="http://blog.naver.com/PostView.nhn?blogId=paranzui&logNo=221227458497&categoryNo=0&parentCategoryNo=0&viewDate=&currentPage=29&postListTopCurrentPage=1&from=postList&userTopListOpen=true&userTopListCount=5&userTopListManageOpen=false&userTopListCurrentPage=29",
    #             session=session_)
    #
    #
    # loop = asyncio.get_event_loop()
    # pprint(loop.run_until_complete(test()))
