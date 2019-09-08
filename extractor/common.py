#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 2019/7/1
# IDE: PyCharm

import youtube_dl
import jmespath
import traceback
import time
from urllib.parse import (parse_qs, urlparse)
from aioVextractor.utils.user_agent import UserAgent
from random import choice


async def extract_info(webpage_url, collaborate=True):
    args = {"nocheckcertificate": True,
            "ignoreerrors": True,
            "quiet": True,
            "nopart": True,
            # "download_archive": "record.txt",
            "no_warnings": True,
            "youtube_include_dash_manifest": False,
            'simulate': True,
            'user-agent': choice(UserAgent),
            }
    try:
        with youtube_dl.YoutubeDL(args) as ydl:
            try:
                VideoJson = ydl.extract_info(webpage_url)
            except:
                traceback.print_exc()
                return False
            else:
                if VideoJson:
                    if collaborate:
                        result = extract_single(VideoJson=VideoJson, webpage_url=webpage_url)
                        return result
                    else:  ## webpage extracting using only youtube-dl
                        if 'entries' in VideoJson:
                            result = []
                            for entry in jmespath.search('entries[]', VideoJson):
                                element = extract_single(VideoJson=entry, webpage_url=webpage_url)
                                result.append(element)
                            return result
                        else:
                            result = extract_single(VideoJson=VideoJson, webpage_url=webpage_url)
                            return result
                else:
                    return False
    except:
        traceback.print_exc()
        return False


def check_cover(cover):
    """
    Some of the vimeo cover urls contain play_icon
    This method try to extract the url that not
    :param cover:
    :return:
    """
    if urlparse(cover).path == '/filter/overlay':
        try:
            cover_ = parse_qs(urlparse(cover).query).get('src0')[0]
        except IndexError:
            return cover
        if 'play_icon' in cover_:
            return cover
        elif cover_ is None:
            return cover
        else:
            return cover_
    else:
        return cover


def extract_play_addr(VideoJson):
    video_list = jmespath.search('formats[]', VideoJson)
    try:
        try:
            # return sorted(filter(lambda x:x.get('protocol', '')  in {'https', 'http'}, video_list), key=lambda x:x['filesize'])[-1]
            return sorted(filter(
                lambda x: (x.get('protocol', '') in {'https', 'http'}) and x.get('acodec') != 'none' and x.get(
                    'vcodec') != 'none', video_list), key=lambda x: x['filesize'])[-1]
        except KeyError:
            return sorted(filter(
                lambda x: x.get('protocol', '') in {'https', 'http'} and x.get('acodec') != 'none' and x.get(
                    'vcodec') != 'none', video_list), key=lambda x: x['height'])[-1]
        except IndexError:
            return jmespath.search('formats[-1]', VideoJson)
    except:
        # traceback.print_exc()
        return jmespath.search('formats[-1]', VideoJson)


def extract_single(VideoJson, webpage_url):
    result = dict()
    result['downloader'] = 'ytd'
    result['webpage_url'] = webpage_url
    result['author'] = jmespath.search('uploader', VideoJson)
    result['cover'] = check_cover(jmespath.search('thumbnail', VideoJson))
    create_time = jmespath.search('upload_date', VideoJson)
    upload_ts = int(time.mktime(time.strptime(create_time, '%Y%m%d'))) if create_time else create_time
    result['upload_ts'] = upload_ts
    result['description'] = jmespath.search('description', VideoJson)
    duration = jmespath.search('duration', VideoJson)
    result['duration'] = int(duration) if duration else 0
    result['rating'] = jmespath.search('average_rating', VideoJson)
    result['height'] = jmespath.search('height', VideoJson)
    result['like_count'] = jmespath.search('like_count', VideoJson)
    result['view_count'] = jmespath.search('view_count', VideoJson)
    result['dislike_count'] = jmespath.search('dislike_count', VideoJson)
    result['width'] = jmespath.search('width', VideoJson)
    result['vid'] = jmespath.search('id', VideoJson)
    cate = jmespath.search('categories', VideoJson)
    result['category'] = ','.join(list(map(lambda x: x.replace(' & ', ','), cate))) if cate else cate
    # formats = extract_play_addr(VideoJson)
    # result['play_addr'] = formats['url']
    result['from'] = VideoJson.get('extractor', None).lower() if VideoJson.get('extractor', None) else urlparse(
        webpage_url).netloc
    result['title'] = jmespath.search('title', VideoJson)
    video_tags = jmespath.search('tags', VideoJson)
    result['tag'] = video_tags
    return result


TEST_CASE = [
    "https://www.bilibili.com/video/av5546345?spm_id_from=333.334.b_62696c695f646f756761.4",
]
if __name__ == '__main__':
    import asyncio
    from pprint import pprint


    async def test():
        return await extract_info(
            webpage_url="https://www.bilibili.com/video/av5546345?spm_id_from=333.334.b_62696c695f646f756761.4")


    loop = asyncio.get_event_loop()
    pprint(loop.run_until_complete(test()))
