#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 2019/7/6
# IDE: PyCharm

import asyncio
import aiohttp
from aioVextractor import config
import re
from aiostream.stream import takewhile
from aioVextractor.utils import paging
from urllib.parse import (urlparse, unquote)
import html
import emoji
import traceback
from random import choice
import jmespath
from aioVextractor.utils.user_agent import (UserAgent)
from aioVextractor.utils.requests_retry import RequestRetry
from scrapy import Selector
import time



async def breakdown(webpage_url,
                    page = 1,
                    params=None):
    """
    cursor is the current place of the video
    offset can only be the integer multiple of 10
    :return: list of title and cover
    """
    clips_list = await asyncio.gather(*[retrieve_user_paging_api(webpage_url=webpage_url, page=page)])
    for clips in clips_list:
        results = await extract_user_pageing_api(ResText=clips)
        return results
        # async for ele in takewhile(extract_user_pageing_api(ResText=clips), lambda x: isinstance(x, (dict, int))):
        #     yield ele
            # offset -= 1
            # if offset <= 0:
            #     break
            # yield results
        # else:
        #     if jmespath.search('clips_meta.has_next', clips):
        #         continue
        #     else:
        #         break
        # yield results


@RequestRetry
async def retrieve_user_paging_api(webpage_url, page=1):
    async with aiohttp.ClientSession() as session:
        url = "https://www.xinpianchang.com/index.php"
        xinpianchang_user_id = webpage_url.split('?')[0].split('/u')[-1]
        headers = {'Origin': "https://www.xinpianchang.com",
                   'Accept-Encoding': "gzip, deflate, br",
                   'Accept-Language': "zh-CN,zh;q=0.9,en;q=0.8,ko;q=0.7",
                   'User-Agent': choice(UserAgent),
                   'Accept': "*/*",
                   'Referer': webpage_url,
                   'X-Requested-With': "XMLHttpRequest",
                   'cache-control': "no-cache"}
        params = {"app": "user",
                  "ac": "space",
                  "ajax": "1",
                  "id": xinpianchang_user_id,
                  "d": "1",
                  "sort": "pick",
                  "cateid": "0",
                  "audit": "1",
                  "is_private": "0",
                  "page": page}
        async with session.post(url, headers=headers, params=params) as response:
            response_text = await response.text()
            return response_text


async def extract_user_pageing_api(ResText):
    try:
        selector = Selector(text=ResText)
    except TypeError:
        return None
    else:
        output = []
        for article in selector.css("li[data-articleid]"):
            ele = dict()
            ele['vid'] = article.css('::attr(data-articleid)').extract_first()
            ele['webpage_url'] = f"https://www.xinpianchang.com/a{ele['vid']}?from=UserProfile"
            ele['cover'] = article.css('img[class*="lazy-img"]::attr(_src)').extract_first()
            ele['upload_ts'] = format_upload_ts(article.css('.video-hover-con p[class*="fs_12"]::text').extract_first())
            ele['duration'] = format_duration(article.css('.duration::text').extract_first())
            ele['description'] = format_desc(article.css('.desc::text').extract_first())
            ele['title'] = format_desc(article.css('.video-con-top p::text').extract_first())
            ele['category'] = format_category(article.css('.new-cate .c_b_9 ::text').extract())
            ele['view_count'] = format_count(article.css('.icon-play-volume::text').extract_first())
            ele['like_count'] = format_count(article.css('.icon-like::text').extract_first())
            ele['role'] = article.css('.user-info .role::text').extract_first()
            ele['from'] = '新片场'
            output.append(ele)
            # yield ele
        else:
            has_more = selector.css("li[data-more]::attr(data-more)").extract_first()
            return output, has_more, {}


def format_duration(duration_str):
    """
    input: "17' 39''"
    """
    try:
        t1 = time.strptime(duration_str, "%M' %S''")
    except:
        return None
    t2 = time.struct_time((1900, 1, 1, 0, 0, 0, 0, 0, -1))
    try:
        duration = int(time.mktime(t1) - time.mktime(t2))
    except Exception:
        return None
    else:
        return duration


def format_category(category):
    """
    input: ['\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t系列短视频\t\t\t\t\t\t\t', '\n\t\t\t\t\t\t\t纪录 - 亲情\t\t\t\t\t\t\t']
    """
    return ",".join(list(map(lambda x: x.strip(), category))) if category else None


def format_upload_ts(upload_ts, detail=0):
    """
    input: '2019-05-14 发布'
    input: '2019-05-19T22:11:39+08:00'

    """
    if detail == 0:
        try:
            return int(time.mktime(time.strptime(upload_ts, '%Y-%m-%d 发布'))) if upload_ts else None
        except:
            traceback.print_exc()
            return None
    else:
        try:
            # upload_ts[:-6] -> '2019-05-19T22:11:39'
            return int(time.mktime(time.strptime(upload_ts[:-6], '%Y-%m-%dT%H:%M:%S'))) if upload_ts else None
        except:
            print(f"upload_ts: {upload_ts}")
            traceback.print_exc()
            return None


def format_desc(desc):
    try:
        return emoji.demojize(html.unescape(unquote(desc)))
    except:
        return desc

def format_count(num):
    try:
        if 'w' in num:
            return str(int(float(num.replace('w', '')) * 10000))
        else:
            return num
    except:
        traceback.print_exc()
        return num


if __name__ == '__main__':
    "https://www.xinpianchang.com/u10014261?from=userList"
    "https://www.xinpianchang.com/u10029931?from=userList"
    "https://www.xinpianchang.com/u10002513?from=userList"


    # async def test():
    #     res = await retrieve_user_paging_api("https://www.xinpianchang.com/u10029931?from=userList")
    #     async for ele in extract_user_pageing_api(res):
    #         print(ele)

    async def test():
        return await breakdown("https://www.xinpianchang.com/u10002513?from=userList", page=1)

    loop = asyncio.get_event_loop()
    _res = loop.run_until_complete(test())
    from pprint import pprint
    pprint(_res)