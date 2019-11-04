#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 2019/6/20
# IDE: PyCharm

import jmespath
import re
import traceback

from aioVextractor.extractor.base_extractor import (
    BaseExtractor,
    validate,
    RequestRetry
)


class Extractor(BaseExtractor):
    target_website = [
        "http[s]?://www\.eyepetizer\.net/detail\.html\?vid=\d{3,8}",
        "www\.eyepetizer\.net/detail\.html\?vid=\d{3,8}",
    ]

    TEST_CASE = [
        "www.eyepetizer.net/detail.html?vid=119611&utm_campaign=routine&utm_medium=share&utm_source=others&uid=0&resourceType=video&udid=1bb9f2f14545490c9168f7b99d89136e8ff14724&vc=443&vn=4.9.1&size=1080X1920&deviceModel=vivo%20X9&first_channel=eyepetizer_vivo_market&last_channel=eyepetizer_vivo_market&system_version_code=25",
    ]

    def __init__(self, *args, **kwargs):
        BaseExtractor.__init__(self, *args, **kwargs)
        self.from_ = "eyepetizer"

    @validate
    @RequestRetry
    async def entrance(self, webpage_url, session, *args, **kwargs):
        try:
            vid = re.compile('vid=([\d]*)').search(webpage_url)[1]
        except (IndexError, TypeError):
            traceback.print_exc()
            return False
        else:
            download_headers = {'Accept': '*/*',
                                'Referer': webpage_url,
                                'Origin': 'https://www.eyepetizer.net',
                                'User-Agent': self.random_ua()}

            params = {'f': 'web'}
            response_url = f'https://baobab.kaiyanapp.com/api/v1/video/{vid}'
            response_json = await self.request(
                url=response_url,
                session=session,
                headers=download_headers,
                params=params,
                response_type="json"
            )
            return {**self.extract(response_json), **{"webpage_url": webpage_url}}

    def extract(self, response_json):
        result = dict()
        result['from'] = self.from_
        result['title'] = jmespath.search('title', response_json)
        result['author'] = jmespath.search('author.name', response_json)
        result['author_description'] = jmespath.search('author.description', response_json)
        result['author_avatar'] = jmespath.search('author.icon', response_json)
        result['author_videoNum'] = jmespath.search('author.videoNum', response_json)
        result['category'] = jmespath.search('category', response_json)
        video_create_time = jmespath.search('date', response_json)
        result['upload_ts'] = int(video_create_time / 1000) if video_create_time else None
        result['description'] = jmespath.search('description', response_json)
        result['duration'] = jmespath.search('duration', response_json)
        result['vid'] = jmespath.search('id', response_json)
        result['play_addr'] = jmespath.search('max_by(playInfo, &height).url', response_json)
        result['tag'] = jmespath.search('tags[*].name', response_json)
        result['cover'] = jmespath.search('coverForFeed', response_json)
        return result

if __name__ == '__main__':
    from pprint import pprint
    with Extractor() as extractor:
        res = extractor.sync_entrance(webpage_url=Extractor.TEST_CASE[0])
        pprint(res)

