#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 2019/7/1
# IDE: PyCharm

# import youtube_dl
# import jmespath
import traceback
# import time
# from urllib.parse import (parse_qs, urlparse)
# from aioVextractor.utils.user_agent import UserAgent
# from random import choice
# import aiohttp
# from aioVextractor.utils.requests_retry import RequestRetry
from concurrent import futures  ## lib for multiprocessing and threading
from scrapy import Selector
import os
import asyncio
#
#
# async def breakdown(webpage_url):
#     def wrapper(url):
#         try:
#             new_loop = asyncio.new_event_loop()
#             asyncio.set_event_loop(new_loop)
#             res = new_loop.run_until_complete(extract_info(webpage_url=url, collaborate=False))
#             new_loop.close()
#             return res
#         except:
#             traceback.print_exc()
#             return False
#     webpage_content = await retrieve_webpapge(webpage_url=webpage_url)
#     selector = Selector(text=webpage_content)
#     iframe_src = selector.css('iframe::attr(src)').extract()
#     with futures.ThreadPoolExecutor(max_workers=min(10, os.cpu_count())) as executor:  ## set up processes
#         executor.submit(wrapper)
#         future_to_url = [executor.submit(wrapper, url=iframe) for iframe in iframe_src]
#         results = []
#         try:
#             for f in futures.as_completed(future_to_url, timeout=max([len(iframe_src) * 3, 15])):
#                 try:
#                     result = f.result()
#                     result['playlist_url'] = webpage_url
#                     results.append(result)
#                 except:
#                     traceback.print_exc()
#                     continue
#         except:
#             pass
#         return results
#
#
# async def extract_info(webpage_url, collaborate=True):
#     args = {"nocheckcertificate": True,
#             "ignoreerrors": True,
#             "quiet": True,
#             "nopart": True,
#             # "download_archive": "record.txt",
#             "no_warnings": True,
#             "youtube_include_dash_manifest": False,
#             'simulate': True,
#             'user-agent': choice(UserAgent),
#             }
#     try:
#         with youtube_dl.YoutubeDL(args) as ydl:
#             try:
#                 VideoJson = ydl.extract_info(webpage_url)
#             except:
#                 traceback.print_exc()
#                 return False
#             else:
#                 if VideoJson:
#                     if collaborate:
#                         result = extract_single(VideoJson=VideoJson, webpage_url=webpage_url)
#                         return result
#                     else:  ## webpage extracting using only youtube-dl
#                         if 'entries' in VideoJson:
#                             result = []
#                             for entry in jmespath.search('entries[]', VideoJson):
#                                 element = extract_single(VideoJson=entry, webpage_url=webpage_url)
#                                 result.append(element)
#                             return result
#                         else:
#                             result = extract_single(VideoJson=VideoJson, webpage_url=webpage_url)
#                             return result
#                 else:
#                     return False
#     except:
#         traceback.print_exc()
#         return False
#
#
# def check_cover(cover):
#     """
#     Some of the vimeo cover urls contain play_icon
#     This method try to extract the url that not
#     :param cover:
#     :return:
#     """
#     if urlparse(cover).path == '/filter/overlay':
#         try:
#             cover_ = parse_qs(urlparse(cover).query).get('src0')[0]
#         except IndexError:
#             return cover
#         if 'play_icon' in cover_:
#             return cover
#         elif cover_ is None:
#             return cover
#         else:
#             return cover_
#     else:
#         return cover
#
#
# def extract_play_addr(VideoJson):
#     video_list = jmespath.search('formats[]', VideoJson)
#     try:
#         try:
#             # return sorted(filter(lambda x:x.get('protocol', '')  in {'https', 'http'}, video_list), key=lambda x:x['filesize'])[-1]
#             return sorted(filter(
#                 lambda x: (x.get('protocol', '') in {'https', 'http'}) and x.get('acodec') != 'none' and x.get(
#                     'vcodec') != 'none', video_list), key=lambda x: x['filesize'])[-1]
#         except KeyError:
#             return sorted(filter(
#                 lambda x: x.get('protocol', '') in {'https', 'http'} and x.get('acodec') != 'none' and x.get(
#                     'vcodec') != 'none', video_list), key=lambda x: x['height'])[-1]
#         except IndexError:
#             return jmespath.search('formats[-1]', VideoJson)
#     except:
#         # traceback.print_exc()
#         return jmespath.search('formats[-1]', VideoJson)
#
#
# def extract_single(VideoJson, webpage_url):
#     result = dict()
#     result['downloader'] = 'ytd'
#     result['webpage_url'] = webpage_url
#     result['author'] = jmespath.search('uploader', VideoJson)
#     result['cover'] = check_cover(jmespath.search('thumbnail', VideoJson))
#     create_time = jmespath.search('upload_date', VideoJson)
#     upload_ts = int(time.mktime(time.strptime(create_time, '%Y%m%d'))) if create_time else create_time
#     result['upload_ts'] = upload_ts
#     result['description'] = jmespath.search('description', VideoJson)
#     duration = jmespath.search('duration', VideoJson)
#     result['duration'] = int(duration) if duration else 0
#     result['rating'] = jmespath.search('average_rating', VideoJson)
#     result['height'] = jmespath.search('height', VideoJson)
#     result['like_count'] = jmespath.search('like_count', VideoJson)
#     result['view_count'] = jmespath.search('view_count', VideoJson)
#     result['dislike_count'] = jmespath.search('dislike_count', VideoJson)
#     result['width'] = jmespath.search('width', VideoJson)
#     result['vid'] = jmespath.search('id', VideoJson)
#     cate = jmespath.search('categories', VideoJson)
#     result['category'] = ','.join(list(map(lambda x: x.replace(' & ', ','), cate))) if cate else cate
#     # formats = extract_play_addr(VideoJson)
#     # result['play_addr'] = formats['url']
#     result['from'] = VideoJson.get('extractor', None).lower() if VideoJson.get('extractor', None) else urlparse(
#         webpage_url).netloc
#     result['title'] = jmespath.search('title', VideoJson)
#     video_tags = jmespath.search('tags', VideoJson)
#     result['tag'] = video_tags
#     return result
#
#
# @RequestRetry
# async def retrieve_webpapge(webpage_url):
#     """retrieve webpage"""
#     async with aiohttp.ClientSession(raise_for_status=True) as session:
#         headers = {
#             'upgrade-insecure-requests': '1',
#             'user-agent': choice(UserAgent),
#             'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
#             'accept-encoding': 'gzip, deflate, br',
#             'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
#         }
#         async with session.get(webpage_url, headers=headers) as response:
#             return await response.text()

TEST_CASE = [
    "https://www.bilibili.com/video/av5546345?spm_id_from=333.334.b_62696c695f646f756761.4",
]

from aioVextractor.extractor.base_extractor import (BaseExtractor, validate, RequestRetry)


class Extractor(BaseExtractor):

    @validate
    @RequestRetry
    async def entrance(self, webpage_url, session):
        results = await self.breakdown(webpage_url=webpage_url)
        return results



if __name__ == '__main__':
    with Extractor() as extractor:
        # print(extractor.target_website)
        ress = extractor.sync_entrance(webpage_url="http://peacefulcuisine.com/category/videos/#")
        print(ress)


    # async def test():
    #     return await extract_info(
    #         webpage_url="https://www.bilibili.com/video/av5546345?spm_id_from=333.334.b_62696c695f646f756761.4")
    #
    #
    # loop = asyncio.get_event_loop()
    # pprint(loop.run_until_complete(test()))
