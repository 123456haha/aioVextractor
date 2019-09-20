#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 2019/6/20
# IDE: PyCharm


import jmespath
import time
from urllib.parse import urlparse
import re
from aioVextractor.utils.requests_retry import RequestRetry

now = lambda: time.time()


@RequestRetry
async def entrance(webpage_url, session):
    try:
        webpage_url = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]| [! *(),] |(?: %[0-9a-fA-F][0-9a-fA-F]))+',
                                 webpage_url)[0]
    except IndexError:
        return False
    download_headers = {'Connection': 'keep-alive',
                        'Upgrade-Insecure-Requests': '1',
                        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                        'Accept-Encoding': 'gzip, deflate',
                        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,ko;q=0.7'}
    async with session.get(webpage_url, headers=download_headers, allow_redirects=False) as response_getinfo:
        Location = response_getinfo.headers['Location']
        get_aweme_id = lambda L: urlparse(L).path.strip('/').split('/')[-1]
        aweme_id = get_aweme_id(Location)
        # print(f"aweme_id: {aweme_id}")
        result = extract(response_json=await aweme_detail(aweme_id=aweme_id,
                                                          session=session))
        return result if result else None


@RequestRetry
async def aweme_detail(aweme_id, session):
    """
    get all info of the video
    """
    api = f'https://aweme-hl.snssdk.com/aweme/v1/aweme/detail/?aweme_id={aweme_id}&device_platform=ios&app_name=aweme&aid=1128'
    aweme_detail_headers = {'user-agent': 'Mozilla/5.0'}
    async with session.get(api.format(aweme_id),
                           headers=aweme_detail_headers,
                           ) as response:
        response_json = await response.json()
        return jmespath.search('aweme_detail', response_json)


def extract(response_json):
    """
    extract all info from response_json
    """
    if response_json is False:
        return False
    else:
        result = dict()
        result['from'] = "抖音"
        result['author'] = jmespath.search('author.nickname', response_json)
        result['author_avatar'] = jmespath.search('author.avatar_larger.url_list[0]', response_json)
        result['author_description'] = jmespath.search('author.signature', response_json)
        author_gender = jmespath.search('author.gender', response_json)
        if author_gender == 2:
            result['author_gender'] = '女'
        elif author_gender == 1:
            result['author_gender'] = '男'
        else:
            result['author_gender'] = None
        result['author_id'] = jmespath.search('author.uid', response_json)
        result['play_addr'] = jmespath.search("video.play_addr.url_list[?contains(@, 'bytecdn')] | [0]", response_json)
        if not result['play_addr']:
            result['play_addr'] = jmespath.search("video.play_addr.url_list[0]", response_json)
        result['title'] = jmespath.search('desc', response_json)
        result['vid'] = jmespath.search('aweme_id', response_json)
        result['cover'] = jmespath.search('video.cover.url_list[0]', response_json)
        result['tag'] = jmespath.search('text_extra[].hashtag_name', response_json)
        result['language'] = jmespath.search('desc_language', response_json)
        result['region'] = jmespath.search('region', response_json)
        result['upload_ts'] = jmespath.search('create_time', response_json)
        result['webpage_url'] = jmespath.search('share_url', response_json)
        result['comment_count'] = jmespath.search('statistics.comment_count', response_json)
        result['like_count'] = jmespath.search('statistics.digg_count', response_json)
        result['download_count'] = jmespath.search('statistics.download_count', response_json)
        result['forward_count'] = jmespath.search('statistics.forward_count', response_json)
        result['share_count'] = jmespath.search('statistics.share_count', response_json)
        result['height'] = jmespath.search('video.height', response_json)
        result['width'] = jmespath.search('video.width', response_json)
        video_duration = jmespath.search('video.duration', response_json)
        result['duration'] = int(int(video_duration) / 1000) if video_duration else None
        return result


TEST_CASE = [
    "#在抖音，记录美好生活#球球老婆怀孕之后就爱睡这个洗脸巢 睡姿也太可爱了8#猫 http://v.douyin.com/hd9sb3/ 复制此链接，打开【抖音短视频】，直接观看视频！",
    "http://v.douyin.com/hd9sb3/",
]

if __name__ == '__main__':
    import asyncio
    import aiohttp
    from pprint import pprint


    async def test():
        async with aiohttp.ClientSession() as session_:
            return await entrance(
                webpage_url="#在抖音，记录美好生活#球球老婆怀孕之后就爱睡这个洗脸巢 睡姿也太可爱了8#猫 http://v.douyin.com/hd9sb3/ 复制此链接，打开【抖音短视频】，直接观看视频！",
                session=session_)


    loop = asyncio.get_event_loop()
    pprint(loop.run_until_complete(test()))
