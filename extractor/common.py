#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 2019/7/1
# IDE: PyCharm

import youtube_dl
import jmespath
import traceback
import time
from urllib.parse import (parse_qs, urlparse)


async def extract_info(webpage_url):
    args = {"nocheckcertificate": True,
            "ignoreerrors": True,
            "quiet": True,
            "nopart": True,
            # "download_archive": "record.txt",
            "no_warnings": True,
            "youtube_include_dash_manifest": False,
            'simulate': True
            }
    try:
        with youtube_dl.YoutubeDL(args) as ydl:
            try:
                VideoJson = ydl.extract_info(webpage_url)
                # pprint(VideoJson)
            except:
                traceback.print_exc()
                return False
            else:
                if VideoJson:
                    result = dict()
                    result['webpage_url'] = webpage_url
                    result['author'] = jmespath.search('uploader', VideoJson)
                    result['cover'] = check_cover(jmespath.search('thumbnail', VideoJson))
                    create_time = jmespath.search('upload_date', VideoJson)
                    upload_ts = int(time.mktime(time.strptime(create_time, '%Y%m%d'))) if create_time else create_time
                    result['upload_ts'] = upload_ts
                    result['description'] = jmespath.search('description', VideoJson)
                    duration = jmespath.search('duration', VideoJson)
                    result['duration'] = int(duration) if duration else duration
                    result['rating'] = jmespath.search('average_rating', VideoJson)
                    result['height'] = jmespath.search('height', VideoJson)
                    result['like_count'] = jmespath.search('like_count', VideoJson)
                    result['view_count'] = jmespath.search('view_count', VideoJson)
                    result['dislike_count'] = jmespath.search('dislike_count', VideoJson)
                    result['width'] = jmespath.search('width', VideoJson)
                    result['vid'] = jmespath.search('id', VideoJson)
                    cate = jmespath.search('categories', VideoJson)
                    result['category'] = ','.join(list(map(lambda x: x.replace(' & ', ','), cate))) if cate else cate
                    formats = extract_play_addr(VideoJson)
                    # play_addr_list = dict()
                    # for u, p, h in jmespath.search('formats[].[url, protocol, height]', VideoJson):
                    #     if ('m3u8' not in u) and ('/../' not in u):
                    #         play_addr_list[h] = u
                    # if len(play_addr_list) == 1:
                    #     result['play_addr'] = play_addr_list[max(play_addr_list)]
                    # else:
                    #     if None in play_addr_list:
                    #         del play_addr_list[None]
                    result['play_addr'] = formats['url']
                    result['title'] = jmespath.search('title', VideoJson)
                    video_tags = jmespath.search('tags', VideoJson)
                    result['tag'] = video_tags
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
