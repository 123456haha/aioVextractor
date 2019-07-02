#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 2019/6/20
# IDE: PyCharm


import jmespath
import time
from urllib.parse import urlparse
from asyncio import TimeoutError
from .. import config
import traceback
import re
from ..utils.exception import exception

now = lambda: time.time()


async def entrance(webpage_url, session, chance_left=config.RETRY):
    try:
        webpage_url = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]| [! *(),] |(?: %[0-9a-fA-F][0-9a-fA-F]))+', webpage_url)[0]
    except IndexError:
        return False
    download_headers = {'Connection': 'keep-alive',
                            'Upgrade-Insecure-Requests': '1',
                            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
                            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                            'Accept-Encoding': 'gzip, deflate',
                            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,ko;q=0.7'}
    try:
        async with session.get(webpage_url, headers=download_headers, allow_redirects=False) as response_getinfo:
            Location = response_getinfo.headers['Location']
    except exception:
        if chance_left != 1:
            return await entrance(webpage_url=webpage_url, session=session, chance_left=chance_left - 1)
        else:
            return False
    except:
        traceback.print_exc()
        return False
    else:
        get_aweme_id = lambda L: urlparse(L).path.strip('/').split('/')[-1]
        aweme_id = get_aweme_id(Location)
        return extract(response_json=await aweme_detail(aweme_id=aweme_id,
                                                        session=session))


async def aweme_detail(aweme_id, session, chance_left=config.RETRY):
    """
    get all info of the video
    """
    api = 'https://aweme.snssdk.com/aweme/v1/aweme/detail/'
    aweme_detail_headers = {'Host': 'aweme.snssdk.com',
                            'sdk-version': '1',
                            'X-SS-TC': '0',
                            'User-Agent': 'com.ss.android.ugc.aweme/400 (Linux; U; Android 7.1.2; zh_CN; vivo X9; Build/N2G47H; Cronet/58.0.2991.0)',
                            'X-Pods': ''}
    aweme_detail_params = (('aweme_id', str(aweme_id)),
                           ('retry_type', 'no_retry'),
                           ('mcc_mnc', '46001'),
                           ('iid', '56611278631'),
                           ('device_id', '46086810620'),
                           ('ac', 'wifi'),
                           ('channel', 'vivo'),
                           ('aid', '1128'),
                           ('app_name', 'aweme'),
                           ('version_code', '400'),
                           ('version_name', '4.0.0'),
                           ('device_platform', 'android'),
                           ('ssmix', 'a'),
                           ('device_type', 'vivo X9'),
                           ('device_brand', 'vivo'),
                           ('language', 'zh'),
                           ('os_api', '25'),
                           ('os_version', '7.1.2'),
                           ('uuid', '864551033997690'),
                           ('openudid', 'f9b692782e50a622'),
                           ('manifest_version_code', '400'),
                           ('resolution', '1080*1920'),
                           ('dpi', '480'),
                           ('update_version_code', '4002'),
                           ('_rticket', int(now() * 1000)),
                           ('ts', int(now())),
                           ('js_sdk_version', '1.6.4'))
    try:
        async with session.get(api,
                               headers=aweme_detail_headers,
                               params=aweme_detail_params) as response:
            response_json = await response.json()
    except exception:
        if chance_left != 1:
            return await aweme_detail(aweme_id=aweme_id,
                                      session=session,
                                      chance_left=chance_left - 1)
        else:
            return False
    except:
        traceback.print_exc()
        return False
    else:
        return jmespath.search('aweme_detail', response_json)


def extract(response_json):
    """
    extract all info from response_json
    """
    if response_json is False:
        return False
    else:
        result = dict()
        result['author'] = jmespath.search('author.nickname', response_json)
        result['author_avatar'] = jmespath.search('author.avatar_larger.url_list[0]', response_json)
        result['author_description'] = jmespath.search('author.signature', response_json)
        author_gender = jmespath.search('author.gender', response_json)
        if author_gender==2:
            result['author_gender'] = '女'
        elif author_gender ==1:
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
        result['tags'] = jmespath.search('text_extra[].hashtag_name', response_json)
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


if __name__ == '__main__':
    import asyncio
    import aiohttp
    from pprint import pprint
    async def test():
        async with aiohttp.ClientSession() as session_:
            return await entrance(webpage_url="#在抖音，记录美好生活#球球老婆怀孕之后就爱睡这个洗脸巢 睡姿也太可爱了8#猫 http://v.douyin.com/hd9sb3/ 复制此链接，打开【抖音短视频】，直接观看视频！",
                                  session=session_)
    pprint(asyncio.run(test()))
