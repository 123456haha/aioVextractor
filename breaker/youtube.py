#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 2019/7/6
# IDE: PyCharm

import asyncio
import aiohttp
from aioVextractor import config
from aioVextractor.utils.requests_retry import RequestRetry
from aioVextractor.utils.user_agent import UserAgent
from random import choice
from urllib.parse import urlsplit
import jmespath
from aioVextractor.utils import paging
import re


async def breakdown(webpage_url,
                    cursor=config.DEFAULT_CURSOR,
                    offset=config.DEFAULT_OFFSET):
    ParseResult = urlsplit(webpage_url)
    path = ParseResult.path
    if all([isinstance(ele, int) for ele in [cursor, offset]]):
        pass
    else:
        print(f"The Type of cursor/offset is not integer: \n"
              f"type(cursor) = {type(cursor)}\n"
              f"type(offset) = {type(offset)}"
              )
        return False

    if re.match('/playlist', path):  ## https://www.youtube.com/playlist?list=PLohYzz4btpaSt2T0rcfmF8wfQzuW_6JTv
        api_step = 10
        results = []
        # offset = math.ceil(float(offset / 10)) * 10  ## limit it to be the integer multiple of 10
        while True:
            clips_list = await asyncio.gather(*[retrieve_user_pageing_api(webpage_url=webpage_url,
                                                                          page=page) for page in
                                                paging.pager(cursor=cursor, offset=offset, step=api_step)])
            for clips in clips_list:
                results += await extract_user_page(ResponseJson=clips)
                offset -= api_step
                if offset <= 0:
                    return results
                else:
                    if jmespath.search('clips_meta.has_next', clips):
                        continue
                    else:
                        return results

    elif re.match('/channel/', path):  ## https://www.youtube.com/channel/UC36FGmBEGfmOV2T5QVNI9ew
        api_step = 10
        results = []
        # offset = math.ceil(float(offset / 10)) * 10  ## limit it to be the integer multiple of 10
        while True:
            clips_list = await asyncio.gather(*[retrieve_user_pageing_api(webpage_url=webpage_url,
                                                                          page=page) for page in
                                                paging.pager(cursor=cursor, offset=offset, step=api_step)])
            for clips in clips_list:
                results += await extract_user_page(ResponseJson=clips)
                offset -= api_step
                if offset <= 0:
                    return results
                else:
                    if jmespath.search('clips_meta.has_next', clips):
                        continue
                    else:
                        return results

    elif re.match('/watch', path):
        return []
    else:
        print(f"webpage_url: {webpage_url}\n"
              f"does NOT MATCH any vimeo playlist pattern!")
        return []

async def retrieve_playlist_pageing_api(referer,):

    headers = {
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36',
        'accept': '*/*',
        'referer': referer,  ## https://www.youtube.com/playlist?list=PLCdifjPK2Xais9oLP9r9_PtfhPTK-eyew
        'authority': 'www.youtube.com',
    }

    params = (
        ('ctoken', '4qmFsgI2EiRWTFBMQ2RpZmpQSzJYYWlzOW9MUDlyOV9QdGZoUFRLLWV5ZXcaDmVnWlFWRHBEUjFFJTNE'),
        ('continuation', '4qmFsgI2EiRWTFBMQ2RpZmpQSzJYYWlzOW9MUDlyOV9QdGZoUFRLLWV5ZXcaDmVnWlFWRHBEUjFFJTNE'),
        ('itct', 'CC0QybcCIhMIjeHptcSi4wIVTm2LCh0PeglhKPos'),
    )

    response = requests.get('https://www.youtube.com/browse_ajax', headers=headers, params=params)

    async with aiohttp.ClientSession(raise_for_status=True) as session:
        headers = {'Accept-Encoding': 'gzip, deflate, br',
                   'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                   'User-Agent': choice(UserAgent),
                   'Accept': '*/*',
                   # 'Referer': 'https://vimeo.com/alitasmitmedia',
                   'X-Requested-With': 'XMLHttpRequest',
                   # 'Connection': 'keep-alive',
                   }

        params = {'action': 'get_profile_clips',
                  'page': page}
        async with session.get(webpage_url, headers=headers, params=params) as response:
            return await response.json()
if __name__ == '__main__':
    pass
