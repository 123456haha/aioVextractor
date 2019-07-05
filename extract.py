#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 2019/7/2
# IDE: PyCharm

## add current path to system path temporary
import sys, os
curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)

import asyncio
import aiohttp
import config
from aioVextractor import config
import distributor
import re
import traceback
from urllib.parse import (urlsplit, urlparse)


async def extract(webpage_url, session):
    try:
        print(f"Extracting URL: {webpage_url}")
        if isinstance(webpage_url, str):  ## determine weather if the webpage_url is a string
            url_list = re.findall(config.URL_REGEX, webpage_url)  ## find all url in the string
            feed = []  ## ur to be parsed
            for num, url_to_parse in enumerate(url_list):
                print(f"NUMBER {num} URL: {url_to_parse}")
                ## construct necessary parms for identifying the url
                ParseResult = urlsplit(url_to_parse)
                netloc = ParseResult.netloc
                path = ParseResult.path
                ## identifying the url
                if netloc in config.ALLOW_NETLOC:  ## determine weather if the netloc of the url is in ALLOW_NETLOC
                    feed.append(distributor.distribute(webpage_url=url_to_parse,
                                                       netloc=netloc,
                                                       path=path,
                                                       session=session))
                else:
                    print(f"The netloc({netloc}) \n"
                          f"of {url_to_parse} \n"
                          f"is not in ALLOW_NETLOC:{config.ALLOW_NETLOC}")
                    continue

            else:
                gather_results = await asyncio.gather(*feed)
                return None if gather_results is [] else gather_results
        else:
            print(f'The URL: {webpage_url} \n'
                  f'is NOT a string')
            return None
    except:
        traceback.print_exc()
        return False

async def janitor


def is_playlist(webpage_url):
    print(f"Identifying URL: {webpage_url}")
    if isinstance(webpage_url, str):  ## determine weather if the webpage_url is a string
        url_list = re.findall(config.URL_REGEX, webpage_url)  ## find all url in the string
        for num, url_to_parse in enumerate(url_list):
            print(f"NUMBER {num} URL: {url_to_parse}")
            ## construct necessary parms for identifying the url
            ParseResult = urlsplit(url_to_parse)
            netloc = ParseResult.netloc
            path = ParseResult.path
            ## identifying the url
            if netloc in config.ALLOW_NETLOC:  ## determine weather if the netloc of the url is in ALLOW_NETLOC
                pass
            else:
                print(f"The netloc({netloc}) \n"
                      f"of {url_to_parse} \n"
                      f"is not in ALLOW_NETLOC:{config.ALLOW_NETLOC}")
                continue
    else:
        print(f'The URL: {webpage_url} \n'
              f'is NOT a string')
        return None

async def breakdown_playlist(webpage_url, cursor=0, offset=10):
    """return title and cover of videos under webpage_url limit to certain range (cursor, offset)"""
    if craw_id in {config.craw_id_category['YOUTUBE']['list'],
                   config.craw_id_category['VIMEO']['list']}:
        args = {
            "nocheckcertificate": True,
            "ignoreerrors": True,
            "quiet": True,
            "nopart": True,
            "download_archive": "record.txt",
            "no_warnings": True,
            "youtube_include_dash_manifest": False,
            'simulate': True
        }
        urls_ = []
        try:
            with youtube_dl.YoutubeDL(args) as ydl:
                try:
                    for single in jmespath.search('entries[].webpage_url', ydl.extract_info(playlist_url)):
                        urls_.append(single)
                except TypeError:
                    ## the playlist_url is a single where come from FailureQueue during formattinf process
                    return [playlist_url]
            return urls_
        except TypeError as error:
            ## possible outcome: TypeError: 'NoneType' object is not iterable
            ## which is cause by mysterious input :)
            ## such as https://www.youtube.com/watch?v=FHm2-qWRW88；https://www.youtube.com/watch?v=Zvpvs5M433Q；https://www.youtube.com/watch?v=Rt5QTEprx5E
            ## which is not categorized as a playlist
            print(f'{crawlist_id} Error occur: {error}\n'
                  f'{crawlist_id} format_exc(): {format_exc()}')
            return False
        except Exception as error:
            print(f'{crawlist_id} Error occur: {error}\n'
                  f'{crawlist_id} format_exc(): {format_exc()}')
            return False

    elif craw_id == config.craw_id_category['XINPIANCHANG']['list']:  ## breakdown xinpianchang playlist
        article_pages = await breakdown_xinpianchang(playlist_url=playlist_url, crawlist_id=crawlist_id)
        return article_pages
    elif craw_id == config.craw_id_category['ADSOFTHEWORLD']['list']:  ## breakdown adsoftheworld playlist
        article_pages = await breakdown_adsoftheworld(playlist_url=playlist_url, crawlist_id=crawlist_id)
        return article_pages



async def breakdown_xinpianchang(playlist_url, crawlist_id, page=1, chance_left=config.RETYR):
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


async def breakdown_adsoftheworld(playlist_url, crawlist_id, page=0, Referer=None, chance_left=config.RETYR):
    article_page_ids = []
    try:
        url = playlist_url
        if page == 0:
            params = None
        else:
            params = {"page": page}

        headers = {
            'Upgrade-Insecure-Requests': "1",
            'User-Agent': choice(UserAgent),
            'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
            'Accept-Encoding': "gzip, deflate, br",
            'Accept-Language': "zh-CN,zh;q=0.9,en;q=0.8,ko;q=0.7",
            'cache-control': "no-cache"
        }

        if Referer:
            headers['Referer'] = Referer
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, headers=headers, params=params) as response:
                    response_text = await response.text()
            except (ServerDisconnectedError, ServerConnectionError, ClientConnectorError, TimeoutError,
                    ServerTimeoutError, ContentTypeError, ClientConnectorCertificateError, ClientOSError):
                if chance_left != 1:
                    return await breakdown_adsoftheworld(playlist_url=playlist_url, crawlist_id=crawlist_id, page=page,
                                                         Referer=Referer, chance_left=chance_left - 1)
                else:
                    return False
            else:
                selector = Selector(text=response_text)
                article_page_ids = selector.css('article[about]::attr(about)').re(
                    '/media/(?!print).*')  ## filter print ads
                has_more = selector.css('a[title*="Go to next page"]::attr(href)').extract_first()
                article_pages = list(
                    map(lambda trailing_path: f"https://www.adsoftheworld.com{trailing_path}", article_page_ids))
                if has_more:
                    next_page = f"https://www.adsoftheworld.com{has_more}"
                    return article_pages + await breakdown_adsoftheworld(playlist_url=next_page,
                                                                         crawlist_id=crawlist_id,
                                                                         page=page + 1,
                                                                         Referer=playlist_url)
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
    from pprint import pprint

    TEST_CASE = [
        # 'https://www.bilibili.com/video/av5546345?spm_id_from=333.334.b_62696c695f646f756761.4',
        # '#在抖音，记录美好生活#球球老婆怀孕之后就爱睡这个洗脸巢睡姿也太可爱了8#猫http://v.douyin.com/hd9sb3/复制此链接，打开【抖音短视频】，直接观看视频！',
        # 'http://v.douyin.com/hd9sb3/',
        # 'https://www.eyepetizer.net/detail.html?vid=119611&utm_campaign=routine&utm_medium=share&utm_source=others&uid=0&resourceType=video&udid=1bb9f2f14545490c9168f7b99d89136e8ff14724&vc=443&vn=4.9.1&size=1080X1920&deviceModel=vivo%20X9&first_channel=eyepetizer_vivo_market&last_channel=eyepetizer_vivo_market&system_version_code=25',
        # 'https://v.qq.com/x/page/s0886ag14xn.html',
        # 'https://v.qq.com/x/cover/bzfkv5se8qaqel2.html',
        # 'http://www.tvcf.co.kr/YCf/V.asp?Code=A000363280',
        # 'https://play.tvcf.co.kr/750556',
        # 'https://vimeo.com/281493330',
        # 'https://www.xinpianchang.com/a10475334?from=ArticleList',
        # 'https://v.youku.com/v_show/id_XMzg5Mjc5NDExMg==.html?spm=a2h0j.11185381.bpmodule-playpage-segments.5~5~A&&s=1f1b995a017c11df97c0',
        # 'https://www.youtube.com/watch?v=tofSaLB9kwE',
        'https://www.bilibili.com/video/av5546345?spm_id_from=333.334.b_62696c695f646f756761.4, http://v.douyin.com/hd9sb3/'
    ]


    async def test():
        async with aiohttp.ClientSession() as session_:
            for iiii in TEST_CASE:
                result = await extract(webpage_url=iiii, session=session_)
                print(result)
                print('\n')


    asyncio.run(test())
