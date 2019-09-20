import asyncio
import aiohttp, json, time
from aioVextractor.utils.requests_retry import *
import emoji


@RequestRetry
async def entrance(webpage_url, session):
    if "/p/" in webpage_url:
        item = dict()
        await get_content_items(webpage_url, item, session)
        return item
    elif "/tv/" in webpage_url:
        return await GetTVData(webpage_url, session)
    else:
        videolist = await get_items_by_user(webpage_url, session)
        return videolist


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
            item['width'] = shortcode_media.get("dimensions",{}).get("width")
            item['height'] = shortcode_media.get("dimensions",{}).get("height")
            item['author'] = shortcode_media.get("owner",{}).get("username")
            item['author_id'] = shortcode_media.get("owner",{}).get("id")
            item['author_avatar'] = shortcode_media.get("owner",{}).get("profile_pic_url")
            if item['author']:
                item['author_url'] = "https://www.instagram.com/" + item['author']
        except:
            traceback.print_exc()


@RequestRetry
async def get_items_by_user(tagurl, session):
    this_user_items = []
    # if not username:
    #     return this_user_items
    # tagurl = 'https://www.instagram.com/{}/?__a=1'.format(username)
    if not tagurl:
        return this_user_items
    if tagurl[-1] != '/':
        tagurl = tagurl+'/?__a=1'
    else:
        tagurl = tagurl+'?__a=1'
    async with session.get(tagurl, verify_ssl=False) as resp:
        html = await resp.text(encoding='utf-8', errors="ignore")
        try:
            jsondata = json.loads(html)
            user = jsondata.get('graphql', {}).get('user', None)
            if not user:
                return this_user_items
            videolist = user.get('edge_owner_to_timeline_media', {}).get('edges', [])
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
                shortcode = node.get('shortcode', None)
                if shortcode:
                    item['webpage_url'] = 'https://www.instagram.com/p/{}/'.format(shortcode)
                    await get_content_items(item['webpage_url'], item, session)
                    if item['duration'] is None:
                        continue
                    this_user_items.append(item)
        except Exception as e:
            print(e)
            import traceback
            print(traceback.format_exc())
            return this_user_items
    return this_user_items


async def fetch_items(username):
    conn = aiohttp.TCPConnector(ssl=False)
    async with aiohttp.ClientSession(connector=conn) as session:
        return await get_items_by_user(username, session)

@RequestRetry
async def entrance(webpage_url, session):
    if "/p/" in webpage_url:
        item = dict()
        await get_content_items(webpage_url, item, session)
        return item
    elif "/tv/" in webpage_url:
        return await GetTVData(webpage_url,session)
    else:
        videolist = await get_items_by_user(webpage_url,session)
        return videolist

async def GetTVData(webpage_url,session):
    if webpage_url.endswith("/"):
        tagurl = webpage_url+"?__a=1"
    else:
        tagurl = webpage_url.split("#")[0] +"/?__a=1"
    item = dict()
    async with session.get(tagurl, verify_ssl=False) as resp:
        try:
            html = await resp.text(encoding='utf-8', errors='ignore')
            jsondata = json.loads(html)
            # print(json.dumps(jsondata))
            shortcode_media = jsondata.get('graphql', {}).get('shortcode_media', None)
            if not shortcode_media:
                return
            item['play_addr'] = shortcode_media.get('video_url', None)
            item['description'] = emoji.demojize(
                shortcode_media.get('edge_media_to_caption', {}).get('edges', [{}])[0].get('node',
                                                                                           {}).get(
                    'text', ''))
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
            item['author_id'] = shortcode_media.get("owner",{}).get("id")
            item['author_avatar'] = shortcode_media.get("owner",{}).get("profile_pic_url")
            if item['author']:
                item['author_url'] = "https://www.instagram.com/" + item['author']
        except:
            traceback.print_exc()
    return item


TEST_CASE = [
    "https://www.instagram.com/p/B1G1rBiAa_8/",
]

if __name__ == '__main__':
    async def test():
        async with aiohttp.ClientSession() as session_:
            return await entrance("https://www.instagram.com/p/B1G1rBiAa_8/", session_)


    # user = 'losangeles_eats'
    # tag = fetch_items(user)
    loop = asyncio.get_event_loop()
    res = loop.run_until_complete(test())
    print(res)
