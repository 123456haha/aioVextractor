#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 2019/7/1
# IDE: PyCharm

import youtube_dl
import jmespath
import traceback
import time

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
                result = dict()
                result['webpage_url'] = webpage_url
                result['author'] = jmespath.search('uploader', VideoJson)
                result['cover'] = jmespath.search('thumbnail', VideoJson)
                create_time = jmespath.search('upload_date', VideoJson)
                result['upload_ts'] = int(
                    time.mktime(time.strptime(create_time, '%Y%m%d'))) if create_time else create_time
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
                play_addr_list = dict()
                for u, p, h in jmespath.search('formats[].[url, protocol, height]', VideoJson):
                    if ('m3u8' not in u) and ('/../' not in u):
                        play_addr_list[h] = u
                if len(play_addr_list) == 1:
                    result['play_addr'] = play_addr_list[max(play_addr_list)]
                else:
                    if None in play_addr_list:
                        del play_addr_list[None]
                    result['play_addr'] = play_addr_list[max(play_addr_list)]
                result['title'] = jmespath.search('title', VideoJson)
                video_tags = jmespath.search('tags', VideoJson)
                result['tag'] = video_tags
                return result
    except:
        traceback.print_exc()
        return False
