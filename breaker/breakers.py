#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 2019/10/20
# IDE: PyCharm
"""
HOW TO GENERATE THIS FILE:
import os
breaker_path = "/path/to/breker"
res = [ele for ele in os.listdir(breaker_path) if ele not in {'__init__.py', 'extractors.py', '__pycache__', 'breakers.py'}]
for ele in res:
    print(f"from aioVextractor.breker.{ele.replace('.py', '')} import Breaker as {ele.replace('.py', '')}BK")

"""
from aioVextractor.breaker.base_breaker import BaseBreaker as baseBK
from aioVextractor.breaker.bilibili import Breaker as bilibiliBK
# from aioVextractor.breaker.douyin import Breaker as douyinBK
from aioVextractor.breaker.eyepetizer import Breaker as eyepetizerBK
from aioVextractor.breaker.instagram import Breaker as instagramBK
from aioVextractor.breaker.pinterest import Breaker as pinterestBK
from aioVextractor.breaker.vimeo import Breaker as vimeoBK
from aioVextractor.breaker.weibo import Breaker as weiboBK
from aioVextractor.breaker.xinpianchang import Breaker as xinpianchangBK
from aioVextractor.breaker.youtube import Breaker as youtubeBK