#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 1/28/19
# IDE: PyCharm

import jmespath
from scrapy.selector import Selector
import platform

if platform.system() in {"Linux", "Darwin"}:
    import ujson as json
else:
    import json


TEST_CASE = [
    "https://www.hellorf.com/video/show/15148543",
    "https://www.hellorf.com/video/show/11995691",
]

from aioVextractor.extractor.base_extractor import (BaseExtractor, validate, RequestRetry)


class Extractor(BaseExtractor):
    target_website = [
        "www\.hellorf\.com/video.show/\d{5,10}",
    ]

    def __init__(self, *args, **kwargs):
        BaseExtractor.__init__(self, *args, **kwargs)
        self.from_ = "hellorf"

    @validate
    @RequestRetry
    async def entrance(self, webpage_url, session):
        async with session.get(webpage_url, headers=self.general_headers(self.random_ua())) as response:
            response_text = await response.text(encoding='utf8', errors='ignore')
            selector = Selector(text=response_text)
            result = dict()
            video_json = json.loads(selector.css('#__NEXT_DATA__::text').re_first('([\s|\S]*)'))
            result['author'] = jmespath.search('props.pageProps.initialProps.detail.contributor.display_name',
                                               video_json)
            result['play_addr'] = jmespath.search('props.pageProps.initialProps.detail.video.preview_mp4_url',
                                                  video_json)
            result['title'] = jmespath.search('props.pageProps.initialProps.detail.video.description', video_json)
            result['vid'] = jmespath.search('props.pageProps.initialProps.detail.video.id', video_json)
            video_category = jmespath.search('props.pageProps.initialProps.detail.video.categories[].name', video_json)
            result['category'] = ','.join(video_category)
            result['cover'] = jmespath.search('props.pageProps.initialProps.detail.video.preview_jpg_url', video_json)
            result['duration'] = jmespath.search('props.pageProps.initialProps.detail.video.duration', video_json)
            result['tag'] = jmespath.search('props.pageProps.initialProps.detail.video.keywords', video_json)
            result['from'] = self.from_
            result['webpage_url'] = webpage_url
            return result

if __name__ == '__main__':
    from pprint import pprint
    with Extractor() as extractor:
        res = extractor.sync_entrance(webpage_url="https://creative.adquan.com/show/286808")
        pprint(res)

