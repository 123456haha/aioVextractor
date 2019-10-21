#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 1/21/19
# IDE: PyCharm

from scrapy.selector import Selector
import asyncio

TEST_CASE = [
    "https://www.digitaling.com/projects/55684.html",
    "https://www.digitaling.com/projects/56636.html",
    "https://www.digitaling.com/articles/105167.html",
]

from aioVextractor.extractor.base_extractor import (BaseExtractor, validate, RequestRetry)

class Extractor(BaseExtractor):
    target_website = [
        "https://www\.digitaling\.com/projects/\d{3,7}\.html",
        "https://www\.digitaling\.com/articles/\d{3,7}\.html",
    ]

    def __init__(self, *args, **kwargs):
        BaseExtractor.__init__(self, *args, **kwargs)
        self.from_ = "digitaling"

    @validate
    @RequestRetry
    async def entrance(self, webpage_url, session):
        headers = self.general_headers(user_agent=self.random_ua())
        headers['Referer'] = webpage_url
        async with session.get(webpage_url, headers=headers) as response:
            text = await response.text(errors='ignore')
            selector = Selector(text=text)
            youku_urls = selector.css("iframe[src*='player.youku.com']::attr(src)").extract()
            tencent_urls = selector.css('iframe[src*="v.qq"]::attr(src)').extract()
            urls = youku_urls + tencent_urls
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
        res = extractor.sync_entrance(webpage_url="https://www.digitaling.com/articles/105167.html")
        pprint(res)
