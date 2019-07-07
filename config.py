#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 2019/6/20
# IDE: PyCharm

from urllib.parse import urlsplit

## retry at most 3 times when encounters failure request
RETRY = 3

URL_REGEX = r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"

TEST_CASE = ['https://www.bilibili.com/video/av5546345?spm_id_from=333.334.b_62696c695f646f756761.4',
             '#在抖音，记录美好生活#球球老婆怀孕之后就爱睡这个洗脸巢睡姿也太可爱了8#猫http://v.douyin.com/hd9sb3/复制此链接，打开【抖音短视频】，直接观看视频！',
             'http://v.douyin.com/hd9sb3/',
             'https://www.eyepetizer.net/detail.html?vid=119611&utm_campaign=routine&utm_medium=share&utm_source=others&uid=0&resourceType=video&udid=1bb9f2f14545490c9168f7b99d89136e8ff14724&vc=443&vn=4.9.1&size=1080X1920&deviceModel=vivo%20X9&first_channel=eyepetizer_vivo_market&last_channel=eyepetizer_vivo_market&system_version_code=25',
             'https://v.qq.com/x/page/s0886ag14xn.html',
             'https://v.qq.com/x/cover/bzfkv5se8qaqel2.html',
             'http://www.tvcf.co.kr/YCf/V.asp?Code=A000363280',
             'https://play.tvcf.co.kr/750556',
             'https://vimeo.com/281493330',
             'https://www.xinpianchang.com/a10475334?from=ArticleList',
             'https://v.youku.com/v_show/id_XMzg5Mjc5NDExMg==.html?spm=a2h0j.11185381.bpmodule-playpage-segments.5~5~A&&s=1f1b995a017c11df97c0',
             'https://www.youtube.com/watch?v=tofSaLB9kwE']

ALLOW_NETLOC = {urlsplit(url).netloc for url in TEST_CASE}

PLAYLIST_TEST_CASE = ['https://vimeo.com/alitasmitmedia',
                      'https://vimeo.com/channels/ceiga',
                      'https://www.youtube.com/playlist?list=PLohYzz4btpaSt2T0rcfmF8wfQzuW_6JTv',
                      'https://www.youtube.com/channel/UC36FGmBEGfmOV2T5QVNI9ew',
                      'https://www.xinpianchang.com/u10539256?from=userList',
                      ]
## how many videos retrieve from a playlist by default
DEFAULT_CURSOR = 0
DEFAULT_OFFSET = 10


# BreakdownPlaylistArgs = {
#     "nocheckcertificate": True,
#     "ignoreerrors": True,
#     "quiet": True,
#     "nopart": True,
#     # "download_archive": "record.txt",
#     "no_warnings": True,
#     "youtube_include_dash_manifest": False,
#     'simulate': True
# }

# ALLOW_NETLOC_PLAYLIST = {urlsplit(url).netloc for url in PLAYLIST_TEST_CASE}
