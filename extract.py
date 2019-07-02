#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 2019/7/2
# IDE: PyCharm

import asyncio
import aiohttp
from . import (config,distributor)
import re
from urllib.parse import urlsplit


async def extract(webpage_url, session):
    print(f"Extracting URL: {webpage_url}")
    if isinstance(webpage_url, str):
        url_list = re.findall(config.URL_REGEX, webpage_url)
        feed = []
        for num, url_to_parse in enumerate(url_list):
            print(f"NUMBER {num} URL: {url_to_parse}")
            ParseResult = urlsplit(url_to_parse)
            netloc = ParseResult.netloc
            path = ParseResult.path
            if netloc in config.ALLOW_NETLOC:
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
            return gather_results
    else:
        print(f'The URL: {webpage_url} \n'
              f'is NOT a string')
        return None


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


    # asyncio.run(test())
