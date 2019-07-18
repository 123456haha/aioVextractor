#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 2019/6/20
# IDE: PyCharm

from aioVextractor.utils.requests_retry import RequestRetry
from aioVextractor.utils.user_agent import UserAgent
import time
from random import choice
from scrapy.selector import Selector
import os
from urllib.parse import urlparse
import jmespath
import ujson as json
import asyncio


@RequestRetry
async def entrance(webpage_url, session):
    if 'code' in webpage_url.lower():  ## old version http://www.tvcf.co.kr/YCf/V.asp?Code=A000363280
        ParseResult = urlparse(webpage_url)
        try:
            code = ParseResult.query.split('=')[1]
        except:
            return False
        else:
            headers = {'User-Agent': choice(UserAgent),
                       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                       'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
                       'Connection': 'keep-alive',
                       'Upgrade-Insecure-Requests': '1',
                       'Cache-Control': 'max-age=0'}
            params = {'Code': code}
            async with session.get('http://www.tvcf.co.kr/YCf/V.asp', headers=headers, params=params) as response:
                response_text = await response.text(encoding='utf8', errors='ignore')
                result = dict()
                result['webpage_url'] = webpage_url
                result['from'] = "tvcf"
                result = await extract_old(response_text, code, result=result)
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
                r_code_json = json.loads(response_text)
                code = jmespath.search('video.code', r_code_json)
                result['from'] = "tvcf"
                result['webpage_url'] = webpage_url
                result['vid'] = code
                result['cover'] = jmespath.search('video.cut', r_code_json)
                result['title'] = jmespath.search('video.title', r_code_json)
                result['description'] = jmespath.search('video.copy', r_code_json)
                ## download video
                fn = os.path.split(result['cover'])[-1].split('.')[0]
                fn_high_quality = fn + "_720p"
                play_addr_high_quality = f"http://media.tvcf.co.kr/Service/VStream/VideoStreamer.ashx?fn={fn_high_quality}.mp4"
                # play_addr = f"http://media.tvcf.co.kr/Service/VStream/VideoStreamer.ashx?fn={fn}.mp4"
                result['play_addr'] = play_addr_high_quality
                try:
                    upload_date = jmespath.search('video.onair', r_code_json)
                    result['upload_ts'] = int(
                        time.mktime(time.strptime(upload_date, '%Y%m%d'))) if upload_date else None
                except:
                    result['upload_ts'] = None
                result['rating'] = None
                return await extract_new(session=session, result=result, idx=idx)


# async def download(url, crawlist_id, dir_uuid, chance_left=config.RETRY):
#     async with aiohttp.ClientSession() as session:
#         if 'code' in url.lower():  ## old version http://www.tvcf.co.kr/YCf/V.asp?Code=A000363280
#             ParseResult = urlparse(url)
#             code = ParseResult.query.split('=')[1]
#             headers = {'User-Agent': choice(UserAgent),
#                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#                        'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
#                        'Connection': 'keep-alive',
#                        'Upgrade-Insecure-Requests': '1',
#                        'Cache-Control': 'max-age=0'}
#             params = {'Code': code}
#             try:
#                 async with session.get('http://www.tvcf.co.kr/YCf/V.asp', headers=headers, params=params) as response:
#                     response_text = await response.text(encoding='utf8', errors='ignore')
#             except (ServerDisconnectedError, ServerConnectionError, TimeoutError, ClientConnectorError,
#                     ServerTimeoutError, ContentTypeError, ClientConnectorCertificateError, ClientOSError,
#                     ClientPayloadError):
#                 if chance_left != 1:
#                     return await download(url=url, crawlist_id=crawlist_id, dir_uuid=dir_uuid,
#                                           chance_left=chance_left - 1)
#                 else:
#                     return False
#             else:
#                 result = dict()
#                 result['webpage_url'] = url
#                 result = await extract_old(response_text, code, result=result)
#                 return result
#
#         else:  ## new version https://v.tvcf.co.kr/728764
#             headers = {
#                 'Authorization': 'Bearer null',
#                 'Accept-Encoding': 'gzip, deflate, br',
#                 'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,ko;q=0.7',
#                 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36',
#                 'Accept': 'application/json, text/plain, */*',
#                 'Referer': url,  ## https://v.tvcf.co.kr/738572
#                 'Connection': 'keep-alive'}
#             try:
#                 idx = os.path.split(url)[-1]
#             except IndexError:
#                 return False
#             else:
#                 result = dict()
#                 result['webpage_url'] = url
#                 async with session.get(f'https://v.tvcf.co.kr/rest/api/player/init/{idx}', headers=headers) as r_code:
#                     r_code_json = await r_code.json()
#                     code = jmespath.search('video.code', r_code_json)
#                     result['id'] = code
#                     result['thumbnail'] = jmespath.search('video.cut', r_code_json)
#                     ## download video
#                     fn = os.path.split(result['thumbnail'])[-1].split('.')[0]
#                     fn_high_quality = fn + "_720p"
#                     play_addr_high_quality = f"http://media.tvcf.co.kr/Service/VStream/VideoStreamer.ashx?fn={fn_high_quality}.mp4"
#                     # play_addr = f"http://media.tvcf.co.kr/Service/VStream/VideoStreamer.ashx?fn={fn}.mp4"
#                     result['play_addr'] = play_addr_high_quality
#                     try:
#                         upload_date = jmespath.search('video.onair', r_code_json)
#                         result['timestamp'] = int(
#                             time.mktime(time.strptime(upload_date, '%Y%m%d'))) if upload_date else None
#                     except:
#                         result['timestamp'] = None
#                     result['rating'] = None
#                     return await extract_new(session=session, result=result, idx=idx)


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
    result['tags'] = selector.css('.tag::text').extract()
    try:
        fn = os.path.split(result['cover'])[-1].split('.')[0]
    except TypeError:
        return False
    else:
        ## download video
        fn_high_quality = fn + "_720p"
        play_addr_high_quality = f"http://media.tvcf.co.kr/Service/VStream/VideoStreamer.ashx?fn={fn_high_quality}.mp4"
        # play_addr = f"http://media.tvcf.co.kr/Service/VStream/VideoStreamer.ashx?fn={fn}.mp4"
        result['play_addr'] = play_addr_high_quality
        return result


async def extract_new(session, result, idx):
    """
    :param session:
    :param result:
    :param idx:
    :return:
    """
    result['title'], result['tags'] = await asyncio.gather(*[get_title(session=session, idx=idx),
                                                             get_tags(session=session, idx=idx)])
    return result


# async def download_video(play_addr, result, dir_uuid, crawlist_id, chance_left=config.RETRY):
#     print(
#         f"{time.strftime('%m-%d %H:%M:%S', time.localtime(time.time()))} {crawlist_id} Downloading play_addr {play_addr}")
#     vid = result['id']
#     download_path = os.path.join(config.download_video_prefix_path, dir_uuid).replace('\\', '/')
#     video_ext = get_ext(play_addr)
#     if video_ext is False or video_ext is '':
#         video_ext = 'mp4'
#     filename = '.'.join([vid, video_ext])
#     file_path = os.path.join(download_path, filename)
#     os.makedirs(download_path, exist_ok=True)
#     headers = {'Connection': 'keep-alive',
#                'Cache-Control': 'max-age=0',
#                'Upgrade-Insecure-Requests': '1',
#                'User-Agent': choice(UserAgent),
#                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
#                'Accept-Encoding': 'gzip, deflate',
#                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,ko;q=0.7'}
#     try:
#         with requests.get(play_addr, verify=False, headers=headers, stream=True) as response:
#             response.raise_for_status()
#             async with aiofiles.open(file_path, mode='wb') as stream:
#                 for chunk in response.iter_content(chunk_size=8192):
#                     await stream.write(chunk)
#     except Exception as error:
#         print(f'{time.strftime("%m-%d %H:%M", time.localtime(time.time()))} {crawlist_id} Error occur: {error}\n'
#               f'{time.strftime("%m-%d %H:%M", time.localtime(time.time()))} {crawlist_id} format_exc(): {format_exc()}')
#         if chance_left != 1:
#             await download_video(play_addr=play_addr, result=result, dir_uuid=dir_uuid,
#                                  crawlist_id=crawlist_id, chance_left=chance_left - 1)
#         else:
#             return False
#     else:
#         result['_filename'] = file_path
#         result['filesize'] = os.path.getsize(file_path)
#         return result


# def get_ext(url_):
#     """Return the filename extension from url, or ''."""
#     if url_ is None:
#         return False
#     parsed = urlparse(url_)
#     root, ext_ = splitext(parsed.query)
#     ext = ext_[1:]  # or ext[1:] if you don't want the leading '.'
#     ## ext = 'jpeg@80w_80h_1e_1c'
#     return ext.split('@')[0]


@RequestRetry(default_exception_return=[], default_other_exception_return=[])
async def get_tags(session, idx):
    headers = {
        'Authorization': 'Bearer null',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'User-Agent': choice(UserAgent),
        'Accept': 'application/json, text/plain, */*',
        'Referer': f'https://play.tvcf.co.kr/{idx}',
        'Connection': 'keep-alive',
    }
    async  with session.get(f'https://play.tvcf.co.kr/rest/api/player/tag/{idx}', headers=headers) as response:
        response_text = await response.text()
        response_json = json.loads(response_text)
        return response_json


@RequestRetry(default_exception_return='', default_other_exception_return='')
async def get_title(session, idx):
    headers = {
        'Authorization': 'Bearer null',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'User-Agent': choice(UserAgent),
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
async def get_commit_num(vid, session):
    headers = {'Authorization': 'Bearer null',
               'Accept-Encoding': 'gzip, deflate, br',
               'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
               'User-Agent': choice(UserAgent),
               'Accept': 'application/json, text/plain, */*'}
    params = {'skip': '0',
              'take': '5'}
    url = f'https://play.tvcf.co.kr/rest/api/player/ReplyMore/{vid}'
    async with session.get(url, headers=headers, params=params) as resp:
        html = await resp.text(encoding='utf-8')
        try:
            data = json.loads(html)
            return data.get('total', 0)
        except:
            return None


if __name__ == '__main__':
    import asyncio
    import aiohttp
    from pprint import pprint

    "http://www.tvcf.co.kr/YCf/V.asp?Code=A000363280"
    "https://play.tvcf.co.kr/750556"


    async def test():
        async with aiohttp.ClientSession() as session_:
            return await entrance(webpage_url="https://play.tvcf.co.kr/750556",
                                  session=session_)


    loop = asyncio.get_event_loop()
    pprint(loop.run_until_complete(test()))