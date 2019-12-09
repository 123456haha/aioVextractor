#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 2019/6/20
# IDE: PyCharm

import re, json
from bs4 import BeautifulSoup
from aioVextractor.extractor.base_extractor import (
    BaseExtractor,
    validate,
    RequestRetry)


class Extractor(BaseExtractor):
    target_website = [
        "https://h.xiami.com/mv_detail.html\?id=\w{6}",
    ]
    TEST_CASE = [
        "MV分享 | 黄义达-那女孩对我说 https://h.xiami.com/mv_detail.html?id=K6hFe7 (分享自@虾米音乐)",
        "MV分享 | 丸子呦-广寒宫 https://h.xiami.com/mv_detail.html?id=K6hX1j (分享自@虾米音乐)",
    ]

    def __init__(self, *args, **kwargs):
        BaseExtractor.__init__(self, *args, **kwargs)
        self.from_ = "xiami"

    @validate
    @RequestRetry
    async def entrance(self, webpage_url, session, *args, **kwargs):
        headers = {
            'authority': 'm.xiami.com',
            'upgrade-insecure-requests': '1',
            'user-agent': self.random_ua(),
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
            'sec-fetch-site': 'same-site',
            'sec-fetch-mode': 'navigate',
            'referer': webpage_url,
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'zh-CN,zh;q=0.9',
        }
        vid = re.findall("id=(\w{2,10})", webpage_url)[0]
        webpage_url = f"https://m.xiami.com/mv/K6hX1j?id={vid}"
        text = await self.request(
            url=webpage_url,
            session=session,
            headers=headers,
        )
        item = dict()
        soup = BeautifulSoup(text, 'lxml')
        title = soup.find('p', attrs={"class": "mv-detail-name text-overflow-ellipsis"})
        item['name'] = title.text
        count = soup.find('p', attrs={"class": "mv-detail-view-count"})
        item['count'] = count.text
        like_count = soup.find('a', attrs={"class": "iconfont"})
        item['like_count'] = like_count.text
        author = soup.find('p', attrs={"class": "artist-name text-overflow-ellipsis"})
        item['author'] = author.text
        datas = re.findall("<script>window.__PRELOADED_STATE__ = ([\S|\s].*)</script>", text)
        if datas:
            data = json.loads(datas[0])['mvDetail']['mvDetails']['mvDetailVO']
            item['vid'] = data['mvId']
            item['cover'] = data['mvCover']
            item['play_addr'] = data['mp4Url']
        return item


if __name__ == '__main__':
    from pprint import pprint

    with Extractor() as extractor:
        res = extractor.sync_entrance(webpage_url=Extractor.TEST_CASE[-1])
        pprint(res)
