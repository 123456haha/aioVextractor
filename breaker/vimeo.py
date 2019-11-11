#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 2019/7/6
# IDE: PyCharm

from urllib.parse import urlsplit
import jmespath
import re
from aioVextractor.utils import RequestRetry
from aioVextractor.breaker import (
    BaseBreaker,
    BreakerValidater
)


class Breaker(BaseBreaker):
    target_website = [
        "https://vimeo\.com/[\w]*",
    ]

    downloader = 'ytd'

    TEST_CASE = [
        "https://vimeo.com/alitasmitmedia",
    ]

    def __init__(self, *args, **kwargs):
        BaseBreaker.__init__(self, *args, **kwargs)
        self.from_ = "vimeo"

    @BreakerValidater
    @RequestRetry
    async def breakdown(self, webpage_url, session, **kwargs):
        page = int(kwargs.pop("page", 1))
        ParseResult = urlsplit(webpage_url)
        path = ParseResult.path
        if re.match('/channels/.*', path):  ## https://vimeo.com/channels/ceiga
            ## do not supported
            return []
        elif re.match('/\d{6,11}', path):  ## https://vimeo.com/281493330  ## this is single
            return []
        elif re.match('[/.*]', path):  ## https://vimeo.com/alitasmitmedia
            headers = {
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'User-Agent': self.random_ua(),
                'Accept': '*/*',
                'X-Requested-With': 'XMLHttpRequest',
            }

            clips = await self.request(
                url=webpage_url,
                session=session,
                headers=headers,
                params={'action': 'get_profile_clips',
                        'page': page},
                response_type="json"
            )
            results = jmespath.search('clips[].{'
                                      '"title": title, '
                                      '"cover": thumbnail.src, '
                                      # '"cover": thumbnail.src_8x, '
                                      '"duration": duration.raw, '
                                      '"vid": clip_id, '
                                      '"webpage_url": url, '
                                      '"recommend": is_staffpick, '
                                      '"comment_count": quickstats.total_comments.raw, '
                                      '"like_count": quickstats.total_likes.raw, '
                                      '"view_count": quickstats.total_plays.raw, '
                                      '"author": user.name, '
                                      '"author_id": user.id, '
                                      '"author_url": user.url, '
                                      '"author_avatar": user.thumbnail.src_8x}', clips)
            for ele in results:
                ele['author_url'] = "https://vimeo.com" + ele['author_url']
                ele['webpage_url'] = "https://vimeo.com" + ele['webpage_url']
                ele['playlist_url'] = webpage_url
                ele['from'] = self.from_

            has_next = jmespath.search('clips_meta.has_next', clips)
            return results, has_next, {}


if __name__ == '__main__':
    from pprint import pprint

    with Breaker() as breaker:
        res = breaker.sync_breakdown(
            webpage_url=Breaker.TEST_CASE[0],
            # page=2,
        )
        pprint(res)
