#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 2019/6/20
# IDE: PyCharm

import jmespath
from aioVextractor.utils.user_agent import UserAgent
from aioVextractor.utils.requests_retry import RequestRetry
from random import choice
from os.path import splitext
from scrapy.selector import Selector
import asyncio
import html
import emoji
import dateutil.parser
import traceback
from urllib.parse import urlparse
import os


@RequestRetry
async def entrance(webpage_url, session):
    headers = {'Connection': 'keep-alive',
               'Cache-Control': 'max-age=0',
               'Upgrade-Insecure-Requests': '1',
               'User-Agent': choice(UserAgent),
               'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
               'Accept-Encoding': 'gzip, deflate',
               'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,ko;q=0.7'}
    params = {'from': 'ArticleList'}
    async with session.get(webpage_url, headers=headers, params=params) as response:
        response_text = await response.text(encoding='utf8', errors='ignore')
        webpage = await extract_publish(response=response_text)
        vid = webpage['vid']
        if not vid:
            return False
        video = await extract_video_info(referer=webpage_url, vid=vid, session=session)
        if all([webpage, video]):
            return {**webpage, **video}
        else:
            pprint([webpage, video])
            return False


async def extract_publish(response):
    result = dict()
    try:
        selector = Selector(text=response)
    except:
        traceback.print_exc()
        return False
    vid = selector.css('body script').re_first('vid: "([\s|\S]*?)",')
    result['from'] = "新片场"
    result['vid'] = vid
    try:
        result['author'] = emoji.demojize(selector.css('.creator-info .name::text').extract_first().strip())
    except AttributeError:
        result['author'] = None
    result['author_id'] = selector.css('a[data-userid]::attr(data-userid)').extract_first()
    uploader_url = selector.css('a[data-userid]::attr(href)').extract_first()
    try:
        result['author_url'] = os.path.join("https://www.xinpianchang.com", uploader_url.strip('/'))
    except AttributeError:
        result['author_url'] = None

    result['title'] = selector.css('.title-wrap .title::text').extract_first()
    result['tag'] = selector.css('.tag-wrapper a ::text').extract()  ## ['公益', '央视', '清明']
    try:
        result['category'] = list(map(lambda x: x.strip(), selector.css('.cate a::text').extract()))
    except AttributeError:
        result['category'] = None

    video_create_time = selector.css('meta[property="article:published_time"]::attr(content)').extract_first()
    result['upload_ts'] = int(dateutil.parser.parse(video_create_time).timestamp()) if video_create_time else None
    try:
        result['upload_date'] = dateutil.parser.parse(video_create_time).strftime('%Y%m%d')
    except TypeError:
        result['upload_date'] = None
    try:
        result['description'] = unescape('\n'.join(
            map(lambda x: x.strip(), selector.css('.filmplay-info-desc>p[class~="desc"]::text').extract())))
    except AttributeError:
        result['description'] = None
    try:
        result['view_count'] = int(selector.css('.play-counts::text').extract_first().replace(',', ''))
    except (ValueError, AttributeError):
        result['view_count'] = None
    try:
        result['like_count'] = int(selector.css('.like-counts::text').extract_first().replace(',', ''))
    except (ValueError, AttributeError):
        result['like_count'] = None
    result['cover'] = selector.css('script').re_first("cover: '([\s|\S]*?)',")
    return result


@RequestRetry
async def extract_video_info(referer, vid, session):
    headers = {'User-Agent': choice(UserAgent),
               'Referer': referer,
               'Origin': 'http://www.xinpianchang.com'}
    params = {'expand': 'resource,resource_origin?'}
    extract_video_info_url = f'https://openapi-vtom.vmovier.com/v3/video/{vid}'
    async with session.get(extract_video_info_url, headers=headers, params=params) as response:
        response_json = await response.json()
        result = dict()
        try:
            play_addr = jmespath.search('max_by(data.resource.progressive, &filesize).https_url', response_json)
        except:
            play_addr = jmespath.search('data.resource.progressive[-1].https_url', response_json)
        result['play_addr'] = play_addr
        video_duration = jmespath.search('data.video.duration', response_json)
        try:
            width, height = jmespath.search('data.resource.*.[width, height]', response_json)[0]
        except IndexError:
            width = height = None
        result['width'] = width
        result['height'] = height
        result['duration'] = int(int(video_duration) / 1000) if video_duration else video_duration
        result['webpage_url'] = referer
        return result


def unescape(string):
    if string:
        return html.unescape(string)
    else:
        return None


def get_ext(url_):
    """Return the filename extension from url, or ''."""
    if url_ is None:
        return False
    parsed = urlparse(url_)
    root, ext_ = splitext(parsed.path)
    ext = ext_[1:]  # or ext[1:] if you don't want the leading '.'
    ## ext = 'jpeg@80w_80h_1e_1c'
    return ext.split('@')[0]


if __name__ == '__main__':
    import aiohttp
    from pprint import pprint

    "https://www.xinpianchang.com/a10475334?from=ArticleList"
    "https://www.xinpianchang.com/u10009204?from=userList"


    async def test():
        async with aiohttp.ClientSession() as session_:
            return await entrance(
                webpage_url="https://www.xinpianchang.com/a10475334?from=ArticleList",
                session=session_)


    loop = asyncio.get_event_loop()
    pprint(loop.run_until_complete(test()))
