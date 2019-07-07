#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 2019/7/6
# IDE: PyCharm

import asyncio
import aiohttp
from aioVextractor import config


async def breakdown(webpage_url, chance_left=config.RETRY):
    pass

async def breakdown(playlist_url, crawlist_id, page=1, chance_left=config.RETRY):
    article_page_ids = []
    try:
        url = "https://www.xinpianchang.com/index.php"
        xinpianchang_user_ids = re.findall('/u(\d{8,12})', urlparse(playlist_url).path)
        headers = {'Origin': "https://www.xinpianchang.com",
                   'Accept-Encoding': "gzip, deflate, br",
                   'Accept-Language': "zh-CN,zh;q=0.9,en;q=0.8,ko;q=0.7",
                   'User-Agent': choice(UserAgent),
                   'Accept': "*/*",
                   'Referer': playlist_url,
                   'X-Requested-With': "XMLHttpRequest",
                   'cache-control': "no-cache"}

        async with aiohttp.ClientSession() as session:
            for xinpianchang_user_id in xinpianchang_user_ids:
                params = {"app": "user",
                          "ac": "space",
                          "ajax": "1",
                          "id": xinpianchang_user_id,
                          "d": "1",
                          "sort": "pick",
                          "cateid": "0",
                          "audit": "1",
                          "is_private": "0",
                          "page": page}
                try:
                    async with session.post(url, headers=headers, params=params) as response:
                        response_text = await response.text()
                except (ServerDisconnectedError, ServerConnectionError, ClientConnectorError, TimeoutError,
                        ServerTimeoutError, ContentTypeError, ClientConnectorCertificateError, ClientOSError):
                    if chance_left != 1:
                        return await breakdown_xinpianchang(playlist_url=playlist_url, crawlist_id=crawlist_id,
                                                            page=page, chance_left=chance_left - 1)
                    else:
                        return False
                else:
                    selector = Selector(text=response_text)
                    article_page_ids = selector.css("li[data-articleid]::attr(data-articleid)").extract()
                    has_more = selector.css("li[data-more]").extract()
                    article_pages = list(
                        map(lambda vid: f"https://www.xinpianchang.com/a{vid}?from=UserProfile", article_page_ids))
                    if has_more:
                        return article_pages + await breakdown_xinpianchang(playlist_url=playlist_url,
                                                                            crawlist_id=crawlist_id,
                                                                            page=page + 1)
                    else:
                        return article_pages

    except RecursionError:
        print(f'{crawlist_id} RecursionError occur in playlist_url: {playlist_url}\n'
              f'{crawlist_id} format_exc(): {format_exc()}')
        return article_page_ids if article_page_ids else False
    except Exception as error:
        print(f'{crawlist_id} Error occur: {error}\n'
              f'{crawlist_id} format_exc(): {format_exc()}')
        return False

if __name__ == '__main__':
    pass