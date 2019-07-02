#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 2019/7/2
# IDE: PyCharm

import traceback
from extractor import (bilibili,
                       douyin,
                       eyepetizer,
                       tencent,
                       tvcf,
                       vimeo,
                       xinpianchang,
                       youku,
                       youtube)

async def distribute(webpage_url, netloc, path, session):
    try:
        if netloc == 'www.bilibili.com':
            if '/video' in path:
                return bilibili.entrance(webpage_url=webpage_url, session=session)
        elif netloc == 'v.douyin.com':
            return douyin.entrance(webpage_url=webpage_url, session=session)
        elif netloc == 'www.eyepetizer.net':
            if constrain(path, '/detail.html'):
                return eyepetizer.entrance(webpage_url=webpage_url, session=session)
        elif netloc == 'v.qq.com':
            if constrain(path, '/x/page/', '/x/cover/'):
                return tencent.entrance(webpage_url=webpage_url, session=session)
        elif netloc in {'www.tvcf.co.kr',
                        'play.tvcf.co.kr'}:
            if constrain(path, '/YCf/V.asp', '/'):
                return tvcf.entrance(webpage_url=webpage_url, session=session)
        elif netloc == 'vimeo.com':
            return vimeo.entrance(webpage_url=webpage_url, session=session)
        elif netloc == 'www.xinpianchang.com':
            if constrain(path, '/a'):
                return xinpianchang.entrance(webpage_url=webpage_url, session=session)
        elif netloc == 'v.youku.com':
            if constrain(path, '/v_show/id'):
                return youku.entrance(webpage_url=webpage_url, session=session)
        elif netloc == 'www.youtube.com':
            if constrain(path, '/watch'):
                return youtube.entrance(webpage_url=webpage_url, session=session)
        else:
            return f'URL is not SUPPORTED {webpage_url}'
    except:
        traceback.print_exc()
        return False

def constrain(path, *constraint):
    return any([constraint in path for constraint in constraint])


if __name__ == '__main__':
    pass
