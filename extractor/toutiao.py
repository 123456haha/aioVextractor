#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 2019/6/20
# IDE: PyCharm

from bs4 import BeautifulSoup
import re, json, time
import traceback
from aioVextractor.extractor.base_extractor import (
    BaseExtractor,
    validate,
    RequestRetry
)

class Extractor(BaseExtractor):
    target_website = [
        "http[s]?://m\.toutiaoimg\.com/a\d{10,36}",
        "http[s]?://m\.toutiaocdn\.com/a\d{10,36}",
        "http[s]?://m\.toutiaoimg\.cn/group/\d{10,36}",
        "http[s]?://m\.toutiaocdn\.net/a\d{10,36}}",
        "http[s]?://m\.toutiaocdn\.com/i\d{10,36}",
        "http[s]?://m\.toutiaoimg\.com/group/\d{10,36}",
    ]

    TEST_CASE = [
        "https://m.toutiaoimg.com/a6731923698707595790/?app=news_article&is_hit_share_recommend=0",
        "雨桐的电影: 气质这一块没输过！https://m.toutiaoimg.cn/group/6747521740714429707/?app=news_article&timestamp=1572243832",
        "https://m.toutiaocdn.com/a6752189114830815757/?app=news_article&is_hit_share_recommend=0",
        "https://m.toutiaocdn.net/a6752504513917092359/?app=news_article&is_hit_share_recommend=0",
        "https://m.toutiaocdn.com/i6752291249207640590/?app=news_article&timestamp=1572147617&req_id=201910271140170100140481310BDEA279&group_id=6752291249207640590&wxshare_count=20&tt_from=weixin_moments&utm_source=weixin_moments&utm_medium=toutiao_android&utm_campaign=client_share&share_type=original&pbid=6751721020236875277&from=singlemessage&isappinstalled=0",
        "https://m.toutiaoimg.com/group/6739755269032509966/?app=news_article_lite&timestamp=1572244151&req_id=20191028142911010011048231030168A8&group_id=6739755269032509966",
    ]

    def __init__(self, *args, **kwargs):
        BaseExtractor.__init__(self, *args, **kwargs)
        self.from_ = "toutiao"

    @validate
    @RequestRetry
    async def entrance(self, webpage_url, session, *args, **kwargs):
        pass

if __name__ == '__main__':
    from pprint import pprint
    with Extractor() as extractor:
        res = extractor.sync_entrance(webpage_url=Extractor.TEST_CASE[0])
        pprint(res)

