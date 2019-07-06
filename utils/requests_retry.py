#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 2019/7/6
# IDE: PyCharm

from aioVextractor import config
import traceback
from aioVextractor.utils.exception import exception

def RequestRetry(func):
    async def _wrapper(*args, **kwargs):
        for _ in range(config.RETRY):
            try:
                return await func(*args, **kwargs)
            except exception:
                continue
            except:
                traceback.print_exc()
                return False
        return False
    return _wrapper

