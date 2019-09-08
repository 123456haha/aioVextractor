#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 2019/6/20
# IDE: PyCharm

from aioVextractor.utils.requests_retry import RequestRetry
import re, json, time
import jmespath
import traceback


@RequestRetry
async def entrance(webpage_url, session):
    video = await extract_video_info(webpage_url, session=session)
    return video


async def extract_video_info(webpage_url, session):
    if "video" not in webpage_url:
        return None
    try:
        async with session.get(webpage_url) as resp:
            item = dict()
            text = await resp.text()
            jsonstr = re.findall("window.__NUXT__=(.*?);<", text)
            if jsonstr:
                try:
                    jsondata = json.loads(jsonstr[0])
                except (IndexError, TypeError):
                    traceback.print_exc()
                    return False
                video = jmespath.search("data[0].feeddata.video", jsondata)
                item['from'] = "carben"
                item['webpage_url'] = webpage_url
                item['cover'] = video.get('cover')
                item['description'] = video.get('description')
                item['tag'] = video.get('tags')
                item['title'] = video.get('title')
                item['vid'] = video.get('id')
                item['play_addr'] = jmespath.search('qualities[0].path', video)
                try:
                    item['width'], item['height'] = re.compile('_(\d{3,4})x(\d{3,4})\.').findall(item['play_addr'])[0]
                except:
                    traceback.print_exc()
                    return False
                item['duration'] = video.get('duration')
                item['collect_count'] = video.get('collectionCount')
                item['share_count'] = video.get('shareCount')
                item['recommend'] = video.get('recommend')
                item['view_count'] = video.get('playCount')
                item['like_count'] = video.get('likeCount')
                item['author'] = video.get('author').get('name')
                item['author_id'] = jmespath.search('data[0].feeddata.user.id', jsondata)
                item['author_avatar'] = video.get('author').get('icon')
                if jmespath.search('author.id', video):
                    item['author_url'] = "https://carben.me/user/" + str(item['author_id'])
                item['comment_count'] = video.get('replyCount')
                item['upload_ts'] = int(time.mktime(time.strptime(video.get("published_at"), "%Y-%m-%d %H:%M:%S")))
            return item
    except:
        traceback.print_exc()
        return None


TEST_CASE = [
    "https://carben.me/video/9049",
]

if __name__ == '__main__':
    import asyncio
    import aiohttp
    from pprint import pprint


    async def test():
        async with aiohttp.ClientSession() as session_:
            return await entrance(
                "https://carben.me/video/9049", session_)


    loop = asyncio.get_event_loop()
    res = loop.run_until_complete(test())
    pprint(res)
