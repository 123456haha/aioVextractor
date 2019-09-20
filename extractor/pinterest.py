import asyncio
import aiohttp, json ,time
from aioVextractor.utils.requests_retry import *
import emoji
import re

@RequestRetry
async def ExtractOne(webpage_url, session):
    headers = {
        "Host":"www.pinterest.com",
        "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36"
    }
    async with session.get(webpage_url, verify_ssl=False,headers=headers) as resp:
        html = await resp.text()
        try:
            jsonstr = re.findall("<script type='application/json' id='jsInit1'>(.*?)</script>",html)
            if not jsonstr:
                return []
            jsondata = json.loads(jsonstr[0])
            # print(jsondata)
            resourceDataCache = jsondata.get("resourceDataCache")
            video = resourceDataCache[0].get("data")
            v = video.get("videos")
            item = dict()
            item['vid'] = video.get('id')
            item['webpage_url'] = "https://www.pinterest.com/pin/"+video.get('id')
            iname = ["orig","736x","564x","474x","600x315"]
            for inn in iname:
                if item.get("cover"):
                    break
                item['cover'] = video.get("images",{}).get(inn,{}).get("url")
            pn = ["V_720P","V_HLSV3_MOBILE","V_HLSV3_WEB","V_HLSV4"]
            for n in pn:
                if item.get("duration"):
                    break
                item['play_addr'] = v.get("video_list",{}).get(n,{}).get("url")
                if not item.get('cover'):
                    item['cover'] = v.get("video_list",{}).get(n,{}).get("thumbnail")
                item['duration'] = v.get("video_list",{}).get(n,{}).get("duration")//1000
                item['width'] = v.get("video_list",{}).get(n,{}).get("width")
                item['height'] = v.get("video_list",{}).get(n,{}).get("height")
            item['title'] = video.get("grid_title")
            rich_summary = video.get("rich_summary",{})
            if rich_summary:
                item['description'] = emoji.demojize(rich_summary.get("display_description"))
            else:
                item['description'] = ''
            if not item['description']:
                item['description'] = video.get("description")
            item['ad_link'] = video.get("tracked_link")
            pinner = video.get("pinner")
            if pinner:
                item['author'] = pinner.get("full_name")
                item['author_id'] = pinner.get("id")
                item['author_avatar'] = pinner.get("image_large_url")
                if not item['author_avatar']:
                    item['author_avatar'] = pinner.get("image_small_url")
                item['author_url'] = webpage_url
            item['comment_count'] = video.get("comment_count",0)
            item['from'] ='pinterest'
            return item
        except Exception as e:
            import traceback
            print(traceback.format_exc())
            print(e)
            return None

@RequestRetry
async def entrance(webpage_url, session,retry=0):
    if retry>=5:
        return None
    videolist = await ExtractOne(webpage_url,session)
    if not videolist:
        return await entrance(webpage_url,session,retry=retry+1)
    return videolist


TEST_CASE = [
    "https://www.pinterest.com/pin/457256168416688731",
]

async def test():
    async with aiohttp.ClientSession() as session_:
        return await entrance("https://www.pinterest.com/pin/457256168416688731", session_)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    res = loop.run_until_complete(test())
    print(res)
