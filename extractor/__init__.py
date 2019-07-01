#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 2019/6/20
# IDE: PyCharm


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
                    'created_time',
                    'updated_time',
                    'video_path',
                    'cover_path',
                    'avatar_path'
                    ]


if __name__ == '__main__':
    pass
