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
import os
import asyncio
from utils.user_agent import (UserAgent, android)
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
        # result['upload_ts'] = strptime(
        #     selector.css('head meta[itemprop*="datePublished"]::attr(content)').extract_first())
        # result['comment_count'] = selector.css('head meta[itemprop*="commentCount"]::attr(content)').extract_first()
        try:
            playinfo = json.loads(selector.css("head script").re_first("window.__playinfo__=(\{[\s|\S]*?\})</script>"))
        except:
            traceback.print_exc()
            return False
        else:
            pprint(playinfo)
        #     result['duration'] = jmespath.search('data.dash.duration', playinfo)
        #     # return result
        #     try:
        #         video = sorted(filter(lambda x: 'avc' in x['codecs'],
        #                               jmespath.search('data.dash.video[]', playinfo)),
        #                        key=lambda x: x['width'])[-1]
        #     except:
        #         video =
        #     result['height'] = video['height']
        #     result['width'] = video['width']
        #     result['play_addr'] = video['base_url']
        #     result['audio'] = jmespath.search('max_by(data.dash.audio, &bandwidth).base_url', playinfo)

        gather_results =  await asyncio.gather(*[
            extract_video(result=result, user_agent=choice(UserAgent), session=session),
            extract_video(result=result, user_agent=choice(android), session=session)
        ])
        result = {**result, **{**gather_results[0], **gather_results[1]}}

        try:
            base = 'https://'
            result['author_url'] = os.path.join(base,
                                                selector.css('#v_upinfo .u-face a::attr(href)').extract_first()[2:])
        except:
            traceback.print_exc()
            result['author_url'] = None
        else:
            pass

    return result


async def extract_video(result, user_agent, session, chance_left=config.RETRY):
    try:
        headers = {'Connection': 'keep-alive',
                   'Pragma': 'no-cache',
                   'Cache-Control': 'no-cache',
                   'Upgrade-Insecure-Requests': '1',
                   'User-Agent': user_agent,
                   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,'
                             'image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
                   'Referer': 'https://m.bilibili.com/index.html',
                   'Accept-Encoding': 'gzip, deflate, br',
                   'Accept-Language': 'zh-CN,zh;q=0.9',
                   }
        av_url = f'https://m.bilibili.com/video/av{result["vid"]}.html'
        async with session.get(av_url, headers=headers) as resp:
            html = await resp.text(encoding='utf-8', errors='ignore')
    except (ServerDisconnectedError, ServerConnectionError, asyncio.TimeoutError,
            ClientConnectorError, ClientPayloadError, ServerTimeoutError,
            ContentTypeError, ClientConnectorCertificateError, ClientOSError):
        if chance_left != 1:
            return await extract_video(result=result, session=session, chance_left=chance_left - 1)
        else:
            return False
    except:
        traceback.print_exc()
        return False
    else:
        jsonstr = re.findall("window.__INITIAL_STATE__=(.*?)};", html)  # 提取json数据 为保证容错 用 }; 来标识
        if jsonstr:
            jsonstr = jsonstr[0] + '}'
        else:
            if chance_left != 1:
                return await extract_video(result=result, session=session, chance_left=chance_left - 1)
            else:
                return False
        try:
            jsondata = json.loads(jsonstr)
            pprint(jsondata)
            if user_agent in android:
                play_addr = jmespath.search('reduxAsyncConnect.videoInfo.initUrl', jsondata)
                result['play_addr'] =  os.path.join('http://', play_addr[2:]) if play_addr.startswith('//') else play_addr
                result['dislike_count'] =  jmespath.search('reduxAsyncConnect.videoInfo.stat.dislike', jsondata)
                result['collect_count'] =  jmespath.search('reduxAsyncConnect.videoInfo.stat.like', jsondata)
                result['like_count'] =  jmespath.search('reduxAsyncConnect.videoInfo.stat.like', jsondata)
                result['share_count'] =  jmespath.search('reduxAsyncConnect.videoInfo.stat.share', jsondata)
                result['view_count'] =  jmespath.search('reduxAsyncConnect.videoInfo.stat.view', jsondata)
                result['category'] =  jmespath.search('reduxAsyncConnect.videoInfo.toptype', jsondata)
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
            return result
        except Exception as e:
            print(e)
            return None


async def extract_user(author_id, session, chance_left=config.RETRY):
    """
    :return:返回这个用户最新更新的视频
    """
    # headers = {'Connection': 'keep-alive',
    #            'Cache-Control': 'max-age=0',
    #            'Upgrade-Insecure-Requests': '1',
    #            'User-Agent': choice(UserAgent),
    #            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
    #            'Accept-Encoding': 'gzip, deflate, br',
    #            'Accept-Language': 'zh-CN,zh;q=0.9',
    #            }
    #
    # response = requests.get('https://m.bilibili.com/space/177361244', headers=headers, cookies=cookies)

    try:
        headers = {'Connection': 'keep-alive',
                   'Cache-Control': 'max-age=0',
                   'Upgrade-Insecure-Requests': '1',
                   'User-Agent': choice(UserAgent),
                   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
                   'Referer': 'https://www.bilibili.com/',
                   'Accept-Encoding': 'gzip, deflate, br',
                   'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8'}
        user_space_api = f'https://space.bilibili.com/ajax/member/getSubmitVideos?mid={author_id}&pagesize=100&tid=0&page=1&keyword=&order=pubdate'
        async with session.get(user_space_api, headers=headers, verify_ssl=False) as resp:
            html = await resp.text(encoding='utf-8', errors='ignore')
    except (ServerDisconnectedError, ServerConnectionError, asyncio.TimeoutError,
            ClientConnectorError, ClientPayloadError, ServerTimeoutError,
            ContentTypeError, ClientConnectorCertificateError, ClientOSError):
        if chance_left != 1:
            return await extract_user(author_id=author_id, session=session, chance_left=chance_left - 1)
        else:
            return False
    except:
        traceback.print_exc()
        return False
    else:
        respdata = json.loads(html)
        from pprint import pprint
        pprint(respdata)
        # video_list = respdata.get('data', {}).get('vlist', [])
        # for video in video_list:
        #     videoitem = dict()
        #     videoitem['description'] = video.get('description', '')
        #     videoitem['comment_count'] = video.get('comment', None)
        #     length = video.get('length', None)
        #     if length:
        #         videoitem['duration'] = get_duration(length)
        #     videoitem['comment_count'] = video.get('comment', None)
        #     videoitem['id'] = video.get('aid', None)
        #     videoitem['upload_ts'] = video.get('created', None)
        #     videoitem['view_count'] = video.get('play', None)
        #     videoitem['cover'] = video.get('pic', None)
        #     videoitem['title'] = video.get('title', None)
        #     videoitem['from'] = config.agg_target_v2['bilibili']
        #     videoitem['player'] = config.agg_target_v2['bilibili']
        #     videoitem['player_id'] = videoitem['id']
        #     videoitem['webpage_url'] = 'https://www.bilibili.com/video/av' + str(videoitem.get('id', ''))
        #     if videoitem['cover']:
        #         videoitem['cover'] = 'http' + videoitem['cover']
        #     if videoitem['id']:
        #         if videoitem['id'] in haved:  # 去重
        #             return this_user_items
        #         videoitem = await get_play_addr(videoitem, session)  #
        #         if videoitem and check_item(videoitem):
        #             this_user_items.append(videoitem.update(item) or videoitem)
        # return this_user_items


def get_duration(strl):
    """

    :param strl: 传入时间 如 "02：02"
    :return: 返回秒
    """
    if ':' not in strl:
        return None
    else:
        try:
            return int(strl.split(':')[0]) * 60 + int(strl.split(':')[1])
        except:
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
