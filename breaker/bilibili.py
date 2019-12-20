#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 2019/7/6
# IDE: PyCharm
from bs4 import BeautifulSoup
import re
import traceback
import jmespath
from aioVextractor.breaker import (
    BaseBreaker,
    BreakerValidater
)
from aioVextractor.utils import RequestRetry


class Breaker(BaseBreaker):
    target_website = [
        "https://www.bilibili.com/v/ad/ad/\?.*",
        "https://www.bilibili.com/v/cinephile/.*",
        "https://space\.bilibili\.com/\d{5,10}",

    ]

    downloader = 'ytd'

    TEST_CASE = [
        "https://space.bilibili.com/29296192/video",

        "https://www.bilibili.com/v/ad/ad/?spm_id_from=333.851.b_7072696d6172794368616e6e656c4d656e75.77",

        "https://www.bilibili.com/v/cinephile/shortfilm/?spm_id_from=333.5.b_63696e657068696c655f73686f727466696c6d.2#/",
        "https://www.bilibili.com/v/cinephile/trailer_info/?spm_id_from=333.5.b_63696e657068696c655f747261696c65725f696e666f.2#/",
        "https://www.bilibili.com/v/cinephile/cinecism/?spm_id_from=333.5.b_63696e657068696c655f63696e656369736d.2#/",
        "https://www.bilibili.com/v/cinephile/montage/?spm_id_from=333.5.b_63696e657068696c655f6d6f6e74616765.2#/",
    ]

    def __init__(self, *args, **kwargs):
        BaseBreaker.__init__(self, *args, **kwargs)
        self.from_ = "bilibili"

    @RequestRetry
    @BreakerValidater
    async def breakdown(self, webpage_url, session, **kwargs):
        page = int(kwargs.pop("page", 1))
        if re.match("https://www.bilibili.com/v/cinephile/?.*", webpage_url):
            response = await self.extract_first(session=session, page=page)
            result = self.extract_first(response=response, page=page, playlist_url=webpage_url)
            return result
        elif re.match("https://www.bilibili.com/v/ad/ad/?.*", webpage_url):
            spm_id_from = re.findall("spm_id_from=(.*)")
            response = await self.extract_second(session=session, spm_id_from=spm_id_from, page=page)
            result = self.extract_second(response=response, page=page, playlist_url=webpage_url)
            return result
        else:
            headers = {
                'Accept': 'application/json, text/plain, */*',
                'Referer': f'{webpage_url}/video?tid=0&page={page - 1}&keyword=&order=pubdate'
                if page > 1
                else f'{webpage_url}/video?tid=0&page=1&keyword=&order=pubdate',
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.108 Safari/537.36',
            }
            mid = re.findall("https://space\.bilibili\.com/(\d{5,10})", webpage_url)[0]
            params = (
                ('mid', mid),
                ('pagesize', '30'),
                ('tid', '0'),
                ('page', str(page)),
                ('keyword', ''),
                ('order', 'pubdate'),
            )
            api = 'https://space.bilibili.com/ajax/member/getSubmitVideos'
            response = await self.request(
                url=api,
                headers=headers,
                session=session,
                params=params,
                response_type="json"
            )
            results = self.extract(response=response, page=page, playlist_url=webpage_url)
            return results

    def extract(self, response, page, playlist_url):
        results = []
        vlist = jmespath.search("data.vlist", response)
        max_page = jmespath.search(['data.page'], response) // 25 + 1
        has_more = True if page < max_page else False
        for ele in vlist:
            try:
                results.append({
                    "comment_count": ele['comment'],
                    "view_count": ele['play'],
                    "cover": "http://" + ele['pic'].strip('//'),
                    "description": ele['description'],
                    "title": ele['title'],
                    "author": ele['author'],
                    "author_id": ele['mid'],
                    "upload_ts": ele['created'],
                    "vid": ele['aid'],
                    "duration": self.cal_duration(ele['length']),
                    "from": "bilibili",
                    "playlist_url": playlist_url,
                    "webpage_url": f'https://www.bilibili.com/video/av{ele["aid"]}',
                })
            except:
                traceback.print_exc()
                continue
        else:
            return results, has_more, {}

    @RequestRetry
    async def extract_first(self, session, page, webpage_url):
        cookies = {
                '$Cookie: CURRENT_FNVAL': '16',
                '_uuid': '0544AE64-EECD-0931-9862-FC4E03F59DB420631infoc',
                'buvid3': 'B06C199B-749B-49CE-B582-6D0422FA551C190944infoc',
                'LIVE_BUVID': 'AUTO6115759479211558',
                'stardustvideo': '1',
                'rpdid': '|(um|JY~umuY0J\'ul~lmR~mkl',
                'laboratory': '1-1',
                'sid': '4xbomhpx',
                'INTVER': '1',
            }
        api = 'https://api.bilibili.com/x/web-interface/newlist?callback=jqueryCallback_bili_47808997877590054&rid=182&type=0&pn=1&ps=20&jsonp=jsonp&_=1576666021253'
        callback = re.findall('callback=(\w{14}\_\w{4}\_\d{17})', api)
        rid = re.findall('rid=(\d{1,3})', api)
        aid = re.findall('_=(\d{1,14})', api)
        headers = {
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
                'Referer': 'https://www.bilibili.com/v/cinephile/shortfilm/?spm_id_from=333.5.b_63696e657068696c655f73686f727466696c6d.2#/',
            }
        params = (
                ('callback', callback),
                ('rid', rid),
                ('type', '0'),
                ('pn', '1'),
                ('ps', '20'),
                ('jsonp', 'jsonp'),
                ('_', aid),
            )
        response = await self.request(
                url=api,
                session=session,
                cookies=cookies,
                headers=headers,
                params=params,
                response_type="json"
            )
        results = self.extract(response=response, page=page, playlist_url=webpage_url)
        return results

    def extract_first(self, page, response, playlist_url):
        results = []
        data = jmespath.search("data.archives", response)
        max_page = jmespath.search(['data.page'], response) // 20 + 1
        has_more = True if page < max_page else False
        for item in data:
            try:
                results.append({
                    "vid": item['aid'],
                    "playlist_url": playlist_url,
                    "cover": item['pic'],
                    "description": item['desc'],
                    "title": item['title'],
                    "from": "bilibili",
                    "author": jmespath.search(['owner.name'], item),
                    "author_id": jmespath.search(['owner.mid'], item),
                    "upload_ts": item['ctime'],
                    "comment_count": item['comment'],
                    "view_count": item['play'],
                    "webpage_url": f'https://www.bilibili.com/video/av{item["vid"]}',
                    "category": item['tname']
                })
            except:
                traceback.print_exc()
                continue
        else:
            return results, has_more, {}

    @RequestRetry
    async def extract_second(self, spm_id_from, session, page, webpage_url):
        cookies = {
            '$Cookie: CURRENT_FNVAL': '16',
            '_uuid': '0544AE64-EECD-0931-9862-FC4E03F59DB420631infoc',
            'buvid3': 'B06C199B-749B-49CE-B582-6D0422FA551C190944infoc',
            'LIVE_BUVID': 'AUTO6115759479211558',
            'stardustvideo': '1',
            'rpdid': '|(um|JY~umuY0J\'ul~lmR~mkl',
            'laboratory': '1-1',
            'sid': '4xbomhpx',
            'INTVER': '1',
        }
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
            'Referer': 'https://www.bilibili.com/v/ad/ad/?spm_id_from=333.851.b_7072696d6172794368616e6e656c4d656e75.81',
        }
        api = 'https://api.bilibili.com/x/web-interface/newlist?callback=jqueryCallback_bili_47808997877590054&rid=182&type=0&pn=1&ps=20&jsonp=jsonp&_=1576666021253'
        callback = re.findall('callback=(\w{14}\_\w{4}\_\d{17})')
        rid = re.findall('rid=(\d{1,3})')
        aid = re.findall('_=(\d{1,14})')
        params = (
            ('callback', callback),
            ('rid', rid),
            ('type', '0'),
            ('pn', '1'),
            ('ps', '20'),
            ('jsonp', 'jsonp'),
            ('_', aid),
        )
        response = await self.request(
            url=api,
            session=session,
            cookies=cookies,
            headers=headers,
            params=params,
            response_type="json"
        )
        results = self.extract(response=response, page=page, playlist_url=webpage_url)
        return results

    def extract_second(self, page, response, playlist_url):
        results = []
        data = jmespath.search("data.archives", response)
        max_page = jmespath.search(['data.page'], response) // 20 + 1
        has_more = True if page < max_page else False
        for item in data:
            try:
                results.append({
                    "vid": item['aid'],
                    "playlist_url": playlist_url,
                    "cover": item['pic'],
                    "description": item['desc'],
                    "title": item['title'],
                    "from": "bilibili",
                    "author": jmespath.search(['owner.name'], item),
                    "author_id": jmespath.search(['owner.mid '], item),
                    "upload_ts": item['ctime'],
                    "comment_count": item['comment'],
                    "view_count": item['play'],
                    "webpage_url": f'https://www.bilibili.com/video/av{item["vid"]}',
                    "category": item['tname']
                })
            except:
                traceback.print_exc()
                continue
        else:
            return results, has_more, {}

    @staticmethod
    def cal_duration(raw_duration_string):
        regex = re.compile("(\d{1,3}):?")
        _duration = regex.findall(raw_duration_string)
        duration = 0
        for num, i in enumerate(_duration[::-1]):
            duration += int(i) * (60 ** num)
        return duration


if __name__ == '__main__':
    from pprint import pprint

    with Breaker() as breaker:
        res = breaker.sync_breakdown(
            webpage_url=Breaker.TEST_CASE[-1],
            # page=2
        )
        pprint(res)
