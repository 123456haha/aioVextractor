#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 2019/6/20
# IDE: PyCharm

from aioVextractor.player import xinpianchang
from aioVextractor.extractor.base_extractor import (
    BaseExtractor,
    validate,
    RequestRetry
)

TEST_CASE = [
    "https://www.xinpianchang.com/a10475334?from=ArticleList",
]


class Extractor(BaseExtractor):
    target_website = [
        "www\.xinpianchang\.com/a\d{7,10}",
    ]

    def __init__(self, *args, **kwargs):
        BaseExtractor.__init__(self, *args, **kwargs)
        self.from_ = "xinpianchang"

    @validate
    @RequestRetry
    async def entrance(self, webpage_url, session):
        return await xinpianchang.entrance(webpage_url=webpage_url, session=session)


if __name__ == '__main__':
    from pprint import pprint

    with Extractor() as extractor:
        res = extractor.sync_entrance(webpage_url="https://www.xinpianchang.com/a10475334?from=ArticleList")
        pprint(res)
