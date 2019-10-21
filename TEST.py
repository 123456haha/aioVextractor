#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 2019/9/9
# IDE: PyCharm
"""
RUN ME BEFORE GOING SERIOUS!
"""

from pprint import pprint
from aioVextractor import extract
from aioVextractor.extractor import *
import aiohttp
import asyncio

async def test(asking=True):
    async with aiohttp.ClientSession() as session:
        fail_url = set()
        for ie in gen_extractor_classes():
            try:
                TEST_CASE = ie.TEST_CASE
            except:
                continue
            for sample in TEST_CASE:
                if asking:
                    procceed = input(f"proccee webpage_url: {sample}?\n"
                                     f"press Enter/n/no to ignore and y/yes to procceed\n"
                                     f"enter `pass` to the next extractor TEST_CASE: ")
                else:
                    procceed = "yes"
                if procceed in {"y", 'yes'}:
                    result = await extract(webpage_url=sample, session=session)
                    pprint(result)
                    if not result:
                        fail_url.add(sample)
                    print("**************************************************"
                          "*************************************************\n")
                elif procceed == "pass":
                    break
        else:
            print(f"fail_url: \n"
                  f"{fail_url}")


asyncio.run(test(asking=False))
