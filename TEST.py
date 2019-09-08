#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 2019/9/9
# IDE: PyCharm
"""
RUN ME BEFORE GOING SERIOUS!
"""

if __name__ == '__main__':
    from aioVextractor import *
    from aioVextractor.extractor import *
    from pprint import pprint
    async def test():
        async with aiohttp.ClientSession() as session:
            for webpage_url in TEST_CASE:
                result = await extract(webpage_url=webpage_url, session=session)
                pprint(result)
                print("******************************************************")