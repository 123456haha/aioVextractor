#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 2019/7/2
# IDE: PyCharm

import traceback
import re
from extractor import *


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
            if re.match('/\d{6,11}', path):
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
        elif "www.instagram.com" == netloc:
            res = await instagram.entrance(webpage_url=webpage_url, session=session)
            return res
        elif "carben.me" == netloc:
            res = await carben.entrance(webpage_url=webpage_url, session=session)
            return res
        elif "lanfanapp.com" == netloc:
            res = await lanfan.entrance(webpage_url=webpage_url, session=session)
            return res
        elif "www.digitaling.com" == netloc:
            res = await digitaling.entrance(webpage_url=webpage_url, session=session)
            return res
        elif "www.pinterest.com" == netloc:
            res = await pinterest.entrance(webpage_url=webpage_url, session=session)
            return res
        elif "creative.adquan.com" == netloc:
            res = await adquan.entrance(webpage_url=webpage_url, session=session)
            return res
        elif "www.adquan.com" == netloc:
            res = await adquan.entrance(webpage_url=webpage_url, session=session)
            return res
        elif "blog.naver.com" == netloc:
            res = await naver.entrance(webpage_url=webpage_url, session=session)
            return res
        elif "mobile.rr.tv" == netloc:
            res = await renren.entrance(webpage_url=webpage_url, session=session)
            return res
        elif "socialbeta.com" == netloc:
            res = await socialbeta.entrance(webpage_url=webpage_url, session=session)
            return res
        elif "www.vmovier.com" == netloc:
            res = await vmovier.entrance(webpage_url=webpage_url, session=session)
            return res
        elif "iwebad.com" == netloc:
            res = await iwebad.entrance(webpage_url=webpage_url, session=session)
            return res
        else:
            print(f"USING THE COMMON EXTRACTOR")
            res = await common.extract_info(webpage_url, collaborate=False)
            if isinstance(res, (dict, list)):
                return res
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
