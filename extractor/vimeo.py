#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 2019/6/20
# IDE: PyCharm


import traceback
import asyncio
from aioVextractor.utils.user_agent import safari
from random import choice
from scrapy import Selector
from aioVextractor.extractor.base_extractor import (
    BaseExtractor,
    validate,
    RequestRetry
)

TEST_CASE = [
    "https://vimeo.com/281493330",
    "https://vimeo.com/344361560",
]



class Extractor(BaseExtractor):

    target_website = [
        "https://vimeo\.com/\d{7,18}"
    ]

    def __init__(self, *args, **kwargs):
        BaseExtractor.__init__(self, *args, **kwargs)
        self.from_ = "vimeo"


    @validate
    @RequestRetry
    async def entrance(self, webpage_url, session):

        try:
            gather_results = await asyncio.gather(*[
                self.extract_info(webpage_url=webpage_url),
                self.extract_author(webpage_url=webpage_url, session=session)
            ])
            if all(gather_results):
                return {**gather_results[0], **gather_results[1]}
            else:
                return False
        except:
            traceback.print_exc()
            return False

    @RequestRetry
    async def extract_author(self, webpage_url, session):
        headers = self.general_headers(user_agent=choice(safari))
        headers['Referer'] = 'https://vimeo.com/search?q=alita'
        async with session.get(webpage_url, headers=headers) as response:
            text = await response.text(encoding='utf8', errors='ignore')
            regex = '"portrait":\{"src":".*?",\s*"src_2x":"(.*?)"\},'
            selector = Selector(text=text)
            try:
                clip_page_config = selector.css('script').re_first(regex)
            except TypeError:
                return False
            else:
                avatar = clip_page_config.replace('\\/', '/')
            return {"author_avatar": avatar,
                    'from': self.from_
                    }



if __name__ == '__main__':
    from pprint import pprint
    with Extractor() as extractor:
        res = extractor.sync_entrance(webpage_url="https://creative.adquan.com/show/286808")
        pprint(res)

