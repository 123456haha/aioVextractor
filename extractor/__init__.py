#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 2019/6/20
# IDE: PyCharm

from urllib.parse import urlsplit
import aiohttp
import asyncio

# __all__ = [
#     'adquan',
#     'bilibili',
#     'carben',
#     'common',
#     'digitaling',
#     'douyin',
#     'eyepetizer',
#     'hellorf',
#     'instagram',
#     'iwebad',
#     'lanfan',
#     'naver',
#     'pinterest',
#     'renren',
#     'socialbeta',
#     'tencent',
#     'tvcf',
#     'vimeo',
#     'vmovier',
#     'xinpianchang',
#     'youku',
#     'youtube',
#     'FIELD_HAVING',
#     'TEST_CASE',
#     'ALLOW_NETLOC',
# ]

from extractor import adquan
from extractor import bilibili
from extractor import carben
from extractor import common
from extractor import digitaling
from extractor import douyin
from extractor import eyepetizer
from extractor import hellorf
from extractor import instagram
from extractor import pinterest
from extractor import iwebad
from extractor import lanfan
from extractor import naver
from extractor import youku
from extractor import youtube
from extractor import renren
from extractor import socialbeta
from extractor import tencent
from extractor import tvcf
from extractor import vimeo
from extractor import vmovier
from extractor import xinpianchang
from extractor import weixin

TEST_CASE = list(set(
        adquan.TEST_CASE
        + bilibili.TEST_CASE
        + carben.TEST_CASE
        + common.TEST_CASE
        + digitaling.TEST_CASE
        + douyin.TEST_CASE
        + eyepetizer.TEST_CASE
        + hellorf.TEST_CASE
        + instagram.TEST_CASE
        + iwebad.TEST_CASE
        + lanfan.TEST_CASE
        + naver.TEST_CASE
        + pinterest.TEST_CASE
        + renren.TEST_CASE
        + socialbeta.TEST_CASE
        + tencent.TEST_CASE
        + tvcf.TEST_CASE
        + vimeo.TEST_CASE
        + vmovier.TEST_CASE
        + weixin.TEST_CASE
        + xinpianchang.TEST_CASE
        + youku.TEST_CASE
        + youtube.TEST_CASE
))

ALLOW_NETLOC = {urlsplit(url).netloc for url in TEST_CASE}

FIELD_HAVING = ["ad_link",
                "author",
                "author_attention",
                "author_avatar",
                "author_birthday",
                "author_description",
                "author_follwer_count",
                "author_follwing_count",
                "author_gender",
                "author_id",
                "author_sign",
                "author_url",
                "author_videoNum",
                "category",
                "cdn_url",
                "collect_count",
                "comment_count",
                "cover",
                "created_at",
                "description",
                "dislike_count",
                "download_count",
                "duration",
                "forward_count",
                "from",
                "gender",
                "height",
                "language",
                "like_count",
                "play_addr",
                "player_id",
                "rating",
                "recommend",
                "region",
                "share_count",
                "tag",
                "title",
                "upload_date",
                "upload_ts",
                "vid",
                "view_count",
                "webpage_url",
                "width",
                ]
# FIELDS = ['品牌',
#           '行业',
#           '类型',
#           '语言',
#           '标签',
#           '投放地区',
#           '视频详情（视频介绍、简介）',
#           '视频相关的seo信息']
#
# FIELDS_CHECKED = ["视频封面",
#                   "视频标题",
#                   "视频信息",  ## 发布人填写的对视频的介绍和说明信息
#                   "品牌",
#                   "评分",
#                   "行业",
#                   "类型",
#                   "语言",
#                   "标签",
#                   "投放地区",
#                   # "视频相关的seo信息",
#                   "上传时间",
#                   "发布人昵称",
#                   "发布人头像"]

# FIELDS_CONVERTED = ['author',
#                     'author_avatar',
#                     'brand',
#                     'category',
#                     'cover',
#                     'description',
#                     'industry',
#                     'language',
#                     'rating',
#                     'region',
#                     'tag',
#                     'title',
#                     'upload_ts',
#                     'webpage_url',
#                     'vid',
#                     'created_time',
#                     'updated_time',
#                     'video_path',
#                     'cover_path',
#                     'avatar_path'
#                     ]

# FIELD_HAVING = ['author',
#                 'author_attention',
#                 'author_avatar',
#                 'author_birthday',
#                 'author_description',
#                 'author_follwer_count',
#                 'author_follwing_count',
#                 'author_gender',
#                 'author_id',
#                 'author_sign',
#                 'author_url',
#                 'author_videoNum',
#                 'category',
#                 'cdn_url',
#                 'comment_count',
#                 'cover',
#                 'description',
#                 'dislike_count',
#                 'download_count',
#                 'duration',
#                 'forward_count',
#                 'from',
#                 'gender',
#                 'height',
#                 'language',
#                 'like_count',
#                 'play_addr',
#                 'rating',
#                 'region',
#                 'share_count',
#                 'tag',
#                 'tags',
#                 'title',
#                 'upload_date',
#                 'upload_ts',
#                 'vid',
#                 'view_count',
#                 'webpage_url',
#                 'width']
