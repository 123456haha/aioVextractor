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
        "https://creative\.adquan\.com/show/\d{3,7}",
        "http://creative\.adquan\.com/show/\d{3,7}",
        "http://www\.adquan\.com/post-\d-\d{3,7}\.html$",
        "https://www\.adquan\.com/post-\d-\d{3,7}\.html$",
    ]

    TEST_CASE = [
        "https://creative.adquan.com/show/286788",
        "https://creative.adquan.com/show/286778",
        "http://www.adquan.com/post-2-49507.html",
        "http://creative.adquan.com/show/49469",
        "http://creative.adquan.com/show/49415",
    ]

    def __init__(self, *args, **kwargs):
        BaseExtractor.__init__(self, *args, **kwargs)
        self.from_ = "adquan"

    @validate
    @RequestRetry
    async def entrance(self, webpage_url, session):
        headers = self.general_headers(user_agent=self.random_ua())
        headers['Referer'] = webpage_url
        cookies = {
            'acw_sc__v2': '5d53aa5bb49e0baea03a2f7ea7c2988205474261',
        }
        async with session.get(webpage_url, headers=headers, cookies=cookies) as response:
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
        res = extractor.sync_entrance(webpage_url="https://creative.adquan.com/show/286808")
        pprint(res)
