#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 2019/9/30
# IDE: PyCharm

from aioVextractor.utils.requests_retry import RequestRetry
from aioVextractor.utils.user_agent import UserAgent
from aioVextractor.player import tencent
from aioVextractor.player import youku
from aioVextractor.player import xinpianchang
from random import choice
from scrapy.selector import Selector
import asyncio
import aiohttp
import platform
from aioVextractor import config
import wrapt
import re
import youtube_dl
import traceback
import jmespath
import time
from os.path import splitext
import html
import os
from concurrent import futures  ## lib for multiprocessing and threading
from urllib.parse import (
    urlparse,
    parse_qs,
)


@wrapt.decorator
async def validate(func, extractor_instace, args, kwargs):
    """
    1. ensure the accuracy of the input url: match the url by `target_website` in BaseExtractor
    2. ensure the integrated of the output data according to the config.FIELDS
    :return:
    """
    ## list of regexs for matching exact webpage_url for extractor_instance
    target_website = extractor_instace.target_website
    webpage_url = kwargs['webpage_url']
    urls = []
    ## match url form webpage_url
    for regex in target_website:
        urls += re.findall(regex, webpage_url)

    ## asyncio gather these urls
    gather_results = await asyncio.gather(
        *[
            func(*args, **{**kwargs, **{"webpage_url": webpage_url}}) for webpage_url in urls
        ])

    outputs = []
    for results in gather_results:
        ## if the results is []/False/None/0
        ## skip to the next one
        if results:
            pass
        else:
            continue
            # return None

        if isinstance(results, list):
            pass
        elif isinstance(results, dict):
            results = [results]

        ## validate the integrity of the output
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
                    dependent_field_value_actual = result.get(dependent_field_name,
                                                              "f79e2450e6b911e99af648d705c16021")
                    ## actual value of the dependent_field
                    ## if the dependent_field is not given
                    ## the default value is considered
                    dependent_field_value_actual = config.FIELDS[dependent_field_name]["default_value"] \
                        if dependent_field_value_actual == "f79e2450e6b911e99af648d705c16021" \
                        else dependent_field_value_actual
                    if dependent_field_value_actual == dependent_field_value:
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


class BaseExtractor:
    """
    When you define a new extractor base on this class
    1. specify target_website as class variable
    2. inherit BaseExtractor.__init__() and define self.from_
    3. redefine BaseExtractor.entracne()
    """
    ## a list of regexs to match the target website
    ## this is used to identify whether a incoming url is extractable
    target_website = [
        r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),#]|(?:%[0-9a-fA-F][0-9a-fA-F]))+",
    ]

    def __init__(self, *args, **kwargs):
        self.from_ = "generic"

    @classmethod
    def suitable(cls, url):
        """
        Define a classmethod to confirm that the incoming urls
        match the regex in target_website,
        before you need to instantiate the class
        """
        urls = []
        for _VALID_URL in cls.target_website:
            urls += re.findall(_VALID_URL, url)
        else:
            return urls if urls else False

    def __enter__(self):
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

    async def extract_iframe(self, iframe_url, session):
        """
        An API to extract iframe with src link to v.qq / youku / youtube / vimeo and etc.
        :param iframe_url:
        :param session:
        :return:
        """
        if 'v.qq.com' in iframe_url:
            return await tencent.entrance(iframe_url=iframe_url, session=session)
        elif 'player.youku.com' in iframe_url or 'v.youku' in iframe_url:
            return await youku.entrance(iframe_url=iframe_url, session=session)
        elif "xinpianchang" in iframe_url:
            return await xinpianchang.entrance(webpage_url=iframe_url, session=session)
        else:
            return await self.breakdown(webpage_url=iframe_url)

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

    @staticmethod
    def janitor(string):
        """
        match the url(s) from string
        :param string:
        :return:
        """
        url_list = re.findall(config.URL_REGEX, string)  ## find all url in the string
        return url_list

    async def extract_info(self, webpage_url, collaborate=True):
        """
        Extracting the webpage by youtube-dl without downloading
        :param webpage_url:
        :param collaborate: IGNORE THIS (seems to be useless at this point)
        :return:
        """
        args = {
            "nocheckcertificate": True,
            "ignoreerrors": True,
            "quiet": True,
            "nopart": True,
            # "download_archive": "record.txt",
            "no_warnings": True,
            "youtube_include_dash_manifest": False,
            'simulate': True,
            'user-agent': self.general_headers(user_agent=self.random_ua()),
        }
        try:
            with youtube_dl.YoutubeDL(args) as ydl:
                try:
                    VideoJson = ydl.extract_info(webpage_url)
                except:
                    traceback.print_exc()
                    return False
                else:
                    if VideoJson:
                        if collaborate:
                            result = self.extract_single(video_json=VideoJson, webpage_url=webpage_url)
                            return result
                        else:  ## webpage extracting using only youtube-dl
                            if 'entries' in VideoJson:
                                result = []
                                for entry in jmespath.search('entries[]', VideoJson):
                                    element = self.extract_single(video_json=entry, webpage_url=webpage_url)
                                    result.append(element)
                                return result
                            else:
                                result = self.extract_single(video_json=VideoJson, webpage_url=webpage_url)
                                return result
                    else:
                        return False
        except:
            traceback.print_exc()
            return False

    def extract_single(self, video_json, webpage_url):
        """
        scrubbing info from video_json which comes from youtube-dl output
        :param video_json:
        :param webpage_url:
        :return:
        """
        result = dict()
        result['downloader'] = 'ytd'
        result['webpage_url'] = webpage_url
        result['author'] = jmespath.search('uploader', video_json)
        result['cover'] = self.check_cover(jmespath.search('thumbnail', video_json))
        create_time = jmespath.search('upload_date', video_json)
        upload_ts = int(time.mktime(time.strptime(create_time, '%Y%m%d'))) if create_time else create_time
        result['upload_ts'] = upload_ts
        result['description'] = jmespath.search('description', video_json)
        duration = jmespath.search('duration', video_json)
        result['duration'] = int(duration) if duration else 0
        result['rating'] = jmespath.search('average_rating', video_json)
        result['height'] = jmespath.search('height', video_json)
        result['like_count'] = jmespath.search('like_count', video_json)
        result['view_count'] = jmespath.search('view_count', video_json)
        result['dislike_count'] = jmespath.search('dislike_count', video_json)
        result['width'] = jmespath.search('width', video_json)
        result['vid'] = jmespath.search('id', video_json)
        cate = jmespath.search('categories', video_json)
        result['category'] = ','.join(list(map(lambda x: x.replace(' & ', ','), cate))) \
            if cate \
            else cate
        # formats = self.extract_play_addr(VideoJson)
        # result['play_addr'] = formats['url']
        result['from'] = video_json.get('extractor', None).lower() \
            if video_json.get('extractor', None) \
            else urlparse(webpage_url).netloc
        result['title'] = jmespath.search('title', video_json)
        video_tags = jmespath.search('tags', video_json)
        result['tag'] = video_tags
        return result

    @staticmethod
    def check_cover(cover):
        """
        Some of the vimeo cover urls contain play_icon
        This method try to extract the url that not
        :param cover:
        :return:
        """
        if urlparse(cover).path == '/filter/overlay':
            try:
                cover_ = parse_qs(urlparse(cover).query).get('src0')[0]
            except IndexError:
                return cover
            if 'play_icon' in cover_:
                return cover
            elif cover_ is None:
                return cover
            else:
                return cover_
        else:
            return cover

    @staticmethod
    def extract_play_addr(video_json):
        """

        This method is depreciated

        extract play_addr from the return of youtube-dl
        :param video_json:
        :return:
        """
        video_list = jmespath.search('formats[]', video_json)
        try:
            try:
                return sorted(filter(
                    lambda x: (x.get('protocol', '') in {'https', 'http'}) and x.get('acodec') != 'none' and x.get(
                        'vcodec') != 'none', video_list), key=lambda x: x['filesize'])[-1]
            except KeyError:
                return sorted(filter(
                    lambda x: x.get('protocol', '') in {'https', 'http'} and x.get('acodec') != 'none' and x.get(
                        'vcodec') != 'none', video_list), key=lambda x: x['height'])[-1]
            except IndexError:
                return jmespath.search('formats[-1]', video_json)
        except:
            return jmespath.search('formats[-1]', video_json)

    @staticmethod
    def merge_dicts(*dict_args):
        """
        Given any number of dicts, shallow copy and merge into a new dict,

        You may use new_dict = {**dict_num_one, **dict_num_two},
        which will merge dict_num_one and dict_num_two,
        and dict_num_two's value will replace dict_num_one's value when they have the same key

        This method provide something more the the above method:
        1. merging more than 2 dictionaries
        2. only replace the previous value with the upcoming value if the previous value is in {None/False/0}
        """

        result = {}
        for dictionary in dict_args:
            for k, v in dictionary.items():
                if k in result:
                    result[k] = result[k] if result[k] else v
                else:
                    result[k] = v
            result.update(dictionary)
        return result

    @RequestRetry
    async def retrieve_webpapge(self, webpage_url):
        """
        retrieve webpage
        """
        async with aiohttp.ClientSession(raise_for_status=True) as session:
            async with session.get(webpage_url, headers=self.general_headers(self.random_ua())) as response:
                return await response.text()

    async def breakdown(self, webpage_url):
        """
        extract iframes from webpage_url and extract these iframe_urls concurrently
        :param webpage_url:
        :return:
        """

        def wrapper(url):
            try:
                new_loop = asyncio.new_event_loop()
                asyncio.set_event_loop(new_loop)
                r = new_loop.run_until_complete(self.extract_info(webpage_url=url, collaborate=False))
                new_loop.close()
                return r
            except:
                traceback.print_exc()
                return False

        webpage_content = await self.retrieve_webpapge(webpage_url=webpage_url)
        selector = Selector(text=webpage_content)
        iframe_src = selector.css('iframe::attr(src)').extract()
        with futures.ThreadPoolExecutor(max_workers=min(10, os.cpu_count())) as executor:  ## set up processes
            executor.submit(wrapper)
            future_to_url = [executor.submit(wrapper, url=iframe) for iframe in iframe_src]
            results = []
            try:
                for f in futures.as_completed(future_to_url, timeout=max([len(iframe_src) * 3, 15])):
                    try:
                        result = f.result()
                        result['playlist_url'] = webpage_url
                        results.append(result)
                    except:
                        traceback.print_exc()
                        continue
            except:
                traceback.print_exc()
                pass
            return results

    @staticmethod
    def unescape(string):
        if string:
            return html.unescape(string)
        else:
            return None

    @staticmethod
    def get_ext(url_):
        """
        Return the filename extension from url, or ''
        """
        if url_ is None:
            return False
        parsed = urlparse(url_)
        root, ext_ = splitext(parsed.path)
        ext = ext_[1:]  # or ext[1:] if you don't want the leading '.'
        ## ext = 'jpeg@80w_80h_1e_1c'
        return ext.split('@')[0]

    @RequestRetry
    async def request_get(self, url, session, headers, params=None, response_type="text", **kwargs):
        async with session.get(url, headers=headers, params=params, **kwargs) as response:
            if response_type == "text":
                return await response.text()
            elif response_type == "json":
                return await response.json()

    def __exit__(self, exc_type, exc_val, exc_tb):
        # asyncio.run(self.async_session.close())
        print(f"exc_type, exc_val, exc_tb: {exc_type, exc_val, exc_tb}")


if __name__ == '__main__':
    from pprint import pprint

    with BaseExtractor() as extractor:
        res = extractor.sync_entrance(webpage_url="https://www.digitaling.com/projects/55684.html")
        pprint(res)
        res = extractor.sync_entrance(webpage_url="https://www.digitaling.com/projects/56636.html")
        pprint(res)
