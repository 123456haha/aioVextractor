#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 1/21/19
# IDE: PyCharm

from scrapy.selector import Selector
import asyncio
from aioVextractor.extractor.base_extractor import (
    BaseExtractor,
    validate,
    RequestRetry
)


class Extractor(BaseExtractor):
    target_website = [
        "http://iwebad\.com/video/\d{1,7}\.html",
    ]

    TEST_CASE = [
        "http://iwebad.com/video/3578.html",
        "http://iwebad.com/video/3577.html",
    ]

    def __init__(self, *args, **kwargs):
        BaseExtractor.__init__(self, *args, **kwargs)
        self.from_ = "iwebad"

    @validate
    @RequestRetry
    async def entrance(self, webpage_url, session):
        headers = self.general_headers(self.random_ua())
        headers['Referer'] = 'http://iwebad.com/'
        async with session.get(webpage_url, headers=headers) as response:
            response_text = await response.text(encoding='utf8', errors='ignore')
            selector = Selector(text=response_text)
            tencent_urls = selector.css('iframe[src*="v.qq"]::attr(src)').extract()
            youku_urls = selector.css("iframe[src*='player.youku.com']::attr(src)").extract()
            urls = tencent_urls + youku_urls
            if not urls:
                return False
            results = await asyncio.gather(
                *[self.extract_iframe(
                    iframe_url=iframe_url,
                    session=session
                ) for iframe_url in urls])
            for ele in results:
                if ele:
                    ele['from'] = self.from_
                    ele['webpage_url'] = webpage_url

            return results


if __name__ == '__main__':
    from pprint import pprint

    with Extractor() as extractor:
        res = extractor.sync_entrance(
            webpage_url="http://iwebad.com/video/3577.html,   http://iwebad.com/video/3578.html")
        pprint(res)
