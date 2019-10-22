#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 2019/7/2
# IDE: PyCharm

## add current path to system path temporary
import sys, os

curPath = os.path.abspath(os.path.dirname(__file__))
sys.path.append(curPath)

from aioVextractor.distributor import distribute
from aioVextractor.extract import extract
from aioVextractor.extractor.base_extractor import (
    BaseExtractor,
    validate,
    RequestRetry
)
# from aioVextractor import (
#     breaker,
#     extractor,
#     utils,
#     config,
#     distributor,
#     breakdown,
# )
#
# from extract import (
#     extract,
#     is_playlist
# )
#
# from breakdown import breakdown
# from aioVextractor.distributor import distribute
# from aioVextractor.extractor import ALLOW_NETLOC
# import aiohttp
# import asyncio