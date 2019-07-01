#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 2019/6/20
# IDE: PyCharm

import youtube_dl
import jmespath
import traceback
import time
import ujson as json
import config
from utils.user_agent import UserAgent
from scrapy import Selector
from random import choice
from aiohttp.client_exceptions import (ServerDisconnectedError, ServerConnectionError, ClientOSError,
                                       ClientConnectorCertificateError, ServerTimeoutError, ContentTypeError,
                                       ClientConnectorError, ClientPayloadError)


async def entrance(webpage_url, session, chance_left=config.RETRY):
    try:
        gather_results = await asyncio.gather(*[
            extract_info(webpage_url=webpage_url),
            extract_author(webpage_url=webpage_url, session=session)
        ])
        return {**gather_results[0], **gather_results[1]}


    except:
        traceback.print_exc()
        return False


async def extract_info(webpage_url):
    args = {"nocheckcertificate": True,
            "ignoreerrors": True,
            "quiet": True,
            "nopart": True,
            # "download_archive": "record.txt",
            "no_warnings": True,
            "youtube_include_dash_manifest": False,
            'simulate': True
            }
    try:
        with youtube_dl.YoutubeDL(args) as ydl:
            try:
                VideoJson = ydl.extract_info(webpage_url)
                # pprint(VideoJson)
            except:
                traceback.print_exc()
                return False
            else:
                result = dict()
                result['webpage_url'] = webpage_url
                result['author'] = jmespath.search('uploader', VideoJson)
                result['cover'] = jmespath.search('thumbnail', VideoJson)
                create_time = jmespath.search('upload_date', VideoJson)
                result['upload_ts'] = int(
                    time.mktime(time.strptime(create_time, '%Y%m%d'))) if create_time else create_time
                result['description'] = jmespath.search('description', VideoJson)
                duration = jmespath.search('duration', VideoJson)
                result['duration'] = int(duration) if duration else duration
                result['rating'] = jmespath.search('average_rating', VideoJson)
                result['height'] = jmespath.search('height', VideoJson)
                result['like_count'] = jmespath.search('like_count', VideoJson)
                result['view_count'] = jmespath.search('view_count', VideoJson)
                result['dislike_count'] = jmespath.search('dislike_count', VideoJson)
                result['width'] = jmespath.search('width', VideoJson)
                result['vid'] = jmespath.search('id', VideoJson)
                cate = jmespath.search('categories', VideoJson)
                result['category'] = ','.join(list(map(lambda x: x.replace(' & ', ','), cate))) if cate else cate
                play_addr_list = dict()
                for u, p, h in jmespath.search('formats[].[url, protocol, height]', VideoJson):
                    if ('m3u8' not in u) and ('/../' not in u):
                        play_addr_list[h] = u
                if len(play_addr_list) == 1:
                    result['play_addr'] = play_addr_list[max(play_addr_list)]
                else:
                    if None in play_addr_list:
                        del play_addr_list[None]
                    result['play_addr'] = play_addr_list[max(play_addr_list)]
                result['title'] = jmespath.search('title', VideoJson)
                video_tags = jmespath.search('tags', VideoJson)
                result['tag'] = video_tags
                return result
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
    except (ServerDisconnectedError, ServerConnectionError, asyncio.TimeoutError,
            ClientConnectorError, ClientPayloadError, ServerTimeoutError,
            ContentTypeError, ClientConnectorCertificateError, ClientOSError):
        if chance_left != 1:
            return await entrance(webpage_url=webpage_url, session=session, chance_left=chance_left - 1)
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
            # pprint(ytInitialData)
            author_avatar = jmespath.search('contents.twoColumnWatchNextResults.results.results.contents[1].videoSecondaryInfoRenderer.owner.videoOwnerRenderer.thumbnail.thumbnails[-1].url', ytInitialData)
        return {"author_avatar":author_avatar}

FIELD_REMAIN = ['author_avatar', ]

if __name__ == '__main__':
    import asyncio
    import aiohttp
    from pprint import pprint

    "https://www.youtube.com/watch?v=tofSaLB9kwE"
    "https://www.bilibili.com/video/av5546345?spm_id_from=333.334.b_62696c695f646f756761.4"


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
