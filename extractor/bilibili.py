#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 2019/6/20
# IDE: PyCharm

import traceback
import re
import time
import ujson as json
import config
import jmespath
from scrapy import Selector
import asyncio
from utils.user_agent import UserAgent
from random import choice
from aiohttp.client_exceptions import (ServerDisconnectedError, ServerConnectionError, ClientOSError,
                                       ClientConnectorCertificateError, ServerTimeoutError, ContentTypeError,
                                       ClientConnectorError, ClientPayloadError)


async def entrance(webpage_url, session, chance_left=config.RETRY):
    result = dict()
    try:
        headers = {'Connection': 'keep-alive',
                   'Cache-Control': 'max-age=0',
                   'Upgrade-Insecure-Requests': '1',
                   'User-Agent': choice(UserAgent),
                   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
                   'Referer': 'https://www.bilibili.com/',
                   'Accept-Encoding': 'gzip, deflate, br',
                   'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8'}
        async with session.get(webpage_url, headers=headers) as response:
            text = await response.text(encoding='utf8', errors='ignore')
    except (ServerDisconnectedError, ServerConnectionError, asyncio.TimeoutError,
            ClientConnectorError, ClientPayloadError, ServerTimeoutError,
            ContentTypeError, ClientConnectorCertificateError, ClientOSError):
        if chance_left != 1:
            return await entrance(webpage_url=webpage_url, session=session, chance_left=chance_left - 1)
        else:
            return False
    except:
        traceback.print_exc()
        return False
    else:
        selector = Selector(text=text)
        result['webpage_url'] = webpage_url
        result['vid'] = webpage_url.split('?')[0].split('av')[-1]
        # await get_play_addr(result['vid'], session=session)
        result['title'] = selector.css('head title::text').extract_first()
        result['tag'] = selector.css('head meta[itemprop*="keywords"]::attr(content)').extract_first()
        result['description'] = selector.css('head meta[itemprop*="description"]::attr(content)').extract_first()
        result['author'] = selector.css('head meta[itemprop*="author"]::attr(content)').extract_first()
        result['upload_ts'] = strptime(
            selector.css('head meta[itemprop*="datePublished"]::attr(content)').extract_first())
        result['comment_count'] = selector.css('head meta[itemprop*="commentCount"]::attr(content)').extract_first()
        try:
            playinfo = json.loads(selector.css("head script").re_first("window.__playinfo__=(\{[\s|\S]*?\})</script>"))
        except:
            traceback.print_exc()
            return False
        else:
            pprint(playinfo)
            result['duration'] = jmespath.search('data.dash.duration', playinfo)
            video = sorted(filter(lambda x: 'avc' in x['codecs'],
                                  jmespath.search('data.dash.video[]', playinfo)),
                           key=lambda x: x['width'])[-1]
            result['height'] = video['height']
            result['width'] = video['width']
            result['play_addr'] = video['base_url']
            result['audio'] = jmespath.search('max_by(data.dash.audio, &bandwidth).base_url', playinfo)
    return result


async def get_play_addr(vid, session):
    av_url = f'https://m.bilibili.com/video/av{vid}.html'
    async with session.get(av_url) as resp:
        html = await resp.text(encoding='utf-8', errors='ignore')
        print(html)
        jsonstr = re.findall("window.__INITIAL_STATE__=(.*?)};", html)  # 提取json数据 为保证容错 用 }; 来标识
        print(jsonstr)
        if jsonstr:
            jsonstr = jsonstr[0] + '}'
        try:
            jsondata = json.loads(jsonstr)
            pprint(jsondata)
            # videoTag = jsondata.get('reduxAsyncConnect', {}).get('videoTag', [])
            # category = ''
            # for Tag in videoTag:
            #     category += Tag.get('tag_name', '') + ';'
            # videoitem['category'] = category
            # videoitem['play_addr'] = jsondata.get('reduxAsyncConnect', {}).get('videoInfo', {}).get('initUrl', '')
            # if videoitem['play_addr'].startswith('//'):
            #     videoitem['play_addr'] = 'http:' + videoitem['play_addr']
            # return videoitem
        except Exception as e:
            print(e)
            return None


def strptime(string):
    if string not in {'null', 'undefined'} and string:
        try:
            struct_time = time.strptime(string, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            return None
        else:
            ts = int(time.mktime(struct_time)) if string else None
            return ts
    else:
        return None


if __name__ == '__main__':
    import asyncio
    import aiohttp
    from pprint import pprint

    "https://www.bilibili.com/video/av39303278?spm_id_from=333.334.b_62696c695f646f756761.3"
    "https://www.bilibili.com/video/av5546345?spm_id_from=333.334.b_62696c695f646f756761.4"


    async def test():
        async with aiohttp.ClientSession() as session_:
            return await entrance(
                webpage_url="https://www.bilibili.com/video/av5546345?spm_id_from=333.334.b_62696c695f646f756761.4",
                session=session_)


    pprint(asyncio.run(test()))
