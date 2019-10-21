#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 2019/6/20
# IDE: PyCharm

from aioVextractor.player import tencent
from aioVextractor.extractor.base_extractor import (
    BaseExtractor,
    validate,
    RequestRetry
)



class Extractor(BaseExtractor):
    target_website = [
        "https://v\.qq\.com/x/page/\w{9,18}\.html",
        "https://v\.qq\.com/x/cover/\w{9,18}\.html",
    ]

    TEST_CASE = [
        "https://v.qq.com/x/page/s0886ag14xn.html",
        "https://v.qq.com/x/page/n0864edqzkl.html",
        "https://v.qq.com/x/page/s08899ss07p.html",
        "https://v.qq.com/x/cover/bzfkv5se8qaqel2.html",
        "https://v.qq.com/x/page/x0888utz1ni.html",
    ]

    def __init__(self, *args, **kwargs):
        BaseExtractor.__init__(self, *args, **kwargs)
        self.from_ = "tencent"

    @validate
    @RequestRetry
    async def entrance(self, webpage_url, session):
        return await tencent.entrance(webpage_url=webpage_url, session=session)


if __name__ == '__main__':
    from pprint import pprint
    with Extractor() as extractor:
        res = extractor.sync_entrance(webpage_url="https://creative.adquan.com/show/286808")
        pprint(res)
