#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 2019/9/30
# IDE: PyCharm

from aioVextractor.utils.requests_retry import RequestRetry
from aioVextractor.utils.user_agent import UserAgent
from aioVextractor.player import tencent
from aioVextractor.player import youku
from aioVextractor.extractor import common
from random import choice
from scrapy.selector import Selector
import asyncio
import aiohttp
import platform
from aioVextractor import config
import traceback
import wrapt
import functools


# import trio


def validate(wrapped=None):
    """
    ensure the integrated of the output data according to the config.FIELDS
    :param wrapped:
    :return:
    """
    if wrapped is None:
        return functools.partial(validate)

    @wrapt.decorator
    async def wrapper(func, instance, args, kwargs):
        results = await func(*args, **kwargs)
        outputs = []
        for result in results:
            output = dict()
            for field in config.FIELDS:
                field_info = config.FIELDS[field]
                signi_level = field_info["signi_level"]
                if signi_level == config.FIELD_SIGNI_LEVEL["else"]:
                    output[field] = result.get(field, field_info["default_value"])
                elif signi_level == config.FIELD_SIGNI_LEVEL["must"]:
                    try:
                        output[field] = result[field]
                    except KeyError:
                        print(f"You should have specify field `{field}`")
                        output = False
                        break
                elif signi_level == config.FIELD_SIGNI_LEVEL["condition_must"]:
                    dependent_field_name = field_info["dependent_field_name"]
                    dependent_field_value = field_info["dependent_field_value"]
                    if dependent_field_value in {result.get(dependent_field_name, "f79e2450e6b911e99af648d705c16021"),
                                                 config.FIELDS[dependent_field_name]["default_value"]}:
                        try:
                            output[field] = result[field]
                        except KeyError:
                            print(f"You should have specify field `{field}` "
                                  f"while field `{dependent_field_name}` == {dependent_field_value}")
                            output = False
                            break
                    else:
                        ## SIGNI_LEVEL=0
                        output[field] = result.get(field, field_info['default_value'])
            if output:  ## after scanning all the listed field in config.FIELDS
                outputs.append(output)
        else:
            return outputs

    return wrapper(wrapped)


class BaseExtractor:
    def __init__(self, from_="generic"):
        self.from_ = from_

    def __enter__(self):
        ## all possible output fields
        # self.fields = [
        #     'ad_link',
        #     'author',
        #     'author_attention',
        #     'author_avatar',
        #     'author_birthday',
        #     'author_description',
        #     'author_follwer_count',
        #     'author_follwing_count',
        #     'author_gender',
        #     'author_id',
        #     'author_sign',
        #     'author_url',
        #     'author_videoNum',
        #     'category',
        #     # 'cdn_url',
        #     'collect_count',
        #     'comment_count',
        #     'cover',
        #     # 'created_at',
        #     'description',
        #     'dislike_count',
        #     'download_count',
        #     'downloader',
        #     'duration',
        #     'forward_count',
        #     'from',
        #     'gender',
        #     'height',
        #     'language',
        #     'like_count',
        #     'play_addr',
        #     # 'player_id',
        #     'rating',
        #     'recommend',
        #     'region',
        #     'share_count',
        #     'tag',
        #     'title',
        #     'upload_date',
        #     'upload_ts',
        #     'vid',
        #     'view_count',
        #     'webpage_url',
        #     'width',
        # ]
        ## a random headers with UA parm
        self.general_headers = lambda user_agent: {
            'Connection': 'keep-alive',
            'Cache-Control': 'max-age=0',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;'
                      'q=0.9,image/webp,image/apng,*/*;'
                      'q=0.8,application/signed-exchange;'
                      'v=b3',
            'Referer': 'https://www.digitaling.com/articles',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,ko;q=0.7',
        }
        self.random_ua = lambda: choice(UserAgent)
        # self.results = []
        return self

    @validate
    @RequestRetry
    async def entrance(self, webpage_url, session):
        """

        If you want to add a new extractor for a specific website,
        this is the top level API you are looking for.

        This API will not show you how to deintegrate(request and scrubbing) a website,
        but give you some convinence apis(self.extract_iframe(), @validate, @RequestRetry) and tools(self.general_headers())
        Should return necessary field
        :param webpage_url:
        :param session: aiohttp.ClientSession()
        :return:
        """
        headers = self.general_headers(user_agent=self.random_ua())
        async with session.get(webpage_url, headers=headers) as response:
            text = await response.text(encoding='utf8', errors='ignore')
            selector = Selector(text=text)
            urls = selector.css('iframe[src]::attr(src)').extract()
            if urls:
                results = await asyncio.gather(
                    *[self.extract_iframe(
                        iframe_url=iframe_url,
                        session=session
                    ) for iframe_url in urls])
                for ele in results:
                    if ele:
                        ele['from'] = self.from_
                        ele['webpage_url'] = webpage_url

                # self.results += results
                return results
            else:  ## webpage having no iframe with attr of `src`
                return False

    @staticmethod
    async def extract_iframe(iframe_url, session):
        """
        An API to extract iframe with src link to v.qq / youku / youtube / vimeo and etc.
        :param iframe_url:
        :param session:
        :return:
        """
        if 'v.qq.com' in iframe_url:
            return await tencent.entrance(iframe_url=iframe_url, session=session)
        elif 'player.youku.com' in iframe_url:
            return await youku.entrance(iframe_url=iframe_url, session=session)
        else:
            return await common.breakdown(webpage_url=iframe_url)

    def sync_entrance(self, webpage_url):
        """
        A synchronous entrance to call self.entrance()
        :param webpage_url:
        :return:
        """

        async def wrapper():
            async with aiohttp.ClientSession() as session:
                return await self.entrance(webpage_url=webpage_url, session=session)

        python_version = float(".".join(platform.python_version_tuple()[0:2]))
        if python_version >= 3.7:
            return asyncio.run(wrapper())
        elif 3.5 <= python_version <= 3.6:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            results = loop.run_until_complete(wrapper())
            loop.close()
            return results
        else:
            return "The Python Interpreter you are using is {python_version}.\n" \
                   "You should consider switching it to some more modern one such as Python 3.7+ " \
                .format(python_version=python_version)

    def __exit__(self, exc_type, exc_val, exc_tb):
        # asyncio.run(self.async_session.close())
        print(f"exc_type, exc_val, exc_tb: {exc_type, exc_val, exc_tb}")


if __name__ == '__main__':
    with BaseExtractor(from_="custom_extractor") as extractor:
        res = extractor.sync_entrance(webpage_url="https://www.digitaling.com/projects/55684.html")
        print(res)
        res = extractor.sync_entrance(webpage_url="https://www.digitaling.com/projects/56636.html")
        print(res)
        # for i in extractor.results:
        #     print(i)
    # extractor = BaseExtractor()
