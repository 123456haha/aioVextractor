#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 2019/7/6
# IDE: PyCharm

import asyncio
import aiohttp
from aioVextractor.utils.requests_retry import RequestRetry
from aioVextractor.utils.user_agent import UserAgent
from random import choice
from urllib.parse import urlsplit
import jmespath
import re


async def breakdown(webpage_url, page = 1, params=None):
    ParseResult = urlsplit(webpage_url)
    path = ParseResult.path
    if re.match('/channels/.*', path):  ## https://vimeo.com/channels/ceiga
        ## do not supported
        return []
        # api_step = 5
        # results = []
        # # offset = math.ceil(float(offset / 10)) * 10  ## limit it to be the integer multiple of 10
        # while True:
        #     page_list = await asyncio.gather(*[retrieve_channel_page(webpage_url=webpage_url,
        #                                                               page=page) for page in
        #                                         paging.pager(cursor=cursor, offset=offset, step=api_step)])
        #     for page in page_list:
        #         results += await extract_channel_page(ResponseText=page)
        #         offset -= api_step
        #         if offset <= 0:
        #             return results
        #         else:
        #             if jmespath.search('clips_meta.has_next', clips):
        #                 continue
        #             else:
        #                 return results
    elif re.match('/\d{6,11}', path):  ## https://vimeo.com/281493330  ## this is single
        return []
    elif re.match('[/.*]', path):  ## https://vimeo.com/alitasmitmedia
        while True:
            clips_list = await asyncio.gather(*[retrieve_user_pageing_api(webpage_url=webpage_url, page=page)])
            for clips in clips_list:
                results = await extract_user_page(ResponseJson=clips, webpage_url=webpage_url)
                has_next = jmespath.search('clips_meta.has_next', clips)
                return results, has_next, {}
    else:
        print(f"webpage_url: {webpage_url}\n"
              f"does NOT MATCH any vimeo playlist pattern!")
        return []


@RequestRetry
async def retrieve_user_pageing_api(webpage_url, page=1):
    """
    request for vimeo user page paging api
    (i.e. https://vimeo.com/user49587354, https://vimeo.com/alitasmitmedia)
    :return: json from the response, containing 10 element in each response
    """
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


async def extract_user_page(ResponseJson, webpage_url):
    clips = ResponseJson
    try:  ## extract info from json/dict
        results = jmespath.search('clips[].{"title": title, '
                               '"cover": thumbnail.src, '
                               # '"cover": thumbnail.src_8x, '
                               '"duration": duration.raw, '
                               '"vid": clip_id, '
                               '"url": url, '
                               '"recommend": is_staffpick, '
                               '"comment_count": quickstats.total_comments.raw, '
                               '"like_count": quickstats.total_likes.raw, '
                               '"view_count": quickstats.total_plays.raw, '
                               '"author": user.name, '
                               '"author_id": user.id, '
                               '"author_url": user.url, '
                               '"author_avatar": user.thumbnail.src_8x}', clips)
    except TypeError:
        print(f"This clips cannot be extracted by breaker.vimeo.breakdown: {clips}")
        return []
    else:
        for ele in results:
            ele['author_url'] = "https://vimeo.com" + ele['author_url']
            ele['webpage_url'] = "https://vimeo.com" + ele['url']
            ele['playlist_url'] = webpage_url
            ele['from'] = "vimeo"
            ele.pop('url', None)
        return results


# @RequestRetry
# async def retrieve_channel_page(webpage_url, page=1):
#     """
#     request for vimeo channel page
#     (i.e. https://vimeo.com/channels/ceiga/page:1)
#     :return: text from the response, containing 5 element in each response
#     """
#     if webpage_url.startswith(':', -2):  ## https://vimeo.com/channels/ceiga/page:1
#         pass
#     else:  ## https://vimeo.com/channels/revengepromos/page:1
#         webpage_url += '/page:1'
#
#     async with aiohttp.ClientSession(raise_for_status=True) as session:
#         headers = {'Upgrade-Insecure-Requests': '1',
#                    'User-Agent': choice(UserAgent),
#                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
#                    # 'Referer': 'https://vimeo.com/channels/ceiga/page:3',
#                    # 'Connection': 'keep-alive',
#                    'Accept-Encoding': 'gzip, deflate, br',
#                    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
#                    }
#         components = webpage_url.split(':')
#         components[-1] = str(page)
#         url = ':'.join(components)
#         async with session.get(url, headers=headers) as response:
#             return await response.text()
#
# async def extract_channel_page(ResponseText):
#     selector = Selector(text=ResponseText)
#     results = []
#
#     return [], True


if __name__ == '__main__':
    # print(asyncio.run(retrieve_user_page("https://vimeo.com/alitasmitmedia", 1)))
    from pprint import pprint
    loop = asyncio.get_event_loop()
    _ = loop.run_until_complete(breakdown(webpage_url='https://vimeo.com/hellounion', page=1))
    pprint(_)
    print(sorted(jmespath.search('[0][].vid', list(_))))
    print(len(_[0]))
