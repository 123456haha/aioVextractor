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
from aioVextractor import config
from aioVextractor import distributor
import re
import traceback
from urllib.parse import urlsplit


async def extract(webpage_url, session):
    """
    extract single webpage_url
    webpage_url can be single url join() by string than can separate any consecutive urls
    """
    print(f"Extracting URL: {webpage_url}")
    feed = [distributor.distribute(webpage_url=url_to_parse,
                                   netloc=netloc,
                                   path=path,
                                   session=session) async for url_to_parse, netloc, path in
            janitor(webpage_url=webpage_url)]

    gather_results = await asyncio.gather(*feed)
    return None if gather_results is [] else gather_results


async def janitor(webpage_url):
    """clean the webpage_url and yield the url from webpage_url"""
    try:
        if isinstance(webpage_url, str):  ## determine weather if the webpage_url is a string
            url_list = re.findall(config.URL_REGEX, webpage_url)  ## find all url in the string
            # feed = []  ## ur to be parsed
            for num, url_to_parse in enumerate(url_list):
                print(f"NUMBER {num} URL: {url_to_parse}"
                      # f"IN webpage_url {webpage_url}"
                      )
                ## construct necessary parms for identifying the url
                ParseResult = urlsplit(url_to_parse)
                netloc = ParseResult.netloc
                path = ParseResult.path
                ## identifying the url
                if netloc in config.ALLOW_NETLOC:  ## determine weather if the netloc of the url is in ALLOW_NETLOC
                    print(f"NUMBER {num} URL: IS ALLOWED")
                    yield url_to_parse, netloc, path
                    # feed.append(execution(**kwargs))
                else:
                    print(f"The netloc({netloc}) \n"
                          f"of {url_to_parse} \n"
                          f"is not in ALLOW_NETLOC:{config.ALLOW_NETLOC}")
                    continue
        else:
            print(f'The URL: {webpage_url} \n'
                  f'is NOT a string')
    except GeneratorExit:
        pass
    except:
        traceback.print_exc()


async def is_playlist(webpage_url):
    """
    determine weather if webpage_url is a playlist
    and yield url,netloc,path when it is a playlist
    :return Boolean: True or False
    """
    print(f"Identifying URL: {webpage_url}")
    async for url_to_parse, netloc, path in janitor(webpage_url):
        if netloc == 'vimeo.com':
            if re.match('/channels/.*', path):  ## do not supported
                # continue
                return None
                # print(f'IS playlist: {url_to_parse}')
                # yield url_to_parse, netloc, path
            elif re.match('/\d{6,11}', path):
                # continue
                return None
            elif re.match('[/.*]', path):
                print(f'IS playlist: {url_to_parse}')
                return url_to_parse, netloc, path
            else:
                print(f"url_to_parse: {url_to_parse}\n"
                      f"is NOT valid playlist url\n")
                # continue
                return None
        elif netloc == 'www.youtube.com':
            if re.match('/playlist', path):
                print(f'IS playlist: {url_to_parse}')
                return url_to_parse, netloc, path
            elif re.match('/channel/', path):
                print(f'IS playlist: {url_to_parse}')
                return url_to_parse, netloc, path
            elif re.match('/watch', path):
                # continue
                return None
            else:
                print(f"url_to_parse: {url_to_parse}\n"
                      f"is NOT valid playlist url\n")
                # continue
                return None
        elif netloc == 'www.xinpianchang.com':
            if re.match('/u\d*', path):
                print(f'IS playlist: {url_to_parse}')
                return url_to_parse, netloc, path
            elif re.match('/a\d*', path):
                # continue
                return None
            else:
                print(f"url_to_parse: {url_to_parse}\n"
                      f"is NOT valid playlist url\n")
                # continue
                return None

        else:
            pass


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
        # 'https://www.bilibili.com/video/av5546345?spm_id_from=333.334.b_62696c695f646f756761.4, http://v.douyin.com/hd9sb3/',
        'https://www.youtube.com//watch?v=QY8Ni8NLVqc&list=PLkLimRXN6NKydb8z9wcGdwqJEyMBYwE0H&index=36&t=0s',
    ]
    #
    #
    async def test():
        async with aiohttp.ClientSession() as session_:
            for iiii in TEST_CASE:
                result = await extract(webpage_url=iiii, session=session_)
                print(result)
                print('\n')
    PLAYLIST_TEST_CASE = ['https://vimeo.com/alitasmitmedia',
                          'https://vimeo.com/channels/ceiga',
                          'https://www.youtube.com/playlist?list=PLohYzz4btpaSt2T0rcfmF8wfQzuW_6JTv',
                          'https://www.youtube.com/channel/UC36FGmBEGfmOV2T5QVNI9ew',
                          'https://www.xinpianchang.com/u10539256?from=userList',
                          ]


    # async def test():
    #     async with aiohttp.ClientSession() as session_:
    #         for iiii in PLAYLIST_TEST_CASE:
    #             result = await is_playlist(webpage_url=iiii)
    #             # async for result in is_playlist(webpage_url=iiii):
    #             print(f"result:{result}")
    #             print('\n')

    loop = asyncio.get_event_loop()
    loop.run_until_complete(test())
