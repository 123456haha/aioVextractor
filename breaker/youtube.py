#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 2019/7/6
# IDE: PyCharm

import asyncio
import aiohttp
from aioVextractor import config
from aiostream.stream import takewhile
from aioVextractor.utils.requests_retry import RequestRetry
from aioVextractor.utils.user_agent import (safari, UserAgent, android)
from random import choice
import ujson as json
from scrapy import Selector
from urllib.parse import (urlsplit, unquote)
import jmespath
import traceback
# from itertools import takewhile
from aioVextractor.utils import paging
import re
import html


async def breakdown(webpage_url,
                    # cursor=config.DEFAULT_CURSOR,
                    # offset=config.DEFAULT_OFFSET
                    ):
    """
    paging using specific params(continuation, clickTrackingParams from ytInitialData) rather than pure page number
    Hence, yield all element one by one once extracted
    """
    ParseResult = urlsplit(webpage_url)
    path = ParseResult.path
    # if all([isinstance(ele, int) for ele in [cursor, offset]]):
    #     pass
    # else:
    #     print(f"The Type of cursor/offset is not integer: \n"
    #           f"type(cursor) = {type(cursor)}\n"
    #           f"type(offset) = {type(offset)}"
    #           )
    #     return False

    if re.match('/playlist', path):  ## https://www.youtube.com/playlist?list=PLohYzz4btpaSt2T0rcfmF8wfQzuW_6JTv
        webpage_content = await retrieve_webpapge(webpage_url=webpage_url)
        async for ele in takewhile(extract_webpage(webpage_content),
                                   lambda x: isinstance(x, (dict, tuple))):
            if isinstance(ele, dict):
                yield ele
            elif isinstance(ele, tuple):
                continuation, clickTrackingParams = ele
                has_more = True
                while has_more:
                    next_content = await retrieve_playlist_pageing_api(referer=webpage_url,
                                                                       continuation=continuation,
                                                                       clickTrackingParams=clickTrackingParams)
                    async for next_ele in extract_playlist_pageing_api(ResJson=next_content):
                        if isinstance(next_ele, dict):
                            yield next_ele
                        elif isinstance(next_ele, tuple):
                            continuation, clickTrackingParams = next_ele
                            continue
                        else:
                            has_more = False

    elif re.match('/channel/', path):  ## https://www.youtube.com/channel/UC36FGmBEGfmOV2T5QVNI9ew
        pass
        # api_step = 10
        # results = []
        # # offset = math.ceil(float(offset / 10)) * 10  ## limit it to be the integer multiple of 10
        # while True:
        #     clips_list = await asyncio.gather(*[retrieve_user_pageing_api(webpage_url=webpage_url,
        #                                                                   page=page) for page in
        #                                         paging.pager(cursor=cursor, offset=offset, step=api_step)])
        #     for clips in clips_list:
        #         results += await extract_user_page(ResponseJson=clips)
        #         offset -= api_step
        #         if offset <= 0:
        #             return results
        #         else:
        #             if jmespath.search('clips_meta.has_next', clips):
        #                 continue
        #             else:
        #                 return results

    elif re.match('/watch', path):
        yield []
    else:
        print(f"webpage_url: {webpage_url}\n"
              f"does NOT MATCH any vimeo playlist pattern!")
        yield []


@RequestRetry
async def retrieve_playlist_pageing_api(referer, continuation, clickTrackingParams):
    """
    retrieve next page response.
    each response contains 100 element at most.
    continuation and clickTrackingParams aRre retrieved from ytInitialData.
    """
    async with aiohttp.ClientSession(raise_for_status=True) as session:
        headers = {'accept-encoding': 'gzip, deflate, br',
                   'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
                   # 'x-youtube-page-label': 'youtube.ytfe.desktop_20190701_7_RC1',
                   # 'x-youtube-page-cl': '256172872',
                   'x-spf-referer': referer,
                   ## https://www.youtube.com/playlist?list=PLs54iBUqIopDv2wRhkqArl9AEV1PU-gmc
                   # 'x-youtube-utc-offset': '480',
                   'x-spf-previous': referer,
                   ## ## https://www.youtube.com/playlist?list=PLs54iBUqIopDv2wRhkqArl9AEV1PU-gmc
                   # 'cookie': 'YSC=HB8KtiI_O00; PREF=f1=50000000; GPS=1; VISITOR_INFO1_LIVE=k4wIJmME_Ws',
                   'x-youtube-client-version': '2.20190702',
                   'user-agent': choice(safari),
                   # 'x-youtube-variants-checksum': '97e19b7118dfdcc87ffff0d189fb17db',
                   'accept': '*/*',
                   'referer': 'https://www.youtube.com/playlist?list=PLs54iBUqIopDv2wRhkqArl9AEV1PU-gmc',
                   'x-youtube-client-name': '1',
                   'authority': 'www.youtube.com',
                   }

        params = {'ctoken': continuation,
                  ## 4qmFsgI0EiRWTFBMczU0aUJVcUlvcER2MndSaGtxQXJsOUFFVjFQVS1nbWMaDGVnZFFWRHBEVFdkQw%3D%3D
                  ## 4qmFsgI2EiRWTFBMczU0aUJVcUlvcER2MndSaGtxQXJsOUFFVjFQVS1nbWMaDmVnWlFWRHBEUjFFJTNE
                  'continuation': continuation,
                  ## 4qmFsgI2EiRWTFBMczU0aUJVcUlvcER2MndSaGtxQXJsOUFFVjFQVS1nbWMaDmVnWlFWRHBEUjFFJTNE
                  'itct': clickTrackingParams,
                  ## CAIQybcCIhMIsaKywqKk4wIVQ2-LCh2zrAjX
                  ## CEEQybcCIhMIq4f9kqOk4wIVmHgqCh27dQLSKPos
                  }
        async with session.get('https://www.youtube.com/browse_ajax', headers=headers, params=params) as response:
            return await response.json()


async def extract_playlist_pageing_api(ResJson):
    """
    extract playlist webpage by extracting ytInitialData
    yield each element and follow by (continuation, clickTrackingParams) at last
    """
    ytInitialData = ResJson
    # print(ytInitialData)
    results = jmespath.search('[1].response.continuationContents.playlistVideoListContinuation.'
                              'contents[].playlistVideoRenderer.{'
                              '"duration": lengthSeconds, '
                              '"vid": videoId, '
                              '"cover": thumbnail.thumbnails[-1].url, '
                              '"title": title.simpleText, '  ## need to be unescaped(html)
                              '"webpage_url": navigationEndpoint.commandMetadata.webCommandMetadata.url '  ## need to be joined  ## '/watch?v=PRT3FjaP71E&list=PLs54iBUqIopDv2wRhkqArl9AEV1PU-gmc&index=101&t=0s'
                              '}', ytInitialData)
    if isinstance(results, list):
        pass
    else:
        print(f"ResJson: {ResJson}")
        yield None
    for ele in results:
        ele['title'] = unquote(html.unescape(ele['title']))
        ele['webpage_url'] = 'https://www.youtube.com/' + ele['webpage_url']
        yield ele
    else:
        try:
            continuation, clickTrackingParams = jmespath.search('[1].'
                                                                'response.'
                                                                'continuationContents.'
                                                                'playlistVideoListContinuation.'
                                                                'continuations[0].'
                                                                'nextContinuationData.'
                                                                '[continuation, clickTrackingParams]',
                                                                ytInitialData)
        except TypeError:  ## cannot unpack non-iterable NoneType object
            ## [continuation, clickTrackingParams] do not exist
            yield None
        else:
            # print(continuation, clickTrackingParams)
            yield continuation, clickTrackingParams


@RequestRetry
async def retrieve_webpapge(webpage_url):
    """retrieve playlist webpage"""
    async with aiohttp.ClientSession(raise_for_status=True) as session:
        headers = {'authority': 'www.youtube.com',
                   # 'cache-control': 'max-age=0',
                   'upgrade-insecure-requests': '1',
                   # 'user-agent': choice(UserAgent),
                   'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.108 Safari/537.36',
                   'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
                   'accept-encoding': 'gzip, deflate, br',
                   'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
                   # 'cookie': 'YSC=HB8KtiI_O00; PREF=f1=50000000; VISITOR_INFO1_LIVE=k4wIJmME_Ws',
                   }
        async with session.get(webpage_url, headers=headers) as response:
            return await response.text()


async def extract_webpage(ResText):
    """
    extract playlist webpage by extracting ytInitialData
    yield each element and follow by (continuation, clickTrackingParams) at last
    """
    try:
        selector = Selector(text=ResText)
    except ValueError:
        traceback.print_exc()
        yield None  ## None is returned
    else:
        try:
            ytInitialData = json.loads(selector.css('script').re_first(
                'window\["ytInitialData"\] = ({[\s|\S]*?});[\s|\S]*?window\["ytInitialPlayerResponse"\]'))
        except TypeError:
            traceback.print_exc()
            yield None  ## None is returned
        # print(ytInitialData)
        else:
            results = jmespath.search('contents.'
                                      'twoColumnBrowseResultsRenderer.'
                                      'tabs[0].'
                                      'tabRenderer.'
                                      'content.'
                                      'sectionListRenderer.'
                                      'contents[0].'
                                      'itemSectionRenderer.'
                                      'contents[0].'
                                      'playlistVideoListRenderer.'
                                      'contents[].playlistVideoRenderer.{'
                                      '"duration": lengthSeconds, '
                                      '"vid": videoId, '
                                      '"cover": thumbnail.thumbnails[-1].url, '
                                      '"title": title.simpleText, '  ## need to be unescaped(html)
                                      '"webpage_url": navigationEndpoint.commandMetadata.webCommandMetadata.url '  ## need to be joined  ## '/watch?v=PRT3FjaP71E&list=PLs54iBUqIopDv2wRhkqArl9AEV1PU-gmc&index=101&t=0s'
                                      '}', ytInitialData)
            for ele in results:
                ele['title'] = unquote(html.unescape(ele['title']))
                ele['webpage_url'] = 'https://www.youtube.com/' + ele['webpage_url']
                yield ele
            else:
                continuation, clickTrackingParams = jmespath.search('contents.'
                                                                    'twoColumnBrowseResultsRenderer.'
                                                                    'tabs[0].'
                                                                    'tabRenderer.'
                                                                    'content.'
                                                                    'sectionListRenderer.'
                                                                    'contents[0].'
                                                                    'itemSectionRenderer.'
                                                                    'contents[0].'
                                                                    'playlistVideoListRenderer.'
                                                                    'continuations[0].'
                                                                    'nextContinuationData.'
                                                                    '[continuation, clickTrackingParams]',
                                                                    ytInitialData)
                # print(continuation, clickTrackingParams)
                yield continuation, clickTrackingParams


if __name__ == '__main__':
    from pprint import pprint


    # _ = asyncio.run(retrieve_playlist_pageing_api(
    #     referer='https://www.youtube.com/playlist?list=PLs54iBUqIopDv2wRhkqArl9AEV1PU-gmc',
    #     continuation='4qmFsgI0EiRWTFBMczU0aUJVcUlvcER2MndSaGtxQXJsOUFFVjFQVS1nbWMaDGVnZFFWRHBEVFdkQw%3D%3D',
    #     clickTrackingParams='CAIQybcCIhMIsaKywqKk4wIVQ2-LCh2zrAjX'))
    # print(_)
    # async def test():
    #     async for ele in extract_playlist_pageing_api(_):
    #         print(ele)
    # _ = asyncio.run(test())
    # print(_)

    # _ = asyncio.run(
    #     retrieve_webpapge(webpage_url='https://www.youtube.com/playlist?list=PLs54iBUqIopDv2wRhkqArl9AEV1PU-gmc', ))
    # async def test():
    #     async for ele in extract_webpage(_):
    #         # print(ele)
    #         print(type(ele))
    # _ = asyncio.run(test())
    res = []
    async def test():
        async for ele in breakdown(
                webpage_url='https://www.youtube.com/playlist?list=PLs54iBUqIopDv2wRhkqArl9AEV1PU-gmc'):
            res.append(ele)
        return res
            # print(type(ele))


    _ = asyncio.run(test())
    print(res)
