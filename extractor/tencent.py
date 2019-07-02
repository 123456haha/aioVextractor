#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 2019/6/20
# IDE: PyCharm


from ..utils.exception import exception
from ..utils.user_agent import UserAgent
from random import choice
from .. import config
import traceback
import ujson as json
import jmespath
import math
import random
import re
import os
from scrapy.selector import Selector
import time
import asyncio


# import uvloop
# uvloop.install()


async def entrance(webpage_url, session, chance_left=config.RETRY):
    result = dict()
    try:
        headers = {'authority': 'v.qq.com',
                   'upgrade-insecure-requests': '1',
                   'user-agent': choice(UserAgent),
                   'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                   'accept-encoding': 'gzip, deflate, br',
                   'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,ko;q=0.7'}
        async with session.get(webpage_url, headers=headers) as response:
            text = await response.text(encoding='utf8', errors='ignore')
    except exception:
        if chance_left != 1:
            return await entrance(webpage_url=webpage_url, session=session, chance_left=chance_left - 1)
        else:
            return False
    except:
        traceback.print_exc()
        return False
    else:
        try:
            selector = Selector(text=text)
        except:
            traceback.print_exc()
            return False
        result['webpage_url'] = webpage_url
        try:
            vid = re.compile('&vid=(.*?)&').findall(text)[0]
        except (TypeError, IndexError):
            return False
        else:
            result['vid'] = vid
            try:
                title = selector.css('meta[name*=title]::attr(content)').extract_first()
                result['title'] = title.replace('_1080P在线观看平台_腾讯视频', ''). \
                    replace('高清1080P在线观看平台', ''). \
                    replace('_腾讯视频', ''). \
                    replace('_', ' ')
            except AttributeError:
                result['title'] = selector.css('.player_title a::text').extract_first()
            tags = selector.css("head meta[name*='keywords']::attr(content)").extract_first()
            result['description'] = selector.css("._video_summary::text").extract_first()
            result['tags'] = tags.split(',') if tags else None
            category = selector.css('.site_channel .channel_nav[class~="current"]::text').extract()
            result['category'] = ','.join(category) if category else None
            result['cover'] = 'http://vpic.video.qq.com/0/{vid}.png'.format(vid=vid)
            video_create_time = selector.css('head meta[itemprop="datePublished"]::attr(content)').extract_first()
            upload_ts, upload_date = strptime(video_create_time)
            result['upload_ts'] = upload_ts
            video_duration = selector.css('head meta[itemprop="duration"]::attr(content)').extract_first()
            video_duration = cal_duration(video_duration)
            if video_duration is None:
                VIDEO_INFO = selector.css('script[r-notemplate]').re_first('var VIDEO_INFO = ([\s|\S]*)\s</script>')
                try:
                    VIDEO_INFO = json.loads(VIDEO_INFO)  ## having tag inside
                except ValueError:
                    video_duration = None
                else:
                    video_duration = jmespath.search("duration", VIDEO_INFO)
            result['duration'] = video_duration
            view_count_type = selector.css('.action_count .icon_text::text').extract_first()
            if '专辑' in view_count_type:
                COVER_INFO = selector.css('script[r-notemplate]').re_first('var COVER_INFO = ([\s|\S]*?)\svar')
                try:
                    COVER_INFO = json.loads(COVER_INFO)  ## having category_map inside
                except ValueError:
                    pass
                else:
                    result['category'] = result['category'] if result['category'] \
                        else extract_category_from_COVER_INFO(COVER_INFO=COVER_INFO)
                    player_view_count = jmespath.search('positive_view_today_count', COVER_INFO)
                    if not player_view_count or player_view_count == 'undefined':
                        player_view_count = jmespath.search('view_today_count', COVER_INFO)
                    if not player_view_count or player_view_count == 'undefined':
                        player_view_count = None
                    result['view_count'] = player_view_count
            else:
                result['view_count'] = selector.css('head meta[itemprop*=interactionCount]::attr(content)').extract_first()
            if result['view_count'] == 'undefined':
                result['view_count'] = None
            gather_results = await asyncio.gather(*[extract_comment_count(selector=selector, session=session),
                                                    extract_author_info(selector=selector, session=session),
                                                    extract_by_vkey(vid=vid, url=webpage_url, session=session)])
            result = {**result, **{'comment_count': gather_results[0]}}
            result = {**result, **gather_results[1]}
            result = {**result, **gather_results[2]}
            return result


def extract_category_from_COVER_INFO(COVER_INFO):
    category_map = jmespath.search('category_map', COVER_INFO)
    category = list({ele if isinstance(ele, str) else None for ele in category_map})
    if category:
        if None in category:
            category.remove(None)
        category = ','.join(category)
        return category
    else:
        return None


async def extract_comment_count(selector, session, chance_left=config.RETRY):
    try:
        COVER_INFO = json.loads(selector.css('script').re_first('var COVER_INFO = (.*?)\svar COLUMN_INFO ='))
        commentId = jmespath.search('commentId.comment_id', COVER_INFO)
    except (TypeError, IndexError):
        return None
    else:
        headers = {
            'authority': 'video.coral.qq.com',
            'cache-control': 'max-age=0',
            'upgrade-insecure-requests': '1',
            'user-agent': choice(UserAgent),
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8'}
        params = {'source': '0',
                  'targetids': commentId}
        api = 'https://video.coral.qq.com/article/batchcommentnumv2'
        try:
            async with session.get(api, headers=headers, params=params) as response:
                response_json = await response.json()
        except exception:
            if chance_left != 1:
                return await extract_comment_count(selector=selector, session=session, chance_left=chance_left - 1)
            else:
                return False
        except:
            traceback.print_exc()
            if chance_left != 1:
                return await extract_comment_count(selector=selector, session=session, chance_left=chance_left - 1)
            else:
                return False
        else:
            return jmespath.search('data[0].commentnum', response_json)


async def extract_author_info(selector, session, chance_left=config.RETRY):
    user_page_url = selector.css('.video_user a::attr(href)').extract_first()
    if not user_page_url or user_page_url == 'javascript:':
        return {}
    headers = {'Connection': 'keep-alive',
               'Cache-Control': 'max-age=0',
               'Upgrade-Insecure-Requests': '1',
               'User-Agent': choice(UserAgent),
               'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
               'Accept-Encoding': 'gzip, deflate',
               'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,ko;q=0.7'}
    try:
        async with session.get(user_page_url, headers=headers) as response:
            text = await response.text(encoding='utf8', errors='ignore')
            selector = Selector(text=text)
    except exception:
        if chance_left != 1:
            return await extract_author_info(selector=selector, session=session, chance_left=chance_left - 1)
        else:
            return {}  ## return empty dict if the page cannot be requested right now
    else:
        result = dict()
        result['author'] = extract_author_name(selector=selector)
        result['author_url'] = user_page_url
        return result


def extract_author_name(selector):
    author = selector.css('.user_info_name::text').extract_first()
    if author is None:
        author = selector.css('head title::text').extract_first()
        if author:
            return author.replace('的个人频道', '')
    else:
        return author


def strptime(string):
    if string not in {'null', 'undefined'} and string:
        try:
            struct_time = time.strptime(string[:10], '%Y-%m-%d')
        except ValueError:
            return None, None
        else:
            ts = int(time.mktime(struct_time)) if string else None
            upload_date = time.strftime("%Y%m%d", struct_time) if string else None
            return ts, upload_date
    else:
        return None, None


def cal_duration(raw_duration_string):
    regex = re.compile("(\d{1,3})([HMS]?)")
    try:
        _duration = regex.findall(raw_duration_string)
    except TypeError:
        print(f"raw_duration_string: {raw_duration_string}")
        traceback.print_exc()
        return None
    duration = 0
    for value, pointer in _duration:
        if pointer == 'H':
            duration += int(value) * 60 * 60
        elif pointer == 'M':
            duration += int(value) * 60
        elif pointer == 'S':
            duration += int(value)

    return duration if duration else None


async def extract_by_vkey(vid, url, session, chance_left=config.RETRY):
    Host = choice(['vv.video.qq.com', 'tt.video.qq.com', 'flvs.video.qq.com',
                   'tjsa.video.qq.com', 'a10.video.qq.com', 'xyy.video.qq.com', 'vsh.video.qq.com',
                   'vbj.video.qq.com', 'bobo.video.qq.com', 'h5vv.video.qq.com'])
    extract_by_vkey_headers = {'Accept-Encoding': 'gzip, deflate',
                               'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                               'User-Agent': choice(UserAgent),
                               'Host': Host,
                               'Accept': '*/*',
                               'Cache-Control': 'max-age=0',
                               'Upgrade-Insecure-Request': '1'}
    guid = createGUID()
    extract_by_vkey_params = {'vid': vid,
                              'platform': 101001,
                              'otype': 'json',
                              'guid': guid,
                              'defaultfmt': 'shd',
                              'defnpayver': 1,
                              'appVer': '3.0.83',
                              'host': 'v.qq.com',
                              'ehost': url,
                              'defn': 'mp4',
                              'fhdswitch': 0,
                              'show1080p': 1,
                              'isHLS': 0,
                              'newplatform': 'v1010',
                              'defsrc': 1,
                              'sdtfrom': 'v1010',
                              '_0': 'undefined',
                              '_1': 'undefined',
                              '_2': 'undefined',
                              '_': int(round(time.time() * 1000)),
                              'callback': 'QZOutputJson=',
                              'charge': 0}

    api_get_info = os.path.join('http://', Host, 'getinfo')
    try:
        async with session.get(api_get_info, headers=extract_by_vkey_headers, params=extract_by_vkey_params) as response_getinfo:
            response_getinfo_text = await response_getinfo.text(encoding='utf8', errors='ignore')
    except exception:
        if chance_left != 1:
            return await extract_by_vkey(vid=vid, url=url, session=session, chance_left=chance_left - 1)
        else:
            return await extract_by_api(url=url, session=session)
    else:
        try:
            ResJson = json.loads(response_getinfo_text[len('QZOutputJson='):-1])
        except ValueError:
            traceback.print_exc()
            print(f"response_getinfo_text: {response_getinfo_text[:50]}")
            if chance_left != 1:
                return await extract_by_vkey(vid=vid, url=url, session=session, chance_left=chance_left - 1)
            else:
                return await extract_by_api(url=url, session=session)
        filename = jmespath.search('vl.vi[0].fn', ResJson)
        if not filename:
            return await extract_by_api(url=url, session=session)
        else:
            vkey = jmespath.search('vl.vi[0].fvkey', ResJson)
            url_prefix = jmespath.search('vl.vi[0].ul.ui[-1].url', ResJson)
            result = {'play_addr': os.path.join(url_prefix, filename) + '?vkey=' + vkey, 'vid': vid}
            return result


def createGUID():
    length = 32
    guid, position = '', 1
    while length >= position:
        digit = format(math.floor(16 * random.uniform(0, 1)), 'x')
        guid += digit
        position += 1
    return guid

async def extract_by_api(url, session, chance_left=config.RETRY):

    extract_by_api_headers = {'Accept-Encoding': 'gzip, deflate',
                                         'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                                         'User-Agent': choice(UserAgent),
                                         'Accept': '*/*',
                                         'Referer': 'http://v.ranks.xin/',
                                         'X-Requested-With': 'XMLHttpRequest'}
    params = {'url': url}
    try:
        api = 'http://v.ranks.xin/video-parse.php'
        async with session.get(api, headers=extract_by_api_headers, params=params) as response:
            response_json = await response.json()
            play_addr = jmespath.search('data[0].url', response_json)
            if not play_addr:
                return False
            result = {'play_addr': play_addr}
    except exception:
        if chance_left != 1:
            return await extract_by_api(url=url, session=session, chance_left=chance_left - 1)
        else:
            return False
    except:
        traceback.print_exc()
        return False
    else:
        return result


if __name__ == '__main__':
    import asyncio
    import aiohttp
    from pprint import pprint
    "https://v.qq.com/x/page/s0886ag14xn.html"
    "https://v.qq.com/x/page/n0864edqzkl.html"
    "https://v.qq.com/x/page/s08899ss07p.html"
    "https://v.qq.com/x/cover/bzfkv5se8qaqel2.html"
    async def test():
        async with aiohttp.ClientSession() as session_:
            return await entrance(webpage_url="https://v.qq.com/x/cover/bzfkv5se8qaqel2.html",
                                  session=session_)
    pprint(asyncio.run(test()))
