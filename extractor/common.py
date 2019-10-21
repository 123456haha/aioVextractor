#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 2019/7/1
# IDE: PyCharm

TEST_CASE = [
    "https://www.bilibili.com/video/av5546345?spm_id_from=333.334.b_62696c695f646f756761.4",
]

from aioVextractor.extractor.base_extractor import (BaseExtractor, validate, RequestRetry)


class Extractor(BaseExtractor):
    """
    Extract iframe url from webpage_url
    """
    @validate
    @RequestRetry
    async def entrance(self, webpage_url, session):
        results = await self.breakdown(webpage_url=webpage_url)
        return results



if __name__ == '__main__':
    from pprint import pprint
    with Extractor() as extractor:
        res = extractor.sync_entrance(webpage_url="https://creative.adquan.com/show/286808")
        pprint(res)
