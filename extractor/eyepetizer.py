#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 2019/6/20
# IDE: PyCharm

import jmespath
import re
from utils.user_agent import UserAgent
from random import choice
import config
import traceback
from asyncio import TimeoutError
from aiohttp.client_exceptions import (ServerDisconnectedError, ServerConnectionError, ClientOSError,
                                       ClientConnectorCertificateError, ServerTimeoutError, ContentTypeError,
                                       ClientConnectorError, ClientPayloadError)


async def entrance(webpage_url, session, chance_left=config.RETRY):
    try:
        vid = re.compile('vid=([\d]*)').search(webpage_url)[1]
    except (IndexError, TypeError):
        traceback.print_exc()
        return False
    else:
        download_headers = {'Accept': '*/*',
                            'Referer': webpage_url,
                            'Origin': 'https://www.eyepetizer.net',
                            'User-Agent': choice(UserAgent)}

        params = {'f': 'web'}
        response_url = 'https://baobab.kaiyanapp.com/api/v1/video/{}'.format(vid)
        try:
            async with session.get(response_url, headers=download_headers, params=params) as response:
                response_json = await response.json()
        except (ServerDisconnectedError, ServerConnectionError, ClientOSError,
                ClientConnectorCertificateError, ServerTimeoutError, ContentTypeError,
                ClientConnectorError, ClientPayloadError, TimeoutError):
            if chance_left != 1:
                return await entrance(webpage_url=webpage_url, session=session, chance_left=chance_left - 1)
            else:
                return False
        except:
            traceback.print_exc()
            return False
        else:
            return extract(response_json)

def extract(response_json):
    result = dict()
    result['title'] = jmespath.search('title', response_json)
    result['author'] = jmespath.search('author.name', response_json)
    result['author_description'] = jmespath.search('author.description', response_json)
    result['author_avatar'] = jmespath.search('author.icon', response_json)
    result['author_videoNum'] = jmespath.search('author.videoNum', response_json)
    result['category'] = jmespath.search('category', response_json)
    video_create_time = jmespath.search('date', response_json)
    result['upload_ts'] = int(video_create_time / 1000) if video_create_time else None
    result['description'] = jmespath.search('description', response_json)
    result['duration'] = jmespath.search('duration', response_json)
    result['vid'] = jmespath.search('id', response_json)
    result['play_addr'] = jmespath.search('max_by(playInfo, &height).url', response_json)
    result['tags'] = jmespath.search('tags[*].name', response_json)
    result['cover'] = jmespath.search('coverForFeed', response_json)
    return result


if __name__ == '__main__':
    import asyncio
    import aiohttp
    from pprint import pprint
    "https://www.eyepetizer.net/detail.html?vid=119611&utm_campaign=routine&utm_medium=share&utm_source=others&uid=0&resourceType=video&udid=1bb9f2f14545490c9168f7b99d89136e8ff14724&vc=443&vn=4.9.1&size=1080X1920&deviceModel=vivo%20X9&first_channel=eyepetizer_vivo_market&last_channel=eyepetizer_vivo_market&system_version_code=25"
    async def test():
        async with aiohttp.ClientSession() as session_:
            return await entrance(webpage_url="https://www.eyepetizer.net/detail.html?vid=119611&utm_campaign=routine&utm_medium=share&utm_source=others&uid=0&resourceType=video&udid=1bb9f2f14545490c9168f7b99d89136e8ff14724&vc=443&vn=4.9.1&size=1080X1920&deviceModel=vivo%20X9&first_channel=eyepetizer_vivo_market&last_channel=eyepetizer_vivo_market&system_version_code=25",
                                  session=session_)
    pprint(asyncio.run(test()))
