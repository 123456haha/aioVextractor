#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 1/21/19
# IDE: PyCharm

import re
from bs4 import BeautifulSoup
from aioVextractor.extractor.base_extractor import (
    BaseExtractor,
    validate,
    RequestRetry
)
from urllib.parse import unquote


class Extractor(BaseExtractor):
    target_website = [
        "http[s]?://mp\.weixin\.qq\.com/s/[\w-]{10,36}",
    ]

    TEST_CASE = [
        "https://mp.weixin.qq.com/s/IqbmeLcurLXvCj-LefJfYw",
        "https://mp.weixin.qq.com/s/PZ0JBxMIAP5zVhsSxpxu7Q",
        # "http://mp.weixin.qq.com/s/2Y5rEq4HXtOAcHtYBNeebQ",
        "https://mp.weixin.qq.com/s/Ld6tw7ZjzFcUkPXa79HH5Q",
        "https://mp.weixin.qq.com/s/6lDIjP799J2b07RHoNil1A",
        "https://mp.weixin.qq.com/s/yjzmRFDEwJgXDfGaK_ooUQ",
        "https://mp.weixin.qq.com/s/WR6EdO8CYcpRHvsOM62Tdw",
    ]

    def __init__(self, *args, **kwargs):
        BaseExtractor.__init__(self, *args, **kwargs)
        self.from_ = "weixin"

    @validate
    @RequestRetry
    async def entrance(self, webpage_url, session, *args, **kwargs):
        headers = {
            'authority': 'mp.weixin.qq.com',
            'origin': 'https://mp.weixin.qq.com',
            'x-requested-with': 'XMLHttpRequest',
            'user-agent': self.random_ua(),
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'accept': '*/*',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'cors',
            'referer': webpage_url,
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'zh-CN,zh;q=0.9',
            'cookie': 'tvfe_boss_uuid=40a1a90fe02e1541; '
                      'pgv_pvid=585509504; '
                      'rewardsn=; '
                      'wxtokenkey=777; '
                      'ua_id=7Oq2IR31TRYerQZIAAAAAO5-dmYN2D2W0TO7HAz1PsI=; '
                      'pgv_pvi=2672868352; '
                      'pgv_si=s7425719296',
        }
        text = await self.request(
            url=webpage_url,
            session=session,
            headers=headers
        )
        results = []
        iframes = re.findall('<iframe.*?data-cover="(.*?)".*?data-src="(.*?)">', text)
        for iframe in iframes:
            item = dict()
            selector = BeautifulSoup(text, 'lxml')
            title = selector.find('h2', attrs={"class": "rich_media_title"})
            item['title'] = title.text.strip()
            author = selector.find('a', attrs={"id": "js_name"})
            item['author'] = author.text.strip()
            # item['cover_list'] = selector.find('img', attrs={"class": "rich_pages "})
            item['play_addr'] = iframe[1].replace(";", "&")
            if re.match("https://mp.weixin.qq.com/mp/readtemplate", item['play_addr']):
                pass
                ## item['play_addr'] = self.test()

            ## 'https://mp.weixin.qq.com/mp/readtemplate?t=pages/video_player_tmpl&amp&action=mpvideo&amp&auto=0&amp&vid=wxv_1064559816019968002'
            ## 'https://mp.weixin.qq.com/mp/readtemplate?t=pages/video_player_tmpl&amp&action=mpvideo&amp&auto=0&amp&vid=wxv_1081584742547505153'
            ## 'https://v.qq.com/iframe/preview.html?width=500&amp&height=375&amp&auto=0&amp&vid=s0167ynbnt9'
            item['cover'] = unquote(iframe[0])
            item['vid'] = iframe[1].split(';')[-1].strip("vid=")
            results.append(item)
        return results


if __name__ == '__main__':
    from pprint import pprint

    with Extractor() as extractor:
        res = extractor.sync_entrance(webpage_url=Extractor.TEST_CASE[-1])
        pprint(res)

