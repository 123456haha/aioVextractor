#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 2019/7/1
# IDE: PyCharm

from aioVextractor.extractor.base_extractor import (BaseExtractor, validate, RequestRetry)


class Extractor(BaseExtractor):
    """
    Extract iframe url from webpage_url
    """
    TEST_CASE = [
        "http://peacefulcuisine.com/category/videos/#",
    ]
    @validate
    @RequestRetry
    async def entrance(self, webpage_url, session, *args, **kwargs):
        results = await self.breakdown(webpage_url=webpage_url)
        return results



if __name__ == '__main__':
    from pprint import pprint
    with Extractor() as extractor:
        res = extractor.sync_entrance(webpage_url="https://www.behance.net/gallery/86216105/GOGORO-VIVA-LOGO-ANIMATION")
        pprint(res)
