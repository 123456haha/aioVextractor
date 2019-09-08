#!/usr/bin/env python
# -*- coding: utf-8 -*-
# IDE: PyCharm

import asyncio
import aiohttp, time
from aioVextractor.utils.requests_retry import *
import json, base64
import emoji
from urllib.parse import quote
import traceback


async def breakdown(webpage_url,
                    page=1,
                    params=None):
    """
    cursor is the current place of the video
    offset can only be the integer multiple of 10
    :return: list of title and cover
    """
    conn = aiohttp.TCPConnector(ssl=False)
    if "channel" in webpage_url and params == {}:
        async with aiohttp.ClientSession(connector=conn) as session:
            results = await GetExtract(webpage_url, session)
            return results
    if params is None or params == {}:
        async with aiohttp.ClientSession(connector=conn) as session:
            results = await GetFirst(webpage_url, session)
            return results
    else:
        async with aiohttp.ClientSession(connector=conn) as session:
            if params['continuation'] == 'video':
                params = params['clickTrackingParams']
                params = str(base64.b64decode(params), 'utf-8')
                params = json.loads(params)
                results = await GetOther(params, session, webpage_url)
                return results
            else:
                params = params['clickTrackingParams']
                return await GetChannelPage(params, session, webpage_url)


async def GetChannelPage(params, session, playlist_url):
    returnList = []
    hasNext = False
    returnParams = None
    ownerid = None
    tagurl = "https://www.instagram.com/graphql/query/?query_hash=bc78b344a68ed16dd5d7f264681c4c76&variables=" + str(
        quote(params))
    async with session.get(tagurl, verify_ssl=False) as resp:
        try:
            jsondata = await resp.json()
            edge_felix_video_timeline = jsondata.get("data", {}).get("user", {}).get("edge_felix_video_timeline", {})
            edges = edge_felix_video_timeline.get("edges", [])
            for edge in edges:
                edge = edge.get("node", {})
                item = dict()
                item['height'] = edge.get("dimensions", {}).get("height")
                item['width'] = edge.get("dimensions", {}).get("width")
                item['cover'] = edge.get("display_url")
                item['like_count'] = edge.get("edge_liked_by", {}).get("count", 0)
                item['comment_count'] = edge.get("edge_media_to_comment", {}).get("count", 0)
                item['vid'] = edge.get("shortcode")
                item['upload_ts'] = edge.get("taken_at_timestamp")
                item['title'] = edge.get("title")
                item['duration'] = int(edge.get("video_duration", 0))
                item['view_count'] = int(edge.get("video_view_count", 0))
                item['webpage_url'] = "https://www.instagram.com/tv/{}/".format(item['vid'])
                item['playlist_url'] = playlist_url
                if not ownerid:
                    ownerid = edge.get("owner").get("id")
                if item['vid']:
                    returnList.append(item)
            if edge_felix_video_timeline.get("page_info", {}).get("has_next_page"):
                hasNext = True
            end_cursor = edge_felix_video_timeline.get("page_info", {}).get("end_cursor")
            returnParams = {"id": ownerid, "first": 12, "after": end_cursor}
        except:
            traceback.print_exc()
    if hasNext:
        return returnList, hasNext, {"continuation": "channel", "clickTrackingParams": json.dumps(returnParams)}
    return returnList, hasNext, None


async def GetExtract(webpage_url, session):
    returnList = []
    hasNext = False
    returnParqams = None
    ownerid = None
    if webpage_url.endswith("/"):
        webpage_url = webpage_url + "?__a=1"
    else:
        webpage_url = webpage_url.split("#")[0] + "/?__a=1"
    async with session.get(webpage_url, verify_ssl=False) as resp:
        try:
            html = await resp.text(encoding='utf-8', errors="ignore")
            jsondata = json.loads(html)
            user = jsondata.get('graphql', {}).get("user")
            if not user:
                return returnList, False, None
            edge_felix_video_timeline = user.get("edge_felix_video_timeline", {})
            edges = edge_felix_video_timeline.get("edges", [])
            for edge in edges:
                edge = edge.get("node", {})
                item = dict()
                item['height'] = edge.get("dimensions", {}).get("height")
                item['width'] = edge.get("dimensions", {}).get("width")
                item['cover'] = edge.get("display_url")
                item['like_count'] = edge.get("edge_liked_by", {}).get("count", 0)
                item['comment_count'] = edge.get("edge_media_to_comment", {}).get("count", 0)
                item['vid'] = edge.get("shortcode")
                item['upload_ts'] = edge.get("taken_at_timestamp")
                item['title'] = edge.get("title")
                item['duration'] = int(edge.get("video_duration", 0))
                item['view_count'] = int(edge.get("video_view_count", 0))
                item['webpage_url'] = "https://www.instagram.com/tv/{}/".format(item['vid'])
                item['playlist_url'] = webpage_url
                if not ownerid:
                    ownerid = edge.get("owner").get("id")
                if item['vid']:
                    returnList.append(item)
            if edge_felix_video_timeline.get("page_info", {}).get("has_next_page"):
                hasNext = True
            end_cursor = edge_felix_video_timeline.get("page_info", {}).get("end_cursor")
            returnParqams = {"id": ownerid, "first": 12, "after": end_cursor}
        except:
            traceback.print_exc()
    if ownerid:
        return returnList, hasNext, {"continuation": "channel", "clickTrackingParams": json.dumps(returnParqams)}
    return returnList, hasNext, returnParqams


async def GetOther(inputparams, session, playlist_url):
    if not inputparams:
        return None
    if inputparams.get("query_hash") is None:
        return [], False, None
    tagurl = 'https://www.instagram.com/graphql/query/?query_hash=' + inputparams.get('query_hash')
    urlp = '{' + '"id":"{}","first":12,"after":"{}"'.format(inputparams.get('id'), inputparams.get('after')) + '}'
    tagurl = tagurl + "&variables=" + urlp
    this_user_items = []
    params = None
    async with session.get(tagurl, verify_ssl=False) as resp:
        html = await resp.text(encoding='utf-8', errors="ignore")
        try:
            jsondata = json.loads(html)
            data = jsondata.get('data', {})
            user = data.get('user')
            if not user:
                return [], False, None
            videolist = user.get('edge_owner_to_timeline_media', {}).get('edges', [])
            hasNext = user.get('edge_owner_to_timeline_media', {}).get("page_info", {}).get("has_next_page", False)
            # {"id": "10821827369", "first": 12,
            #  "after": "QVFCZ3lPWW14QlhIT3lFTjJnR2VYa1FNcmE2ZnM2LU1EYWN3MEVOVVpsNUlpWHk3ZS1wNkZWR0dIdWROY1pLeGE0OENNSGJKNDF5VGRrYW9QdFYteHlmTw=="}
            after = user.get('edge_owner_to_timeline_media', {}).get("page_info", {}).get("end_cursor", None)
            if after:
                params = dict()
                params['query_hash'] = "f2405b236d85e8296cf30347c9f08c2a"
                params['id'] = inputparams.get('id')
                params['first'] = 12
                params['after'] = after
            for video in videolist:
                item = {}
                node = video.get('node', {})
                if not node.get("is_video"):
                    continue
                item['duration'] = node.get('video_duration', '')
                item['like_count'] = node.get('edge_liked_by', {}).get('count', None)
                item['comment_count'] = node.get('edge_media_to_comment', {}).get('count', None)
                item['from'] = 'instagram'
                item['player_id'] = node.get('id')
                item['cover'] = node.get('display_url', '')
                item['author_id'] = node.get('owner', {}).get('id', None)
                item['title'] = node.get('title')
                item['view_count'] = node.get('video_view_count', '')
                item['playlist_url'] = playlist_url
                shortcode = node.get('shortcode', None)
                if shortcode:
                    item['webpage_url'] = 'https://www.instagram.com/p/{}/'.format(shortcode)
                    await get_content_items(item['webpage_url'], item, session)
                    if item['duration'] is None:
                        continue
                    this_user_items.append(item)
        except:
            traceback.print_exc()
            return this_user_items, None, False
    returnparams = json.dumps(params)
    returnparams = base64.b64encode(returnparams.encode('utf-8'))
    return this_user_items, hasNext, {"continuation": "video", "clickTrackingParams": returnparams}


@RequestRetry
async def get_content_items(webpage_url, item, session):
    """
    :param webpage_url: 详情页
    :param item:
    :param session:回话
    :return:没有返回
    从详情页api
    对item进行添加数据
    """
    tagurl = webpage_url + '?__a=1'
    async with session.get(tagurl, verify_ssl=False) as resp:
        try:
            html = await resp.text(encoding='utf-8', errors='ignore')
            jsondata = json.loads(html)
            shortcode_media = jsondata.get('graphql', {}).get('shortcode_media', None)
            if not shortcode_media:
                return
            item['play_addr'] = shortcode_media.get('video_url', None)
            try:
                item['description'] = emoji.demojize(
                    shortcode_media.get('edge_media_to_caption', {}).get('edges', [{}])[0].get('node',
                                                                                               {}).get(
                        'text', ''))
            except:
                pass
            item['view_count'] = shortcode_media.get("video_view_count")
            if not item.get('duration'):
                item['duration'] = int(shortcode_media.get("video_duration"))
            item['upload_ts'] = shortcode_media.get('taken_at_timestamp', None)
            item['created_at'] = int(time.time())
            item['title'] = item.get('title')
            item['vid'] = shortcode_media.get("shortcode")
            item['from'] = 'instagram'
            item['like_count'] = shortcode_media.get('edge_media_preview_like', {}).get('count', None)
            item['comment_count'] = shortcode_media.get('edge_media_to_parent_comment', {}).get('count', None)
            item['webpage_url'] = webpage_url
            item['cover'] = shortcode_media.get("display_url")
            item['width'] = shortcode_media.get("dimensions", {}).get("width")
            item['height'] = shortcode_media.get("dimensions", {}).get("height")
            item['author'] = shortcode_media.get("owner", {}).get("username")
        except:
            traceback.print_exc()


@RequestRetry
async def GetFirst(tagurl, session):
    this_user_items = []
    params = None
    if not tagurl:
        return this_user_items
    if tagurl[-1] != '/':
        tagurl = tagurl + '/?__a=1'
    else:
        tagurl = tagurl.split("?")[0] + '?__a=1'
    async with session.get(tagurl, verify_ssl=False) as resp:
        html = await resp.text(encoding='utf-8', errors="ignore")
        try:
            jsondata = json.loads(html)
            user = jsondata.get('graphql', {}).get('user', None)
            if not user:
                return this_user_items, False, None
            videolist = user.get('edge_owner_to_timeline_media', {}).get('edges', [])
            hasNext = user.get('edge_owner_to_timeline_media', {}).get("page_info", {}).get("has_next_page", False)
            after = user.get('edge_owner_to_timeline_media', {}).get("page_info", {}).get("end_cursor", None)
            if after:
                params = dict()
                params['query_hash'] = "f2405b236d85e8296cf30347c9f08c2a"
                params['id'] = user.get('id')
                params['first'] = 12
                params['after'] = after
            for video in videolist:
                item = {}
                node = video.get('node', {})
                if not node.get("is_video"):
                    continue
                item['duration'] = node.get('video_duration', '')
                item['like_count'] = node.get('edge_liked_by', {}).get('count', None)
                item['comment_count'] = node.get('edge_media_to_comment', {}).get('count', None)
                item['from'] = 'instagram'
                item['player_id'] = node.get('id')
                item['cover'] = node.get('display_url', '')
                item['author_id'] = node.get('owner', {}).get('id', None)
                item['title'] = node.get('title')
                item['view_count'] = node.get('video_view_count', '')
                item['playlist_url'] = tagurl.replace("?__a=1", "")
                shortcode = node.get('shortcode', None)
                if shortcode:
                    item['webpage_url'] = 'https://www.instagram.com/p/{}/'.format(shortcode)
                    await get_content_items(item['webpage_url'], item, session)
                    if item['duration'] is None:
                        continue
                    this_user_items.append(item)
        except:
            traceback.print_exc()
            return this_user_items, None, False
    returnparams = json.dumps(params)
    returnparams = base64.b64encode(returnparams.encode('utf-8'))
    return this_user_items, hasNext, {"continuation": "video", "clickTrackingParams": str(returnparams, 'utf-8')}


if __name__ == '__main__':
    async def test():
        return await breakdown("https://www.instagram.com/funnymike/")
        # params={'query_hash': 'f2405b236d85e8296cf30347c9f08c2a', 'id': '7144449623', 'first': 12, 'after': 'QVFDMVBUcGNPZzNNQWNOZmMyeUx1TUNVeFVQZi1PY3JzRUx0LWtWRW5yTF9lVGVMTjRMdm9qcVJZTXMyVU5JQkxSYlZ1LXFNbHFEdGhGWWlRRkY0ZUladA=='})


    # user = 'losangeles_eats'
    # tag = fetch_items(user)
    loop = asyncio.get_event_loop()
    res = loop.run_until_complete(test())
    from pprint import pprint

    pprint(res)
