#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 2019/6/20
# IDE: PyCharm


import jmespath
from ..utils.user_agent import (UserAgent)
from .. import config
from random import choice
from os.path import splitext
from scrapy.selector import Selector
import asyncio
import html
import emoji
import dateutil.parser
import traceback
from urllib.parse import urlparse
from ..utils.exception import exception
import os

async def entrance(webpage_url, session, chance_left=config.RETRY):
    headers = {'Connection': 'keep-alive',
               'Cache-Control': 'max-age=0',
               'Upgrade-Insecure-Requests': '1',
               'User-Agent': choice(UserAgent),
               'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
               'Accept-Encoding': 'gzip, deflate',
               'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,ko;q=0.7'}
    params = {'from': 'ArticleList'}

    try:
        async with session.get(webpage_url, headers=headers, params=params) as response:
            response_text = await response.text(encoding='utf8', errors='ignore')
    except exception:
        if chance_left != 1:
            return await entrance(webpage_url, session, chance_left=chance_left - 1)
        else:
            return False
    except:
        traceback.print_exc()
        return False
    else:
        webpage = await extract_publish(response=response_text)
        vid = webpage['vid']
        if not vid:
            return False
        video = await extract_video_info(referer=webpage_url, vid=vid, session=session)
        if all([webpage, video]):
            return {**webpage, **video}
        else:
            pprint([webpage, video])
            return False




#
# async def download(url, crawlist_id, dir_uuid, chance_left=config.RETRY):
#     try:
#         headers = {'Connection': 'keep-alive',
#                    'Cache-Control': 'max-age=0',
#                    'Upgrade-Insecure-Requests': '1',
#                    'User-Agent': choice(UserAgent),
#                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
#                    'Accept-Encoding': 'gzip, deflate',
#                    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,ko;q=0.7'}
#         params = {'from': 'ArticleList'}
#         try:
#             path = os.path.split(urlparse(url).path)[1]
#         except IndexError:
#             print(f'{crawlist_id} IndexError occur: \n'
#                   f'{crawlist_id} format_exc(): {format_exc()}')
#             return False
#         else:
#             extract_common_info_url = 'http://www.xinpianchang.com/{}'.format(path)
#             async with aiohttp.ClientSession() as session:
#                 try:
#                     async with session.get(extract_common_info_url, headers=headers, params=params) as response:
#                         response_text = await response.text(encoding='utf8', errors='ignore')
#                 except (ServerDisconnectedError, ServerConnectionError, TimeoutError, ClientConnectorError,
#                         ServerTimeoutError, ContentTypeError, ClientConnectorCertificateError, ClientOSError,
#                         ClientPayloadError):
#                     if chance_left != 1:
#                         return await download(url=url, crawlist_id=crawlist_id,
#                                               dir_uuid=dir_uuid, chance_left=chance_left - 1)
#                     else:
#                         return False
#                 else:
#                     result = await extract_publish(response=response_text)
#                     vid = result['id']
#                     response_json = await extract_video_info(url=url, vid=vid, session=session)
#                     play_addr = jmespath.search('max_by(data.resource.progressive, &filesize).https_url', response_json)
#                     video_duration = jmespath.search('data.video.duration', response_json)
#                     try:
#                         width, height = jmespath.search('data.resource.*.[width, height]', response_json)[0]
#                     except IndexError:
#                         width = height = None
#                     result['formats'] = [{'width': width, 'height': height}]
#                     result['duration'] = int(int(video_duration) / 1000) if video_duration else video_duration
#                     result['webpage_url'] = url
#                     return await download_video(play_addr=play_addr,
#                                                 result=result,
#                                                 session=session,
#                                                 dir_uuid=dir_uuid,
#                                                 crawlist_id=crawlist_id)
#     except Exception as error:
#         print(f'{crawlist_id} Error occur: {error}\n'
#               f'{crawlist_id} format_exc(): {format_exc()}')
#         return False


async def extract_publish(response):
    result = dict()
    try:
        selector = Selector(text=response)
    except:
        traceback.print_exc()
        return False
    vid = selector.css('body script').re_first('vid: "([\s|\S]*?)",')
    result['vid'] = vid
    try:
        result['author'] = emoji.demojize(selector.css('.creator-info .name::text').extract_first().strip())
    except AttributeError:
        result['author'] = None
    result['author_id'] = selector.css('a[data-userid]::attr(data-userid)').extract_first()
    uploader_url = selector.css('a[data-userid]::attr(href)').extract_first()
    try:
        result['author_url'] = os.path.join("https://www.xinpianchang.com", uploader_url.strip('/'))
    except AttributeError:
        result['author_url'] = None

    result['title'] = selector.css('.title-wrap .title::text').extract_first()
    result['tag'] = selector.css('.tag-wrapper a ::text').extract()  ## ['公益', '央视', '清明']
    try:
        result['category'] = list(map(lambda x: x.strip(), selector.css('.cate a::text').extract()))
    except AttributeError:
        result['category'] = None

    video_create_time = selector.css('meta[property="article:published_time"]::attr(content)').extract_first()
    result['upload_ts'] = int(dateutil.parser.parse(video_create_time).timestamp()) if video_create_time else None
    try:
        result['upload_date'] = dateutil.parser.parse(video_create_time).strftime('%Y%m%d')
    except TypeError:
        result['upload_date'] = None
    try:
        result['description'] = unescape('\n'.join(
            map(lambda x: x.strip(), selector.css('.filmplay-info-desc>p[class~="desc"]::text').extract())))
    except AttributeError:
        result['description'] = None
    try:
        result['view_count'] = int(selector.css('.play-counts::text').extract_first().replace(',', ''))
    except (ValueError, AttributeError):
        result['view_count'] = None
    try:
        result['like_count'] = int(selector.css('.like-counts::text').extract_first().replace(',', ''))
    except (ValueError, AttributeError):
        result['like_count'] = None
    result['cover'] = selector.css('.social-share::attr(data-image)').extract_first()
    return result


async def extract_video_info(referer, vid, session, chance_left=config.RETRY):
    headers = {'User-Agent': choice(UserAgent),
               'Referer': referer,
               'Origin': 'http://www.xinpianchang.com'}
    params = {'expand': 'resource,resource_origin?'}
    extract_video_info_url = f'https://openapi-vtom.vmovier.com/v3/video/{vid}'
    try:
        async with session.get(extract_video_info_url, headers=headers, params=params) as response:
            response_json = await response.json()
    except exception:
        if chance_left != 1:
            return await extract_video_info(referer=referer, vid=vid, session=session, chance_left=chance_left - 1)
        else:
            return False
    else:
        result = dict()
        try:
            play_addr = jmespath.search('max_by(data.resource.progressive, &filesize).https_url', response_json)
        except:
            play_addr = jmespath.search('data.resource.progressive[-1].https_url', response_json)
        result['play_addr'] = play_addr
        video_duration = jmespath.search('data.video.duration', response_json)
        try:
            width, height = jmespath.search('data.resource.*.[width, height]', response_json)[0]
        except IndexError:
            width = height = None
        result['width'] = width
        result['height'] = height
        result['duration'] = int(int(video_duration) / 1000) if video_duration else video_duration
        result['webpage_url'] = referer
        return result

# async def download_video(play_addr, result, session, dir_uuid, crawlist_id, chance_left=config.RETRY):
#     print(f'\n{crawlist_id} DOWNLOADING {play_addr}')
#     vid = result['id']
#     download_path = os.path.join(config.download_video_prefix_path, dir_uuid).replace('\\', '/')
#     video_ext = get_ext(play_addr)
#     if video_ext is False or video_ext is '':
#         video_ext = 'mp4'
#     filename = '.'.join([vid, video_ext])
#     file_path = os.path.join(download_path, filename)
#     headers = {'authority': 'qiniu-xpc0.xpccdn.com',
#                'upgrade-insecure-requests': '1',
#                'user-agent': choice(UserAgent),
#                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
#                'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,ko;q=0.7'}
#     try:
#         async with session.get(play_addr, verify_ssl=False, headers=headers) as res_video:
#             response_video_content = await res_video.read()
#             os.makedirs(download_path, exist_ok=True)
#             async with aiofiles.open(file_path, mode='wb') as stream:
#                 await stream.write(response_video_content)
#     except (ServerDisconnectedError, ServerConnectionError, ClientOSError, ClientConnectorError,
#             ServerTimeoutError, ContentTypeError, ClientConnectorCertificateError, TimeoutError, ClientPayloadError):
#         if chance_left != 1:
#             await download_video(play_addr=play_addr, result=result, session=session,
#                                  dir_uuid=dir_uuid, crawlist_id=crawlist_id, chance_left=chance_left - 1)
#         else:
#             return False
#     result['_filename'] = file_path
#     result['filesize'] = os.path.getsize(file_path)
#     return result


def unescape(string):
    if string:
        return html.unescape(string)
    else:
        return None


def get_ext(url_):
    """Return the filename extension from url, or ''."""
    if url_ is None:
        return False
    parsed = urlparse(url_)
    root, ext_ = splitext(parsed.path)
    ext = ext_[1:]  # or ext[1:] if you don't want the leading '.'
    ## ext = 'jpeg@80w_80h_1e_1c'
    return ext.split('@')[0]



if __name__ == '__main__':
    import asyncio
    import aiohttp
    from pprint import pprint

    "https://www.xinpianchang.com/a10475334?from=ArticleList"
    "https://www.xinpianchang.com/u10009204?from=userList"


    async def test():
        async with aiohttp.ClientSession() as session_:
            return await entrance(
                webpage_url="https://www.xinpianchang.com/u10009204?from=userList",
                session=session_)


    pprint(asyncio.run(test()))
