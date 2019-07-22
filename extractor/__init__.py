#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 2019/6/20
# IDE: PyCharm
from . import *

__all__ = [
    'bilibili',
    'common',
    'douyin',
    'eyepetizer',
    'tencent',
    'tvcf',
    'vimeo',
    'xinpianchang',
    'youku',
    'youtube',
    'FIELD_HAVING',
    "tvcbook",
]

FIELDS = ['品牌',
          '行业',
          '类型',
          '语言',
          '标签',
          '投放地区',
          '视频详情（视频介绍、简介）',
          '视频相关的seo信息']

FIELDS_CHECKED = ["视频封面",
                  "视频标题",
                  "视频信息",  ## 发布人填写的对视频的介绍和说明信息
                  "品牌",
                  "评分",
                  "行业",
                  "类型",
                  "语言",
                  "标签",
                  "投放地区",
                  # "视频相关的seo信息",
                  "上传时间",
                  "发布人昵称",
                  "发布人头像"]

FIELDS_CONVERTED = ['author',
                    'author_avatar',
                    'brand',
                    'category',
                    'cover',
                    'description',
                    'industry',
                    'language',
                    'rating',
                    'region',
                    'tag',
                    'title',
                    'upload_ts',
                    'webpage_url',
                    'vid',
                    'created_time',
                    'updated_time',
                    'video_path',
                    'cover_path',
                    'avatar_path'
                    ]

FIELD_HAVING = ['author',
                'author_attention',
                'author_avatar',
                'author_birthday',
                'author_description',
                'author_follwer_count',
                'author_follwing_count',
                'author_gender',
                'author_id',
                'author_sign',
                'author_url',
                'author_videoNum',
                'category',
                'cdn_url',
                'comment_count',
                'cover',
                'description',
                'dislike_count',
                'download_count',
                'duration',
                'forward_count',
                'from',
                'gender',
                'height',
                'language',
                'like_count',
                'play_addr',
                'rating',
                'region',
                'share_count',
                'tag',
                'tags',
                'title',
                'upload_date',
                'upload_ts',
                'vid',
                'view_count',
                'webpage_url',
                'width']

if __name__ == '__main__':
    pass
