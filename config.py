#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 2019/6/20
# IDE: PyCharm


## retry at most 3 times when encounters failure request
RETRY = 3

URL_REGEX = r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"


# PLAYLIST_TEST_CASE = ['https://vimeo.com/alitasmitmedia',
#                       'https://vimeo.com/channels/ceiga',
#                       'https://www.youtube.com/playlist?list=PLohYzz4btpaSt2T0rcfmF8wfQzuW_6JTv',
#                       'https://www.youtube.com/channel/UC36FGmBEGfmOV2T5QVNI9ew',
#                       'https://www.xinpianchang.com/u10539256?from=userList',
#                       ]
## how many videos retrieve from a playlist by default
# DEFAULT_CURSOR = 0
# DEFAULT_OFFSET = 10
