#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 2019/6/20
# IDE: PyCharm


import jmespath
import traceback
from aioVextractor.utils.user_agent import android
import os
import re
import asyncio
import platform

if platform.system() in {"Linux", "Darwin"}:
    import ujson as json
else:
    import json

from aioVextractor.extractor.base_extractor import (BaseExtractor, validate, RequestRetry)


class Extractor(BaseExtractor):
    target_website = [
        "www\.bilibili\.com/video/av\d{4,9}",
    ]

    TEST_CASE = [
        "https://www.bilibili.com/video/av5546345?spm_id_from=333.334.b_62696c695f646f756761.4",
    ]

    def __init__(self, *args, **kwargs):
        BaseExtractor.__init__(self, *args, **kwargs)
        self.from_ = "bilibili"

    @validate
    @RequestRetry
    async def entrance(self, webpage_url, session):
        try:
            result = {'vid': webpage_url.split('?')[0].split('av')[-1]}
            gather_results = await asyncio.gather(*[
                self.extract_info(webpage_url=webpage_url),
                self.extract_video(result=result, session=session)
            ])
            if all(gather_results):
                return self.merge_dicts(*gather_results)
            else:
                return False
        except:
            traceback.print_exc()
            return False

    @RequestRetry
    async def extract_video(self, result, session):
        user_agent = self.random_ua()
        headers = self.general_headers(user_agent=user_agent)
        headers['Referer'] = 'https://m.bilibili.com/index.html'
        av_url = f'https://m.bilibili.com/video/av{result["vid"]}.html'
        async with session.get(av_url, headers=headers) as resp:
            html = await resp.text(encoding='utf-8', errors='ignore')
            jsonstr = re.findall("window.__INITIAL_STATE__=(.*?)};", html)  # 提取json数据 为保证容错 用 }; 来标识
            if jsonstr:
                jsonstr = jsonstr[0] + '}'
            else:
                raise ValueError
            try:
                jsondata = json.loads(jsonstr)
                if user_agent in android:
                    play_addr = jmespath.search('reduxAsyncConnect.videoInfo.initUrl', jsondata)
                    result['play_addr'] = os.path.join('http://', play_addr[2:]) \
                        if play_addr.startswith('//') \
                        else play_addr
                    result['dislike_count'] = jmespath.search('reduxAsyncConnect.videoInfo.stat.dislike', jsondata)
                    result['collect_count'] = jmespath.search('reduxAsyncConnect.videoInfo.stat.like', jsondata)
                    result['like_count'] = jmespath.search('reduxAsyncConnect.videoInfo.stat.like', jsondata)
                    result['share_count'] = jmespath.search('reduxAsyncConnect.videoInfo.stat.share', jsondata)
                    result['view_count'] = jmespath.search('reduxAsyncConnect.videoInfo.stat.view', jsondata)
                    result['category'] = jmespath.search('reduxAsyncConnect.videoInfo.toptype', jsondata)
                elif user_agent in user_agent:
                    result['comment_count'] = jmespath.search('comment.count', jsondata)
                    result['tag'] = jmespath.search('tags[].tag_name', jsondata)
                    result['author_avatar'] = jmespath.search('upData.face', jsondata)
                    result['author_description'] = jmespath.search('upData.description', jsondata)
                    result['author_birthday'] = jmespath.search('upData.birthday', jsondata)
                    result['author_attention'] = jmespath.search('upData.attention', jsondata)
                    result['author_follwer_count'] = jmespath.search('upData.fans', jsondata)
                    result['author_follwing_count'] = jmespath.search('upData.friend', jsondata)
                    result['author_id'] = jmespath.search('upData.mid', jsondata)
                    result['author'] = jmespath.search('upData.name', jsondata)
                    result['gender'] = jmespath.search('upData.sex', jsondata)
                    result['author_sign'] = jmespath.search('upData.sign', jsondata)
                    result['upload_ts'] = jmespath.search('videoData.ctime', jsondata)
                    result['description'] = jmespath.search('videoData.desc', jsondata)
                    result['duration'] = jmespath.search('videoData.duration', jsondata)
                    result['title'] = jmespath.search('videoData.title', jsondata)
                result['from'] = "bilibili"
                return result
            except:
                traceback.print_exc()
                return False


if __name__ == '__main__':
    from pprint import pprint

    with Extractor() as extractor:
        res = extractor.sync_entrance(webpage_url="https://creative.adquan.com/show/286808")
        pprint(res)

    # import aiohttp
    # from pprint import pprint
    #
    #
    # #
    # # def test():
    # #     return entrance(
    # #         webpage_url="https://www.youtube.com/watch?v=tofSaLB9kwE")
    # #
    # #
    # # pprint(test())
    # #
    #
    # async def test():
    #     async with aiohttp.ClientSession() as session_:
    #         return await entrance(
    #             webpage_url="https://www.bilibili.com/video/av5546345?spm_id_from=333.334.b_62696c695f646f756761.4",
    #             session=session_)
    #
    #
    # loop = asyncio.get_event_loop()
    # pprint(loop.run_until_complete(test()))
