#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 2019/7/7
# IDE: PyCharm

from aioVextractor import breaker
import math
import asyncio
# import aiohttp
# from aiostream.stream import takewhile
# from aioVextractor.utils.requests_retry import RequestRetry
# from aioVextractor.utils.user_agent import safari
# from random import choice
# import ujson as json
# from scrapy import Selector
from urllib.parse import (urlsplit, unquote)


# import jmespath
# import emoji
# import traceback
# import re
# import html

async def breakdown(webpage_url, cursor=0, offset=10):
    """
    breakdown each url from webpage_url which is a playlist url
    return title and cover of videos under webpage_url limit to certain range (cursor, offset)
    """
    ParseResult = urlsplit(webpage_url)
    netloc = ParseResult.netloc
    # path = ParseResult.path
    offset = math.ceil(float(int(offset) / 10)) * 10  ## limit it to be the integer multiple of 10
    if netloc == 'vimeo.com':
        for ele in await breaker.vimeo.breakdown(webpage_url=webpage_url,
                                                 cursor=cursor,
                                                 offset=offset):
            yield ele
    elif netloc == 'www.youtube.com':
        async for ele in breaker.youtube.breakdown(webpage_url=webpage_url):
            yield ele
    elif netloc == 'www.xinpianchang.com':

        async for ele in breaker.xinpianchang.breakdown(webpage_url=webpage_url,
                                                        cursor=cursor,
                                                        offset=offset):
            yield ele
    else:
        pass


if __name__ == '__main__':
    "https://vimeo.com/plaidavenger"
    "https://www.youtube.com/channel/UCSRpCBq2xomj7Sz0od73jWw/videos"
    "https://www.xinpianchang.com/u10002513?from=userList"
    res = []


    async def test():
        async for ele in breakdown(webpage_url='https://www.xinpianchang.com/u10002513?from=userList'):
            print(ele)
            res.append(ele['vid'])


    asyncio.run(test())
    print(f"res: {res}")
