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

TEST_CASE = [
    "https://mp.weixin.qq.com/s/IqbmeLcurLXvCj-LefJfYw"
]




class Extractor(BaseExtractor):
    target_website = [
        "https://mp\.weixin\.qq\.com/s/[\w-]{10,36}",
    ]

    def __init__(self, *args, **kwargs):
        BaseExtractor.__init__(self, *args, **kwargs)
        self.from_ = "weixin"

    @validate
    @RequestRetry
    async def entrance(self, webpage_url, session):
        headers = self.general_headers(user_agent=self.random_ua())
        async with session.get(webpage_url, headers=headers) as response:
            text = await response.text(encoding='utf8', errors='ignore')
            selector = Selector(text=text)
            urls = selector.css('iframe[data-src]::attr(data-src)').extract()
            if not urls:
                return False
            results = await asyncio.gather(
                *[self.extract_iframe(iframe_url=iframe_url, session=session) for iframe_url in urls])
            for ele in results:
                if ele:
                    ele['from'] = self.from_
                    ele['webpage_url'] = webpage_url
            return results

if __name__ == '__main__':
    from pprint import pprint

    with Extractor() as extractor:
        res = extractor.sync_entrance(webpage_url="https://mp.weixin.qq.com/s/IqbmeLcurLXvCj-LefJfYw")
        pprint(res)
