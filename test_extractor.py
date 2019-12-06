#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 2019/9/9
# IDE: PyCharm
"""
RUN ME BEFORE GOING SERIOUS!

python -m pytest test_extractor.py --verbose

"""
import sys, os

curPath = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.dirname(curPath))

from aioVextractor.extractor import gen_extractor_classes
from aioVextractor.breaker import gen_breaker_classes
import aiohttp
from aioVextractor import hybrid_worker
import pytest

class Test_Extractor:
    @pytest.mark.parametrize(
        'case', [
            sample
            for instance in gen_extractor_classes() + gen_breaker_classes()
            for sample in instance.TEST_CASE
        ]
    )
    @pytest.mark.asyncio
    async def test_extractor(self, case):
        async with aiohttp.ClientSession() as session:
            result = await hybrid_worker(webpage_url=case, session=session)
            test_benchmark = isinstance(result, (list, tuple))
            assert test_benchmark
