#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 2019/6/20
# IDE: PyCharm

import jmespath
from aioVextractor.extractor.base_extractor import (
    BaseExtractor,
    validate,
    RequestRetry
)


class Extractor(BaseExtractor):
    target_website = [
        "http[s]?://www\.tvcbook\.com/showVideo\.html\?.*?vid=[\d]{1,10}",
        "http[s]?://www\.tvcbook\.com/showVideo_mobile\.html\?.*?vid=[\d]{1,10}",
    ]

    TEST_CASE = [
        "https://www.tvcbook.com/showVideo.html?vid=544444",
        "https://www.tvcbook.com/showVideo_mobile.html?vid=788239&code=f856T3YAgx7kcyaCyQ5jUIjkGKmh8-67TOvL0DQm1YjDkLBgsg",
    ]

    def __init__(self, *args, **kwargs):
        BaseExtractor.__init__(self, *args, **kwargs)
        self.from_ = "tvcbook"

    @validate
    @RequestRetry
    async def entrance(self, webpage_url, session, *args, **kwargs):
        vid = webpage_url.split("vid=")[1].split("&")[0]
        headers = {
            'authority': 'api.tvcbook.com',
            'cache-control': 'max-age=0',
            'upgrade-insecure-requests': '1',
            'user-agent': self.random_ua(),
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,ko;q=0.7',
        }
        response = await self.request(
            url=f'https://api.tvcbook.com/video/{vid}?access-token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJodHRwczpcL1wvYXBpeC50dmNib29rLmNvbVwvYXBpXC9hY2NvdW50XC9sb2dpbiIsImlhdCI6MTU2MzQyMDk3MCwiZXhwIjoxNTY0MDI1NzcwLCJuYmYiOjE1NjM0MjA5NzAsImp0aSI6IkcyTkFaNEtQTVJLUE0wNjciLCJzdWIiOjQ5MywicHJ2IjoiZmZmNjVkZGQ1NzJmZTQyOGIwMzg0MmVlNTI1NGE3OWVmYWJhNTk1MiJ9.cxIaxwdaVvG7JmGDa4Oq12CSQuzPdnGm8HfIpW_n8Ys&expand=media,user,tags,type_id&code=e877ETnlT03MmzcoDHuw0zAiBpmQn5aErZMpG4r50GPvjO_P0gLn',
            session=session,
            headers=headers,
            response_type="json"
        )
        video = await self.extract_video_info(vid=vid, response=response)
        return video

    @staticmethod
    async def extract_video_info(vid, response):
        result = dict()
        data = jmespath.search("data.data", response)
        result['title'] = jmespath.search("title", data)
        result['vid'] = vid
        result['duration'] = int(float(jmespath.search("duration", data)))
        result['width'] = 16
        result['height'] = 9  # videoitem.get('title','')
        result['play_addr'] = f"https://api.tvcbook.com/video/tvindownload/{vid}"
        result['author'] = jmespath.search("user.name", data)
        result['cover'] = jmespath.search("cover_url", data)
        result['description'] = jmespath.search("introduction", data)
        result['upload_ts'] = jmespath.search("created_at", data)
        # result['from'] = self.from_
        # result['webpage_url'] = webpage_url
        return result


if __name__ == '__main__':
    from pprint import pprint

    with Extractor() as extractor:
        res = extractor.sync_entrance(webpage_url=Extractor.TEST_CASE[-1])
        pprint(res)
