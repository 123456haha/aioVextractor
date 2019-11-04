#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 1/21/19
# IDE: PyCharm

from scrapy.selector import Selector
import asyncio
from aioVextractor.extractor.base_extractor import (
    ExtractorMeta,
    BaseExtractor,
    validate,
    RequestRetry
)


class Extractor(BaseExtractor, ExtractorMeta):
    target_website = [
        "http[s]?://mp\.weixin\.qq\.com/s/[\w-]{10,36}",
    ]

    TEST_CASE = [
        "https://mp.weixin.qq.com/s/IqbmeLcurLXvCj-LefJfYw",
        "https://mp.weixin.qq.com/s/PZ0JBxMIAP5zVhsSxpxu7Q",
        "http://mp.weixin.qq.com/s/2Y5rEq4HXtOAcHtYBNeebQ",
        "https://mp.weixin.qq.com/s/PZ0JBxMIAP5zVhsSxpxu7Q",
    ]

    def __init__(self, *args, **kwargs):
        BaseExtractor.__init__(self, *args, **kwargs)
        self.from_ = "weixin"

    @validate
    @RequestRetry
    async def entrance(self, webpage_url, session, *args, **kwargs):
        headers = self.general_headers(user_agent=self.random_ua())
        text = await self.request(
            url=webpage_url,
            session=session,
            headers=headers
        )
        selector = Selector(text=text)
        urls = selector.css('iframe[data-src]::attr(data-src)').extract()
        if not urls:
            return False
        results = await asyncio.gather(
            *[
                self.extract_iframe(
                    iframe_url=iframe_url,
                    session=session
                )
                for iframe_url in urls
            ])

        outputs = []
        for result in results:
            for ele in result:
                if ele:
                    ele['from'] = self.from_
                    ele['webpage_url'] = webpage_url
                    outputs.append(ele)
        return outputs


if __name__ == '__main__':
    from pprint import pprint

    with Extractor() as extractor:
        res = extractor.sync_entrance(webpage_url=Extractor.TEST_CASE[-1])
        pprint(res)
