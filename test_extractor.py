#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 2019/9/9
# IDE: PyCharm
"""
RUN ME BEFORE GOING SERIOUS!
"""
import sys, os

curPath = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.dirname(curPath))

from aioVextractor.extractor import gen_extractor_classes
from aioVextractor.breaker import gen_breaker_classes
import aiohttp
from aioVextractor import hybrid_worker

# async def test(asking=True):
#     async with aiohttp.ClientSession() as session:
#         fail_url = set()
#         for instance in gen_extractor_classes() + gen_breaker_classes():
#             try:
#                 TEST_CASE = instance.TEST_CASE
#             except:
#                 continue
#
#             for sample in TEST_CASE:
#                 if asking:
#                     procceed = input(f"proccee webpage_url: {sample}?\n"
#                                      f"press Enter/n/no to ignore and y/yes to procceed\n"
#                                      f"enter `pass` to the next extractor TEST_CASE: ")
#                 else:
#                     procceed = "yes"
#                 if procceed in {"y", 'yes'}:
#                     result = await hybrid_worker(webpage_url=sample, session=session)
#                     pprint(result)
#                     if not result:
#                         fail_url.add(sample)
#                     print("**************************************************"
#                           "*************************************************\n")
#                 elif procceed == "pass":
#                     break
#         else:
#             print(f"fail_url: \n"
#                   f"{fail_url}")
#
#
# asyncio.run(test(asking=False))

"""
python -m pytest test_extractor.py --verbose 
"""
import pytest


# @pytest.mark.asyncio
# async def test_extractor():
#     async with aiohttp.ClientSession() as session:
#         for instance in gen_extractor_classes() + gen_breaker_classes():
#             for sample in instance.TEST_CASE:
#                 print(sample)
#                 result = await hybrid_worker(webpage_url=sample, session=session)
#                 print(result)
#                 test_benchmark = isinstance(result, list)
#                 assert test_benchmark


# def validate_data(file):
#     if file == 1:
#         return True
#     if file == 2:
#         return False
#     if file == 3:
#         return True


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
