#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 10/07/19
# IDE: PyCharm

import jmespath
import platform
from scrapy import Selector
from aioVextractor.extractor.base_extractor import (
    BaseExtractor,
    validate,
    RequestRetry
)



if platform.system() in {"Linux", "Darwin"}:
    import ujson as json
else:
    import json

class Extractor(BaseExtractor):
    target_website = [
        "https://www\.pinterest\.com/pin/\d{15,23}",
    ]

    TEST_CASE = [
        "https://www.pinterest.com/pin/457256168416688731",
    ]

    def __init__(self, *args, **kwargs):
        BaseExtractor.__init__(self, *args, **kwargs)
        self.from_ = "pinterest"

    @validate
    @RequestRetry
    async def entrance(self, webpage_url, session):
        headers = self.general_headers(user_agent=self.random_ua())
        headers["Host"] = "www.pinterest.com"
        async with session.get(webpage_url, verify_ssl=False, headers=headers) as resp:
            html = await resp.text()
            selector = Selector(text=html)
            jsonstr = selector.css("#initial-state::text").extract_first()
            if not jsonstr:
                return None
            jsondata = json.loads(jsonstr)
            item = dict()
            data = jmespath.search("resourceResponses[0].response.data", jsondata)
            videos = jmespath.search("videos", data)
            item['vid'] = data.get('id')
            item['webpage_url'] = "https://www.pinterest.com/pin/" + item['vid']
            iname = ["orig", "736x", "564x", "474x", "600x315"]
            for inn in iname:
                if item.get("cover"):
                    break
                item['cover'] = jmespath.search(f"images.{inn}.url", data)
            pn = ["V_720P", "V_HLSV3_MOBILE", "V_HLSV3_WEB", "V_HLSV4"]
            for n in pn:
                if item.get("duration"):
                    break
                item['play_addr'] = jmespath.search(f"video_list.{n}.url", videos)
                if not item.get('cover'):
                    item['cover'] = jmespath.search(f"video_list.{n}.thumbnail", videos)
                item['duration'] = jmespath.search(f"video_list.{n}.duration", videos) // 1000
                item['width'] = jmespath.search(f"video_list.{n}.width", videos)
                item['height'] = jmespath.search(f"video_list.{n}.height", videos)

            item['title'] = data.get("grid_title")
            item['description'] = jmespath.search("rich_summary.display_description", data)
            item['description'] = data.get("description") if not item['description'] else None
            item['ad_link'] = data.get("tracked_link")
            pinner = data.get("pinner")
            if pinner:
                item['author'] = pinner.get("full_name")
                item['author_id'] = pinner.get("id")
                item['author_avatar'] = pinner.get("image_large_url")
                item['author_avatar'] = pinner.get("image_small_url") if not item['author_avatar'] else None
                # item['author_url'] = webpage_url
            item['comment_count'] = data.get("comment_count", 0)
            item['from'] = self.from_
            return item

if __name__ == '__main__':
    from pprint import pprint
    with Extractor() as extractor:
        res = extractor.sync_entrance(webpage_url="https://www.pinterest.com/pin/785667097477427570/?nic=1")
        pprint(res)
