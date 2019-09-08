#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 1/21/19
# IDE: PyCharm

import re
import asyncio
import jmespath
from aioVextractor.utils.user_agent import UserAgent
from aioVextractor.utils.requests_retry import RequestRetry
from random import choice


async def entrance(webpage_url, session):
    try:
        vid = re.compile('id=(\d*)').findall(webpage_url)[0]
    except IndexError:
        return False
    else:
        result = await asyncio.gather(extract_playLink(vid=vid, session=session),
                                      extract_info(vid=vid, session=session, webpage_url=webpage_url))
        if all(result):
            result_playLink, result_info = result
            return {**result_playLink, **result_info}
        else:
            print(f"extractor renren result: {result}")
            return False


@RequestRetry
async def extract_playLink(vid, session):
    headers = {'Accept': 'application/json, text/plain, */*',
               'Referer': 'https://mobile.rr.tv/mission/',
               'Origin': 'https://mobile.rr.tv',
               'clientType': 'web',
               'User-Agent': choice(UserAgent),
               'token': 'undefined',
               'clientVersion': 'undefined'}
    params = {'videoId': vid}
    url = 'https://api.rr.tv/v3plus/video/getVideoPlayLinkByVideoId'
    async with session.get(url, headers=headers, params=params) as response:
        ResJson = await response.json()
        if ResJson['code'] != '0000':
            return False
        elif not ResJson['data']['playLink']:
            return False
        else:
            return {'vid': vid, 'play_addr': ResJson['data']['playLink']}


@RequestRetry
async def extract_info(vid, session, webpage_url):
    headers = {'Origin': 'https://mobile.rr.tv',
               'Accept-Encoding': 'gzip, deflate, br',
               'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,ko;q=0.7',
               'User-Agent': choice(UserAgent),
               'Accept': 'application/json, text/plain, */*',
               'Referer': 'https://mobile.rr.tv/mission/',
               'clientVersion': 'undefined',
               'Connection': 'keep-alive',
               'token': 'undefined',
               'clientType': 'web'}
    params = {'videoId': vid}
    async with session.get('https://api.rr.tv/v3plus/video/detail', headers=headers, params=params) as response:
        VideoDetail = await response.json()
        result = dict()
        result['webpage_url'] = webpage_url
        result['from'] = "人人视频"
        result['author'] = jmespath.search('data.videoDetailView.author.nickName', VideoDetail)
        result['avatar'] = jmespath.search('data.videoDetailView.author.headImgUrl', VideoDetail)
        result['role'] = jmespath.search('data.videoDetailView.author.roleInfo', VideoDetail)
        result['author_videoNum'] = jmespath.search('data.videoDetailView.author.videoCount', VideoDetail)
        result['title'] = jmespath.search('data.videoDetailView.title', VideoDetail)
        result['category'] = jmespath.search('data.videoDetailView.type', VideoDetail)
        result['cover'] = jmespath.search('data.videoDetailView.cover', VideoDetail)
        result['description'] = jmespath.search('data.videoDetailView.brief', VideoDetail)
        result['tag'] = jmespath.search('data.videoDetailView.tagList[].name', VideoDetail)
        video_duration = jmespath.search('data.videoDetailView.duration', VideoDetail)
        result['duration'] = cal_duration(video_duration) if video_duration else None
        return result


def cal_duration(raw_duration_string):
    regex = re.compile("(\d{1,3}):?")
    _duration = regex.findall(raw_duration_string)
    duration = 0
    for num, i in enumerate(_duration[::-1]):
        duration += int(i) * (60 ** num)
    return duration


TEST_CASE = [
    "https://mobile.rr.tv/mission/#/share/video?id=1879897",
    "https://mobile.rr.tv/mission/#/share/video?id=1879530",
]
if __name__ == '__main__':
    import aiohttp
    from pprint import pprint


    async def test():
        async with aiohttp.ClientSession() as session_:
            return await entrance(
                webpage_url="https://mobile.rr.tv/mission/#/share/video?id=1879897",
                session=session_)


    loop = asyncio.get_event_loop()
    pprint(loop.run_until_complete(test()))
