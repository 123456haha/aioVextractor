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
        "http[s]?://creative\.adquan\.com/show/\d{3,7}",
        "http[s]?://www\.adquan\.com/post-\d-\d{3,7}\.html$",
        "http[s]?://mobile\.adquan\.com.*",
    ]

    TEST_CASE = [
        "https://creative.adquan.com/show/286788",
        "https://creative.adquan.com/show/286778",
        # "http://www.adquan.com/post-2-49507.html",
        "http://creative.adquan.com/show/49469",
        "http://creative.adquan.com/show/49415",
        "https://mobile.adquan.com/creative/detail/288096",
    ]

    def __init__(self, *args, **kwargs):
        BaseExtractor.__init__(self, *args, **kwargs)
        self.from_ = "adquan"

    @validate
    @RequestRetry
    async def entrance(self, webpage_url, session, *args, **kwargs):
        headers = self.general_headers(user_agent=self.random_ua())
        headers['Referer'] = webpage_url
        Cookie = 'Hm_lvt_b9772bb26f0ebb4e77be78655c6aba4e=1575882598; ' \
                 'acw_tc=65c86a0c15758827105424225eba98fda6d222f47abc0f66507ad18b9ee8b0; ' \
                 'area=eyJpdiI6IllPSEp0eXFZNG1RaExCQWhDbWI3WGc9PSIsInZhbHVlIjoiTm54UTcxYURYYmFGa01aYmhkRjQ1UT09IiwibWFjIjoiMGM2ZGRhZGQ5OTliZmIyNGQxMzJiMTQ3MTRkNWJmZDJiNjM1OTNiNTM5Nzc4N2QzZmUyMWQ1YjIxMDIzN2JjZSJ9; ' \
                 'acw_sc__v2=5def5e44c6e696eb3d9dcc5e3400e1bc1930a9b8; ' \
                 'acw_sc__v3=5def5e4673266e5ec7ff4cdbd04589ba88e76e32; ' \
                 'Hm_lpvt_b9772bb26f0ebb4e77be78655c6aba4e=1575968408; ' \
                 'XSRF-TOKEN=eyJpdiI6IjNPRG92WEVTbkpJdjJ2NjR0OWxOY0E9PSIsInZhbHVlIjoiXC94K1N4TU9KWCtVRUJQWDRQOEFZXC9XTmtOb1ErS2pCSzRQazZXVTh0Wk94dCs5T1ZqWjVKaWRwbHhWTE9OXC9oMGdJUmpuZWRuMmNPNnQwMWZ0elg5Y2c9PSIsIm1hYyI6IjIzODBmZGMwNDE1NmNmNmExMTM3MmE3YmQ1NWU0OTkyNDgwOGNlMTg0Mzc0ZTZlMzhiOTZmZjU3MzBjOTA4YTYifQ%3D%3D; ' \
                 'laravel_session_production=eyJpdiI6IkJcL3h6dkpLeVN4R1wvY1VkOGRTV1VqUT09IiwidmFsdWUiOiJibGl2RklWREtkMW55dW0xeE1aaDdHSVR1TXRPRHk0K3RyMzlUblNHTFA5b05NS3hpTndvSk1WSHN3ME9ublVkdzBlQk11S3FGTFk2YktrXC8ycEdQSWc9PSIsIm1hYyI6ImRkMTc1MTM1OTQ0OTFiMGRkZTg1M2MzZmFkODljNzYzOGM1OWEzMWY3NTY2NmZkMTdlMDU2ODk1YzFmMWUzNzUifQ%3D%3D; ' \
                 'SERVERID=235be1bfd767f5d87ef3d43a3712e539|1575968407|1575968325'
        # Cookie = ''
        headers['Cookie'] = Cookie
        # cookies = {
        #     'acw_sc__v2': '5d53aa5bb49e0baea03a2f7ea7c2988205474261',
        #
        # }

        text = await self.request(
            url=webpage_url,
            session=session,
            headers=headers,
            # cookies=cookies
        )
        selector = Selector(text=text)
        youku_urls = selector.css("iframe[src*='player.youku.com']::attr(src)").extract()
        tencent_urls = selector.css('iframe[src*="v.qq"]::attr(src)').extract()
        urls = youku_urls + tencent_urls
        if not urls:
            return False

        results = await asyncio.gather(
            *[
                self.extract_iframe(
                    iframe_url=iframe_url,
                    session=session
                ) for iframe_url in urls
            ])
        outputs = []
        for result in results:
            for ele in result:
                if ele:
                    outputs.append(ele)
        return outputs


if __name__ == '__main__':
    from pprint import pprint

    with Extractor() as extractor:
        res = extractor.sync_entrance(Extractor.TEST_CASE[-1])
        pprint(res)
