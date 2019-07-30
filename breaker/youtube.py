#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 2019/7/6
# IDE: PyCharm

import asyncio
import aiohttp
from aiostream.stream import takewhile
from aioVextractor.utils.requests_retry import RequestRetry
from aioVextractor.utils.user_agent import safari
from random import choice
import ujson as json
from scrapy import Selector
from urllib.parse import (urlsplit, unquote)
import jmespath
import emoji
import traceback
import re
import html


async def breakdown(webpage_url,
                    page=1,
                    params=None):
    """
    paging using specific params(continuation, clickTrackingParams from ytInitialData) rather than pure page number
    Hence, yield all element one by one once extracted
    """
    ParseResult = urlsplit(webpage_url)
    path = ParseResult.path
    if re.match('/playlist', path):  ## https://www.youtube.com/playlist?list=PLohYzz4btpaSt2T0rcfmF8wfQzuW_6JTv
        if params:
            webpage_content = await retrieve_youtube_pageing_api(referer=webpage_url,
                                                                 continuation=params['continuation'],
                                                                 clickTrackingParams=params['clickTrackingParams'])
            results = await extract_youtube_pageing_api(ResJson=webpage_content, path='playlist')
            return results
        else:
            webpage_content = await retrieve_webpapge(webpage_url=webpage_url)
            results = await extract_webpage(webpage_content, path='playlist')
            return results
        # async for ele in takewhile(extract_webpage(webpage_content, path='playlist'),
        #                            lambda x: isinstance(x, (dict, tuple))):
        #     if isinstance(ele, dict):
        #         yield ele
        #     elif isinstance(ele, tuple):
        #         continuation, clickTrackingParams = ele
        #         has_more = True
        #         while has_more:
        #             next_content = await retrieve_youtube_pageing_api(referer=webpage_url,
        #                                                               continuation=continuation,
        #                                                               clickTrackingParams=clickTrackingParams)
        #             async for next_ele in extract_youtube_pageing_api(ResJson=next_content, path='playlist'):
        #                 if isinstance(next_ele, dict):
        #                     yield next_ele
        #                 elif isinstance(next_ele, tuple):
        #                     continuation, clickTrackingParams = next_ele
        #                     continue
        #                 else:
        #                     has_more = False
        #                     break

    elif re.match('/channel/', path) or re.match('/user/', path):  ## https://www.youtube.com/channel/UC36FGmBEGfmOV2T5QVNI9ew
        if params:
            webpage_content = await retrieve_youtube_pageing_api(referer=webpage_url,
                                                                 continuation=params['continuation'],
                                                                 clickTrackingParams=params['clickTrackingParams'])
            results = await extract_youtube_pageing_api(ResJson=webpage_content, path='channel')
            return results
        else:
            webpage_url += '' if webpage_url.endswith('/videos') else '/videos'
            webpage_content = await retrieve_webpapge(webpage_url=webpage_url)
            results = await extract_webpage(webpage_content, path='channel')
            return results
        # if isinstance(results, tuple):
        # # async for ele in takewhile(extract_webpage(webpage_content, path='channel'),
        # #                            lambda x: isinstance(x, (dict, tuple))):
        #     if isinstance(ele, dict):
        #         yield ele
        #     elif isinstance(ele, tuple):
        #         continuation, clickTrackingParams = ele
        #         has_more = True
        #         while has_more:
        #             next_content = await retrieve_youtube_pageing_api(referer=webpage_url,
        #                                                               continuation=continuation,
        #                                                               clickTrackingParams=clickTrackingParams)
        #             async for next_ele in extract_youtube_pageing_api(ResJson=next_content, path='channel'):
        #                 if isinstance(next_ele, dict):
        #                     yield next_ele
        #                 elif isinstance(next_ele, tuple):
        #                     continuation, clickTrackingParams = next_ele
        #                     continue
        #                 else:
        #                     has_more = False
        #                     break

    elif re.match('/watch', path):
        return []
    else:
        print(f"webpage_url: {webpage_url}\n"
              f"does NOT MATCH any vimeo playlist pattern!")
        return []


@RequestRetry
async def retrieve_youtube_pageing_api(referer, continuation, clickTrackingParams):
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


async def extract_youtube_pageing_api(ResJson, path='playlist'):
    """
    extract playlist webpage by extracting ytInitialData
    yield each element and follow by (continuation, clickTrackingParams) at last
    """
    ytInitialData = ResJson
    # print(ytInitialData)
    if path == 'playlist':
        statement = '[1].' \
                    'response.' \
                    'continuationContents.' \
                    'playlistVideoListContinuation.' \
                    'contents[].playlistVideoRenderer.{' \
                    '"duration": lengthSeconds, ' \
                    '"view_count": viewCountText.simpleText, ' \
                    '"vid": videoId, ' \
                    '"cover": thumbnail.thumbnails[-1].url, ' \
                    '"title": title.simpleText, ' \
                    '"webpage_url": navigationEndpoint.commandMetadata.webCommandMetadata.url ' \
                    '}'
        results = jmespath.search(statement, ytInitialData)
    else:  ## path == 'channel'
        statement = '[1].' \
                    'response.' \
                    'continuationContents.' \
                    'gridContinuation.' \
                    'items[].gridVideoRenderer.{' \
                    '"view_count": viewCountText.simpleText, ' \
                    '"vid": videoId, ' \
                    '"cover": thumbnail.thumbnails[-1].url, ' \
                    '"title": title.simpleText, ' \
                    '"webpage_url": navigationEndpoint.commandMetadata.webCommandMetadata.url ' \
                    '}'
        results = jmespath.search(statement, ytInitialData)
        if results is None:
            statement = 'response.' \
                        'continuationContents.' \
                        'gridContinuation.' \
                        'items[].gridVideoRenderer.{' \
                        '"view_count": viewCountText.simpleText, ' \
                        '"vid": videoId, ' \
                        '"cover": thumbnail.thumbnails[-1].url, ' \
                        '"title": title.simpleText, ' \
                        '"webpage_url": navigationEndpoint.commandMetadata.webCommandMetadata.url ' \
                        '}'
            results = jmespath.search(statement, ytInitialData)
    if isinstance(results, list):
        pass
    else:
        print(f"ytInitialData: {ytInitialData}")
        print(f"results: {results}")
        return None
    output = []
    for ele in results:
        try:
            ele['title'] = emoji.demojize(unquote(html.unescape(ele['title'])))
        except TypeError:
            traceback.print_exc()
            print(f"ele: {ele}")
            pass
        ele['webpage_url'] = 'https://www.youtube.com' + ele['webpage_url']
        ele['view_count'] = ele['view_count'].replace(',', '').replace(' 次观看', '') if ele['view_count'] else None
        ele['from'] = 'youtube'
        output.append(ele)
        # yield ele
    else:
        try:
            if path == 'playlist':
                statement = '[1].' \
                            'response.' \
                            'continuationContents.' \
                            'playlistVideoListContinuation.' \
                            'continuations[0].' \
                            'nextContinuationData.' \
                            '[continuation, clickTrackingParams]'
            else:  ## path == 'channel'
                statement = '[1].' \
                            'response.' \
                            'continuationContents.' \
                            'gridContinuation.' \
                            'continuations[0].' \
                            'nextContinuationData.' \
                            '[continuation, clickTrackingParams]'

            continuation, clickTrackingParams = jmespath.search(statement, ytInitialData)
        except TypeError:  ## cannot unpack non-iterable NoneType object
            traceback.print_exc()
            print(f"ytInitialData: {ytInitialData}")
            ## [continuation, clickTrackingParams] do not exist
            return output, False, {}
        else:
            # print(continuation, clickTrackingParams)
            return output, True, {"continuation": continuation, "clickTrackingParams": clickTrackingParams}


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


async def extract_webpage(ResText, path='playlist'):
    """
    extract playlist webpage by extracting ytInitialData
    yield each element and follow by (continuation, clickTrackingParams) at last
    """
    try:
        selector = Selector(text=ResText)
    except ValueError:
        traceback.print_exc()
        return None  ## None is returned
    else:
        try:
            try:
                ytInitialData = json.loads(json.
                                           loads(selector.
                                                 css('script').
                                                 re_first('window\["ytInitialData"] = JSON.parse\((.*?)\);')))
            except TypeError:
                ytInitialData = json.loads(selector.css('script').re_first(
                    'window\["ytInitialData"\] = ({[\s|\S]*?});[\s|\S]*?window\["ytInitialPlayerResponse"\]'))
        except TypeError:
            traceback.print_exc()
            return None  ## None is returned
        # print(ytInitialData)
        else:
            if path == 'playlist':
                statement = 'contents.' \
                            'twoColumnBrowseResultsRenderer.' \
                            'tabs[0].' \
                            'tabRenderer.' \
                            'content.' \
                            'sectionListRenderer.' \
                            'contents[0].' \
                            'itemSectionRenderer.' \
                            'contents[0].' \
                            'playlistVideoListRenderer.' \
                            'contents[].playlistVideoRenderer.{' \
                            '"duration": lengthSeconds, ' \
                            '"vid": videoId, ' \
                            '"cover": thumbnail.thumbnails[-1].url, ' \
                            '"title": title.simpleText, ' \
                            '"webpage_url": navigationEndpoint.commandMetadata.webCommandMetadata.url ' \
                            '}'
                results = jmespath.search(statement, ytInitialData)
            else:  ## path == 'channel':
                statement = 'contents.' \
                            'twoColumnBrowseResultsRenderer.' \
                            'tabs[1].' \
                            'tabRenderer.' \
                            'content.' \
                            'sectionListRenderer.' \
                            'contents[0].' \
                            'itemSectionRenderer.' \
                            'contents[0].' \
                            'gridRenderer.' \
                            'items[].gridVideoRenderer.{' \
                            '"vid": videoId, ' \
                            '"cover": thumbnail.thumbnails[-1].url, ' \
                            '"title": title.simpleText, ' \
                            '"webpage_url": navigationEndpoint.commandMetadata.webCommandMetadata.url ' \
                            '}'
                results = jmespath.search(statement, ytInitialData)
                if results is None:
                    statement = 'contents.' \
                                'twoColumnBrowseResultsRenderer.' \
                                'tabs[0].' \
                                'tabRenderer.' \
                                'content.' \
                                'sectionListRenderer.' \
                                'contents[0].' \
                                'itemSectionRenderer.' \
                                'contents[0].' \
                                'shelfRenderer.' \
                                'content.' \
                                'horizontalListRenderer.' \
                                'items[].gridVideoRenderer.{' \
                                '"vid": videoId, ' \
                                '"cover": thumbnail.thumbnails[-1].url, ' \
                                '"title": title.simpleText, ' \
                                '"webpage_url": navigationEndpoint.commandMetadata.webCommandMetadata.url ' \
                                '}'
                    results = jmespath.search(statement, ytInitialData)
            if results is None:
                print(f"Cannot extract ytInitialData: {ytInitialData}")
                return None
            output = []
            for ele in results:
                try:
                    ele['title'] = unquote(html.unescape(ele['title']))
                except TypeError:
                    pass
                ele['webpage_url'] = 'https://www.youtube.com' + ele['webpage_url']
                ele['from'] = 'youtube'
                output.append(ele)
                # yield ele
            else:
                if path == 'playlist':
                    statement = 'contents.' \
                                'twoColumnBrowseResultsRenderer.' \
                                'tabs[0].' \
                                'tabRenderer.' \
                                'content.' \
                                'sectionListRenderer.' \
                                'contents[0].' \
                                'itemSectionRenderer.' \
                                'contents[0].' \
                                'playlistVideoListRenderer.' \
                                'continuations[0].' \
                                'nextContinuationData.' \
                                '[continuation, clickTrackingParams]'
                else:  ## path == 'channel':
                    statement = 'contents.' \
                                'twoColumnBrowseResultsRenderer.' \
                                'tabs[1].' \
                                'tabRenderer.' \
                                'content.' \
                                'sectionListRenderer.' \
                                'contents[0].' \
                                'itemSectionRenderer.' \
                                'contents[0].' \
                                'gridRenderer.' \
                                'continuations[0].' \
                                'nextContinuationData.' \
                                '[continuation, clickTrackingParams]'
                    result = jmespath.search(statement, ytInitialData)
                    if result is None:
                        statement = 'contents.' \
                                    'twoColumnBrowseResultsRenderer.' \
                                    'tabs[0].' \
                                    'tabRenderer.' \
                                    'content.' \
                                    'sectionListRenderer.' \
                                    'contents[0].' \
                                    'itemSectionRenderer.' \
                                    'contents[0].' \
                                    'shelfRenderer.' \
                                    'content.' \
                                    'horizontalListRenderer.' \
                                    'continuations[0].' \
                                    'nextContinuationData.' \
                                    '[continuation, clickTrackingParams]'

                try:
                    continuation, clickTrackingParams = jmespath.search(statement, ytInitialData)
                except TypeError:  ## cannot unpack non-iterable NoneType object\
                    traceback.print_exc()
                    return output, False, {}
                    # yield None
                else:
                    # print(continuation, clickTrackingParams)
                    return output, True, {"continuation": continuation, "clickTrackingParams": clickTrackingParams}
                    # yield continuation, clickTrackingParams


if __name__ == '__main__':
    from pprint import pprint

    "https://www.youtube.com/channel/UCSRpCBq2xomj7Sz0od73jWw/videos"
    "https://www.youtube.com/channel/UCAyj5vEhoaw6fDFBpSbQvRg"
    "https://www.youtube.com/playlist?list=PLs54iBUqIopDv2wRhkqArl9AEV1PU-gmc"
    loop = asyncio.get_event_loop()
    _ = loop.run_until_complete(
        breakdown(webpage_url='https://www.youtube.com/playlist?list=PLs54iBUqIopDv2wRhkqArl9AEV1PU-gmc',
                  page=2,
                  params={'clickTrackingParams': 'CEEQybcCIhMIrKLi9_C-4wIVW28qCh3phwWaKPos',
  'continuation': '4qmFsgI2EiRWTFBMczU0aUJVcUlvcER2MndSaGtxQXJsOUFFVjFQVS1nbWMaDmVnWlFWRHBEUjFFJTNE'}
    ))
    pprint(_)
    print(sorted(jmespath.search('[0][].vid', list(_))))
    print(len(_[0]))
