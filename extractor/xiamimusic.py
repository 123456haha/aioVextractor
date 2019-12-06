#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 2019/6/20
# IDE: PyCharm

import jmespath
import re
import traceback
import asyncio

from aioVextractor.extractor.base_extractor import (
    BaseExtractor,
    validate,
    RequestRetry
)
import time
# from pyppeteer.errors import NetworkError
# import asyncio
import os


class Extractor(BaseExtractor):
    target_website = [
        "http[s]?://www\.xiami\.com/mv/\w{6}",
    ]

    TEST_CASE = [
        "任我行 https://www.xiami.com/mv/K66Fx9",
        "这样你还要爱我吗 https://www.xiami.com/mv/K66qP5"

    ]

    def __init__(self, *args, **kwargs):
        BaseExtractor.__init__(self, *args, **kwargs)
        self.from_ = "xiami"
        self.results = []
        self.last_response = time.time()


    @validate
    @RequestRetry
    async def entrance(self, webpage_url, session, *args, **kwargs):
        browser = await self.launch_browers()
        page = await browser.newPage()
        await page.goto(webpage_url)
        while time.time() - self.last_response < 3:
            await asyncio.sleep(0.1)
        page_text = await page.content()
        print(page_text)
        await browser.close()
        self.extract_page(response=page_text)
        # return self.results

    def extract_page(self, response):
        selector = self.Selector(text=response)
        result = {
            "play_addr": os.path.join("http://", selector.css("video::attr(src)").extract_first()),
            "title": selector.css("title::text").extract_first(),
            # "vid": re.findall('<input id="copy-link-input" value=".*?//.*?/mv/(.*?)">',response)[0],
            "cover": selector.css("video::attr(poster)").extract_first(),
            # "view_count": re.findall('<span class="mv__listen">播放量：(.*?)</span>',response)[0],
                  }
        print(result)
        # self.results.append(result)

if __name__ == '__main__':
    from pprint import pprint
    with Extractor() as extractor:
        res = extractor.sync_entrance(webpage_url=Extractor.TEST_CASE[-1])
        pprint(res)
