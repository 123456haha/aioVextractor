#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 1/21/19
# IDE: PyCharm

from scrapy.selector import Selector
import asyncio
import jmespath
from urllib.parse import unquote
from aioVextractor.extractor.base_extractor import (
    BaseExtractor,
    validate,
    RequestRetry
)


class Extractor(BaseExtractor):
    target_website = [
        "http[s]?://mp\.weixin\.qq\.com/s/[\w-]{10,36}",
    ]

    TEST_CASE = [
        # "https://mp.weixin.qq.com/s/IqbmeLcurLXvCj-LefJfYw",
        # "https://mp.weixin.qq.com/s/PZ0JBxMIAP5zVhsSxpxu7Q",
        "http://mp.weixin.qq.com/s/2Y5rEq4HXtOAcHtYBNeebQ",
        # "https://mp.weixin.qq.com/s/Ld6tw7ZjzFcUkPXa79HH5Q",
        # "https://mp.weixin.qq.com/s/6lDIjP799J2b07RHoNil1A",
        # "https://mp.weixin.qq.com/s/yjzmRFDEwJgXDfGaK_ooUQ",
    ]

    def __init__(self, *args, **kwargs):
        BaseExtractor.__init__(self, *args, **kwargs)
        self.from_ = "weixin"
        self.results = []
        self.result = []

    @validate
    @RequestRetry
    async def entrance(self, webpage_url, session, *args, **kwargs):
        await asyncio.gather(
            self.version_uno(webpage_url=webpage_url, session=session),
            self.version_dos(webpage_url=webpage_url),
                                       )
        return self.results


    async def version_uno(self, webpage_url, session):
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
        self.results += outputs

    async def version_dos(self, webpage_url):
        browser = await self.launch_browers()
        page = await browser.newPage()
        page.on('response', self.intercept_response)
        await page.goto(webpage_url)
        await asyncio.sleep(2)
        await page.evaluate('window.scrollTo(0,document.body.scrollHeight)')
        response_text = await page.content()
        selector = Selector(text=response_text)
        cover_list = list(map(lambda x:unquote(x), selector.css(".video_iframe::attr(data-cover)").extract()))
        for num, ele in enumerate(self.result):
            ele["cover"] = cover_list[num]
            ele["webpage_url"] = webpage_url
        self.results += self.result
        # await page.waitForResponse(lambda response: "mp.weixin.qq.com/mp/videoplayer" in response.url)
        # await page.waitForRequest(lambda response: "mp.weixin.qq.com/mp/videoplayer" in response.url, timeout=3)
        await browser.close()


    async def intercept_response(self, response):
        resourceType = response.request.resourceType
        if resourceType in ['xhr'] and 'mp.weixin.qq.com/mp/videoplayer' in response.url:
            response_json = await response.json()
            self.extract_page(response=response_json)

    def extract_page(self, response):
        result = jmespath.search('max_by(url_info, &width).{'
                '"play_addr": url,'
                '"width": width,'
                '"height": height,'
                '"duration": duration_ms'
                '}', response)
        result['duration'] = result['duration']//1000 if result['duration'] else None
        result['vid'] =  result['play_addr'].split("/")[-1].split(".")[0]
        result['from'] =  self.from_
        self.result.append(result)


if __name__ == '__main__':
    from pprint import pprint

    with Extractor() as extractor:
        res = extractor.sync_entrance(webpage_url=Extractor.TEST_CASE[-1])
        pprint(res)
