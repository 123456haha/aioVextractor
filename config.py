#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 2019/6/20
# IDE: PyCharm

# import time

## retry at most 3 times when encounters failure request
RETRY = 3

URL_REGEX = r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),#]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"

## indicator to show the significance level of the fields
FIELD_SIGNI_LEVEL = {
    "must": 1,  ## necessary field that should be present after extracting
    "else": 0,  ## not necessary
    "condition_must": 2  ## conditional necessary such as `play_addr` shold be present while `downloader` is aria2c
}

## desired output fields
## a mapping between field names and FIELD_SIGNI_LEVEL
## signi_level: one of the value in FIELD_SIGNI_LEVEL's values
## default_value: the default value if the results of Extractor.entrance() does not return
## dependent_field_name: if signi_level == 2, this should be the dependent field name.
## i.e. `downloader` for `play_addr`
## dependent_field_value: if signi_level == 2, this should be the dependent field name.
## i.e. `aria2c` for `play_addr`
FIELDS = {
    'ad_link': {"signi_level": 0, "default_value": None},
    'author': {"signi_level": 0, "default_value": None},
    'author_attention': {"signi_level": 0, "default_value": None},
    'author_avatar': {"signi_level": 0, "default_value": None},
    'author_birthday': {"signi_level": 0, "default_value": None},
    'author_description': {"signi_level": 0, "default_value": None},
    'author_follwer_count': {"signi_level": 0, "default_value": None},
    'author_follwing_count': {"signi_level": 0, "default_value": None},
    'author_gender': {"signi_level": 0, "default_value": None},
    'author_id': {"signi_level": 0, "default_value": None},
    'author_sign': {"signi_level": 0, "default_value": None},
    'author_url': {"signi_level": 0, "default_value": None},
    'author_videoNum': {"signi_level": 0, "default_value": None},
    'category': {"signi_level": 0, "default_value": None},
    'cdn_url': {"signi_level": 0, "default_value": None},
    'collect_count': {"signi_level": 0, "default_value": None},
    'comment_count': {"signi_level": 0, "default_value": None},
    'cover': {"signi_level": 1},
    # 'created_at': {"signi_level": 0, "default_value": int(time.time())},
    'description': {"signi_level": 0, "default_value": None},
    'dislike_count': {"signi_level": 0, "default_value": None},
    'download_count': {"signi_level": 0, "default_value": None},
    'downloader': {"signi_level": 0, "default_value": "aria2c"},
    'duration': {"signi_level": 0, "default_value": None},
    'forward_count': {"signi_level": 0, "default_value": None},
    'from': {"signi_level": 1},
    'gender': {"signi_level": 0, "default_value": None},
    'height': {"signi_level": 0, "default_value": None},
    'language': {"signi_level": 0, "default_value": None},
    'like_count': {"signi_level": 0, "default_value": None},
    'play_addr': {"signi_level": 2, "default_value": None,
                  "dependent_field_name": "downloader",
                  "dependent_field_value": "aria2c"},
    # 'player_id',
    'rating': {"signi_level": 0, "default_value": None},
    'recommend': {"signi_level": 0, "default_value": None},
    'region': {"signi_level": 0, "default_value": None},
    'share_count': {"signi_level": 0, "default_value": None},
    'tag': {"signi_level": 0, "default_value": None},
    'title': {"signi_level": 0, "default_value": None},
    'upload_date': {"signi_level": 0, "default_value": None},
    'upload_ts': {"signi_level": 0, "default_value": None},
    'vid': {"signi_level": 1},
    'view_count': {"signi_level": 0, "default_value": None},
    'webpage_url': {"signi_level": 1},
    'width': {"signi_level": 0, "default_value": None},
}

SANIC_PORT = "5555"
LOCAL_IP_ADDR = '0.0.0.0'