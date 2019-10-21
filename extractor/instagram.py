#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 10/07/19
# IDE: PyCharm

from aioVextractor.extractor.base_extractor import (BaseExtractor, validate, RequestRetry)
import jmespath
import platform
if platform.system() in {"Linux", "Darwin"}:
    import ujson as json
else:
    import json

TEST_CASE = [
    "https://www.instagram.com/p/B1G1rBiAa_8/",
]


class Extractor(BaseExtractor):
    target_website = [
        "www\.instagram\.com/p/[\w-]*",
        "www\.instagram\.com/tv/[\w-]*",
    ]

    def __init__(self, *args, **kwargs):
        BaseExtractor.__init__(self, *args, **kwargs)
        self.from_ = "instagram"

    @validate
    @RequestRetry
    async def entrance(self, webpage_url, session):
        retults = await self.extract(webpage_url, session)
        return retults

    @RequestRetry
    async def extract(self, webpage_url, session):
        if webpage_url.endswith("/"):
            tagurl = webpage_url + "?__a=1"
        else:
            tagurl = webpage_url.split("#")[0] + "/?__a=1"
        item = dict()
        async with session.get(tagurl, verify_ssl=False) as resp:
            html = await resp.text(encoding='utf-8', errors='ignore')
            jsondata = json.loads(html)
            shortcode_media = jmespath.search("graphql.shortcode_media", jsondata)
            if not shortcode_media:
                return None
            item['play_addr'] = jmespath.search("video_url", shortcode_media)
            item['description'] = jmespath.search("edge_media_to_caption.edges[0].node.text", shortcode_media)
            item['view_count'] = jmespath.search("video_view_count", shortcode_media)
            item['duration'] = int(shortcode_media.get("video_duration"))
            item['upload_ts'] = jmespath.search("taken_at_timestamp", shortcode_media)
            item['title'] = jmespath.search("title", shortcode_media)
            item['vid'] = jmespath.search("shortcode", shortcode_media)
            item['from'] = self.from_
            item['like_count'] = jmespath.search("edge_media_preview_like.count", shortcode_media)
            item['comment_count'] = jmespath.search("edge_media_to_parent_comment.count", shortcode_media)
            item['webpage_url'] = webpage_url
            item['cover'] = jmespath.search("display_url", shortcode_media)
            item['width'] = jmespath.search("dimensions.width", shortcode_media)
            item['height'] = jmespath.search("dimensions.height", shortcode_media)
            item['author'] = jmespath.search("owner.username", shortcode_media)
            item['author_id'] = jmespath.search("owner.id", shortcode_media)
            item['author_avatar'] = jmespath.search("owner.profile_pic_url", shortcode_media)
            item['author_url'] = "https://www.instagram.com/" + item['author'] if item['author'] else None
            return item

if __name__ == '__main__':
    from pprint import pprint
    with Extractor() as extractor:
        res = extractor.sync_entrance(webpage_url="https://creative.adquan.com/show/286808")
        pprint(res)


