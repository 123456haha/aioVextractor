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
                return await bilibili.entrance(webpage_url=webpage_url, session=session)
        elif netloc == 'v.douyin.com':
            return await douyin.entrance(webpage_url=webpage_url, session=session)
        elif netloc == 'www.eyepetizer.net':
            if constrain(path, '/detail.html'):
                return await eyepetizer.entrance(webpage_url=webpage_url, session=session)
        elif netloc == 'v.qq.com':
            if constrain(path, '/x/page/', '/x/cover/'):
                return await tencent.entrance(webpage_url=webpage_url, session=session)
        elif netloc in {'www.tvcf.co.kr',
                        'play.tvcf.co.kr'}:
            if constrain(path, '/YCf/V.asp', '/'):
                return await tvcf.entrance(webpage_url=webpage_url, session=session)
        elif netloc == 'vimeo.com':
            return await vimeo.entrance(webpage_url=webpage_url, session=session)
        elif netloc == 'www.xinpianchang.com':
            if constrain(path, '/a'):
                return await xinpianchang.entrance(webpage_url=webpage_url, session=session)
        elif netloc == 'v.youku.com':
            if constrain(path, '/v_show/id'):
                return await youku.entrance(webpage_url=webpage_url, session=session)
        elif netloc == 'www.youtube.com':
            if constrain(path, '/watch'):
                return await youtube.entrance(webpage_url=webpage_url, session=session)
        else:
            print(f'URL is not SUPPORTED {webpage_url}')
            return None
    except:
        traceback.print_exc()
        return False


def constrain(path, *constraint):
    return any([constraint in path for constraint in constraint])


if __name__ == '__main__':
    pass
