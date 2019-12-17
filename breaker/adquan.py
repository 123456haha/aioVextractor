#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 2019/7/6
# IDE: PyCharm

import re,json
from aioVextractor.utils import RequestRetry
from aioVextractor.breaker import (
    BaseBreaker,
    BreakerValidater
)


class Breaker(BaseBreaker):
    target_website = [
        "http[s]?://creative\.adquan\.com/",
    ]

    downloader = 'ytd'

    TEST_CASE = [
        "https://creative.adquan.com/",
    ]

    def __init__(self, *args, **kwargs):
        BaseBreaker.__init__(self, *args, **kwargs)
        self.from_ = "adquan"

    @BreakerValidater
    @RequestRetry
    async def breakdown(self, webpage_url, session, **kwargs):
        page = int(kwargs.pop("page", 2))
        if page-1 == 0:
            size = 16
        else:
            size =12
        cookies = {
            'Hm_lvt_b9772bb26f0ebb4e77be78655c6aba4e': '1575882598',
            'acw_tc': '65c86a0a15758827064914767eb58249973cec5a9a242bdf48e19abbf4d8c3',
            'area': 'eyJpdiI6IllPSEp0eXFZNG1RaExCQWhDbWI3WGc9PSIsInZhbHVlIjoiTm54UTcxYURYYmFGa01aYmhkRjQ1UT09IiwibWFjIjoiMGM2ZGRhZGQ5OTliZmIyNGQxMzJiMTQ3MTRkNWJmZDJiNjM1OTNiNTM5Nzc4N2QzZmUyMWQ1YjIxMDIzN2JjZSJ9',
            'XSRF-TOKEN': 'eyJpdiI6IjREUzA3eFpHU1ZFQUlsaVwvTXhYZTJ3PT0iLCJ2YWx1ZSI6Ik5KbVdNWGxcL3M5N3N4cXZldXBGVzNoMlJHdklcLzAwUkkwdHN2YUdSbVd3OWdBaE9oY1h4SndRSzZZZlc1eHZSSTlQakx4dzNuMWJQZjViWE53dEs2TXc9PSIsIm1hYyI6ImE1N2E5MGJiMzQyZGQ4MTM5N2MzYjMwMWYxNjEzNmQ0OTQ4ODE4NjM0MTVmYzY5ZTE3NGE0MWIyNDM1YTkxYTIifQ%3D%3D',
            'laravel_session_production': 'eyJpdiI6ImpTT0E1c3ZjNzZxSERVR0FpeEVKRUE9PSIsInZhbHVlIjoiNkkxZlhXSWlQKzdDTlwvelpHZzVQd3o5ZUxuTkl3QmxDeTBuSkQxMVgzTGdjVzZ4TVwvOFNBTkVCMlRVMG92ZTVLRUNsYk5HMFdWOStKSnRLTWpzZTArUT09IiwibWFjIjoiMWI2MTM1NGUxMmFhNzI0MDc2Yzk3Y2NkMmUzMTM3MzI1MGU2ODFjNjhkZmJkMDYxYmY2MTI5ZDdlNDkzZjdmOSJ9',
            'SERVERID': '235be1bfd767f5d87ef3d43a3712e539|1576477834|1576476617',
            'Hm_lpvt_b9772bb26f0ebb4e77be78655c6aba4e': '1576477845',
        }

        headers = {
            'Connection': 'keep-alive',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'X-CSRF-TOKEN': 'rstksiFz2ee3JAHMGzpyMdi2fOHbFg3dunbzh4tE',
            'X-Requested-With': 'XMLHttpRequest',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'cors',
            'Referer': 'https://creative.adquan.com/',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9',
        }

        params = (
            ('size', size),
            ('p', page-1),
            ('industry', '0'),
            ('typeclass', '0'),
            ('area', '0'),
            ('word', ''),
            ('searchtype', '0'),
            ('filter', '1'),
        )
        api = 'https://creative.adquan.com/more_case'
        clips = await self.request(
            url=api,
            session=session,
            cookies=cookies,
            headers=headers,
            params=params,
        )
        html = json.loads(clips)

        datas = re.findall('<li>([\s\S]*?)</a></h2>',str(html))
        url = 'https://creative.adquan.com'
        for data in datas:
            webpage_url = url + re.findall('<a class="title_img" href="(.*?)"',data)[0]








if __name__ == '__main__':
    from pprint import pprint

    with Breaker() as breaker:
        res = breaker.sync_breakdown(
            webpage_url=Breaker.TEST_CASE[0],
            # page=2,
        )
        pprint(res)
