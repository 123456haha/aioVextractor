#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 2019/6/20
# IDE: PyCharm

from scrapy import Selector
import re
from urllib.parse import unquote
import platform
import jmespath
from aioVextractor.extractor.base_extractor import (
    BaseExtractor,
    validate,
    RequestRetry
)

TEST_CASE = [
    "https://weibo.com/tv/v/I5RTQlExh?fid=1034:4413979699688929",
    "https://weibo.com/tv/v/FxTBC1Dp8?from=vhot",
    "https://weibo.com/tv/v/Ib31ooLdE?fid=1034:4426329710596386",
    "https://weibo.com/tv/v/IbOnau1mu?fid=1034:4428150730652786",
    "https://weibo.com/tv/v/IbFq32OZd?fid=1034:4427803702006591",
    "https://weibo.com/tv/v/I4YSOoeCp?fid=1034:4411872741380331",
    "https://m.weibo.cn/status/4428801453021670?wm=3333_2001&from=109A193010&sourcetype=dingding",
    "http://t.cn/Ai8Bj0z6",
    "https://m.weibo.cn/status/4428801453021670?wm=3333_2001&from=109A193010&sourcetype=dingding",

]



if platform.system() in {"Linux", "Darwin"}:
    import ujson as json
else:
    import json

class Extractor(BaseExtractor):
    target_website = [
        "https://m\.weibo\.cn/status/\d{5,25}",
        "https://weibo\.com/tv/v/[\w]{5,15}\?fid=1034\:\d{5,25}",
        "https://weibo\.com/tv/v/[\w]{5,15}\?from=\w{1,10}",
        "http://t\.cn/[\w-]{3,10}",
    ]

    def __init__(self, *args, **kwargs):
        BaseExtractor.__init__(self, *args, **kwargs)
        self.from_ = "weibo"

    @validate
    @RequestRetry
    async def entrance(self, webpage_url, session):
        if re.match("https://m\.weibo\.cn/status/\d{5,25}", webpage_url):
            headers = {
                'Upgrade-Insecure-Requests': '1',
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) '
                              'AppleWebKit/537.36 (KHTML, like Gecko) '
                              'Chrome/77.0.3865.120 Safari/537.36',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-User': '?1',
            }
            async with session.get(webpage_url, headers=headers) as response:
                response_text = await response.text()
                results = self.extract_mobile(response=response_text)
                return results

        else:
            cookies = {
                'SUB': '_2AkMq-6mNf8NxqwJRmPEWymvraIVyyA7EieKcp1hWJRMxHRl-yT83qkhYtRB6AXuHYVsPmdY9Wu5j06JDOol1qhbRJy9F',
                'SUBP': '0033WrSXqPxfM72-Ws9jqgMF55529P9D9WWbYnYe01JZdLbuWoMQUQVL',
                '_s_tentry': 'passport.weibo.com',
                'Apache': '1084672131205.1a599.1571235515822',
                'SINAGLOBAL': '1084672131205.1599.1571235515822',
                'ULV': '1571235515827:1:1:1:1084672131205.1599.1571235515822:',
                'YF-V5-G0': '27518b2dd3c605fe277ffc0b4f0575b3',
                'YF-Page-G0': 'f1e19cba80f4eeaeea445d7b50e14ebb|1571236449|1571236248',
            }
            headers = {
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.108 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,ko;q=0.7',
            }

            async with session.get(webpage_url, headers=headers, cookies=cookies) as response:
                text = await response.text()
                results = self.extract(response=text, webpage_url=webpage_url)
                return results

    def extract(self, response, webpage_url):
        try:
            selector = Selector(text=response)
        except:
            return None
        result = dict()
        result['from'] = self.from_
        result['title'] = selector.css(".player_info .info_txt::text").extract_first()
        result['avatar'] = selector.css(".player_info .W_face_radius img::attr(src)").extract_first()
        result['author'] = selector.css('.player_info span[class*="name"]::text').extract_first()
        action_data = unquote(selector.css('div[node-type*="common_video_player"]::attr(action-data)').extract_first())
        result['vid'] = re.search("objectid=\d*?:([\d]{1,25})", action_data).group(1)
        result['author_id'] = re.search("uid=(\d{1,36})", action_data).group(1)
        result['play_addr'] = "http://" + re.search("video_src=//([\s|\S]{1,250})&cover_img", action_data).group(1)
        result['cover'] = re.search("cover_img=([\s|\S]*?)&short_url", action_data).group(1)
        result['webpage_url'] = webpage_url

        return result

    def extract_mobile(self, response):
        try:
            selector = Selector(text=response)
            render_data = json.loads(selector.css("script").re_first("\$render_data = (\[[\s|\S]*?\])\[0\]"))[0]
            status = render_data['status']
        except:
            return None
        result = dict()
        result['from'] = self.from_
        result['vid'] = jmespath.search("id", status)
        result['author_id'] = jmespath.search("user.id", status)
        result['author'] = jmespath.search("user.screen_name", status)
        result['avatar'] = jmespath.search("user.avatar_hd", status)
        result['follower'] = jmespath.search("user.followers_count", status)
        result['comment_count'] = jmespath.search("comments_count", status)
        result['cover'] = jmespath.search("page_info.page_pic.url", status)
        result['webpage_url'] = jmespath.search("page_info.page_url", status)
        result['title'] = jmespath.search("page_info.title", status)
        result['description'] = jmespath.search("page_info.content2", status)
        try:
            result['duration'] = int(jmespath.search("page_info.media_info.duration", status))
        except:
            pass
        result['play_addr'] = jmespath.search("page_info.urls.mp4_720p_mp4", status)

        return result


if __name__ == '__main__':
    from pprint import pprint

    with Extractor() as extractor:
        res = extractor.sync_entrance(webpage_url="https://m.weibo.cn/status/4428801453021670?wm=3333_2001&from=109A193010&sourcetype=dingding")
        pprint(res)
