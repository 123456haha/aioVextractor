#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 2019/7/7
# IDE: PyCharm

from urllib.parse import urlsplit
from aioVextractor import breaker
import math

async def breakdown(webpage_url, cursor=0, offset=10):
    """
    breakdown each url from webpage_url which is a playlist url
    return title and cover of videos under webpage_url limit to certain range (cursor, offset)
    """
    ParseResult = urlsplit(webpage_url)
    netloc = ParseResult.netloc
    # path = ParseResult.path
    offset = math.ceil(float(offset / 10)) * 10  ## limit it to be the integer multiple of 10
    if netloc == 'vimeo.com':
        return breaker.vimeo.breakdown(webpage_url=webpage_url, cursor=cursor, offset=offset)
    elif netloc == 'www.youtube.com':
        breaker.youtube.breakdown(webpage_url=webpage_url, cursor=cursor, offset=offset)
    elif netloc == 'www.xinpianchang.com':
        breaker.xinpianchang.breakdown(webpage_url=webpage_url, cursor=cursor, offset=offset)
    else:
        pass

if __name__ == '__main__':
    pass