#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 2019/7/6
# IDE: PyCharm

import traceback
import re
from scrapy import Selector
from aioVextractor.breaker import (
    BaseBreaker,
    BreakerValidater
)
from aioVextractor.utils import RequestRetry
from lxml import etree


class Breaker(BaseBreaker):
    target_website = [
        "https://www.vmovier.com/",
        "https://www.xinpianchang.com/channel/index/id-\d{1,4}.*",
    ]

    TEST_CASE = [
        'https://www.vmovier.com/',

        # 'https://www.xinpianchang.com/channel/index/id-0/sort-pick/type-0?form=indexEditorPick&position=more',
        # 'https://www.xinpianchang.com/channel/index/id-49/sort-like?from=indexCate4&position=more',
        # 'https://www.xinpianchang.com/channel/index/id-129/sort-like?from=indexCate4&position=more',
        # 'https://www.xinpianchang.com/channel/index/id-31/sort-like?from=indexCate2&position=more',
        # 'https://www.xinpianchang.com/channel/index/id-29/sort-like?from=indexCate1&position=more',
        # 'https://www.xinpianchang.com/channel/index/id-76/sort-like?from=indexCate3&position=more',
        # 'https://www.xinpianchang.com/channel/index/id-1/sort-like?from=indexCate1&position=more',
    ]

    def __init__(self, *args, **kwargs):
        BaseBreaker.__init__(self, *args, **kwargs)
        self.from_ = "xinpianchang"

    @BreakerValidater
    @RequestRetry
    async def breakdown(self, webpage_url, session, **kwargs):
        if re.match('https://www.vmovier.com/', webpage_url):
            response = await self.retrieve_tag_paging_api(session=session)
            results = self.extract_tag_pageing_api(response=response, webpage_url=webpage_url)
            return results
        else:
            vid = re.findall('id-(\d{1,5})', webpage_url)[0]
            from1 = re.findall('(\w{1,4}\=\w{5,15})', webpage_url)[0]
            headers = {
                'authority': 'www.xinpianchang.com/58031?from=index_new_img',
                'cache-control': 'max-age=0',
                'upgrade-insecure-requests': '1',
                'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
                'sec-fetch-user': '?1',
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
                'sec-fetch-site': 'same-origin',
                'sec-fetch-mode': 'navigate',
                'referer': 'https://www.xinpianchang.com/square',
                'accept-encoding': 'gzip, deflate, br',
                'accept-language': 'zh-CN,zh;q=0.9',
                'cookie': 'Device_ID=5def447a220cc; _ga=GA1.2.1078040784.1575961723; UM_distinctid=16eeea38256980-07e43b5ad86deb-31760856-1fa400-16eeea38257b54; Hm_lvt_31eb3c3fd6ffa0c0374d37ca2acb6f3b=1576120876; PHPSESSID=tq07pndem5rhagqo1r9ml98pja; SERVER_ID=b52601c8-5caf45c0; Authorization=C1BFC7D9788A55A27788A5447F788A5BECF788A5526C90120A47; CNZZDATA1262268826=482028349-1575960600-%7C1576725757; _gid=GA1.2.637144854.1576727787; Hm_lvt_dfbb354a7c147964edec94b42797c7ac=1576728120,1576728131,1576728168,1576728181; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%2216eeea3822c615-04052ab98abca6-31760856-2073600-16eeea3822d892%22%2C%22%24device_id%22%3A%2216eeea3822c615-04052ab98abca6-31760856-2073600-16eeea3822d892%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_referrer%22%3A%22%22%2C%22%24latest_referrer_host%22%3A%22%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC_%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80%22%7D%7D; channel_page=aQ%3D%3D; Hm_lpvt_dfbb354a7c147964edec94b42797c7ac=1576731091; cn_1262268826_dplus=%7B%22distinct_id%22%3A%20%2216eeea38256980-07e43b5ad86deb-31760856-1fa400-16eeea38257b54%22%2C%22%24_sessionid%22%3A%200%2C%22%24_sessionTime%22%3A%201576731315%2C%22%24dp%22%3A%200%2C%22%24_sessionPVTime%22%3A%201576731315%7D',
            }

            url = f'https://www.xinpianchang.com/channel/index/id-{vid}/sort-like'
            params = (
                ('from', from1),
                ('position', 'more'),
            )
            response = await self.request(
                url=url,
                headers=headers,
                params=params,
                session=session,
                # page=page
            )
            results = self.extract_user_pageing(response=response, webpage_url=webpage_url)
            return results

    @RequestRetry
    async def retrieve_tag_paging_api(self, session,):
        cookies = {
            'UM_distinctid': '16ef819c84a24e-04e4a238c388ac-31760856-1fa400-16ef819c84b44f',
            'zg_did': '%7B%22did%22%3A%20%2216ef819c8948df-086fc813e93887-31760856-1fa400-16ef819c8957b5%22%7D',
            'bdshare_firstime': '1576121258008',
            'PHPSESSID': 'skmg75ghj25an3re0kms5k33au',
            'Hm_lvt_dfd9b1dd5fd1333a1c8e27ce6b5e60ce': '1576730667,1576731383,1576807135,1576807516',
            'zg_88fc4ba51b1e4afdacf3dc9c0994055f': '%7B%22sid%22%3A%201576810704.176%2C%22updated%22%3A%201576810704.176%2C%22info%22%3A%201576728189545%7D',
            'CNZZDATA1262140596': '210108557-1576116281-%7C1576808240',
            'Hm_lpvt_dfd9b1dd5fd1333a1c8e27ce6b5e60ce': '1576810704',
            'responseTimeline': '165',
            'cn_1262140596_dplus': '%7B%22distinct_id%22%3A%20%2216ef819c84a24e-04e4a238c388ac-31760856-1fa400-16ef819c84b44f%22%2C%22%24_sessionid%22%3A%200%2C%22%24_sessionTime%22%3A%201576810715%2C%22%24dp%22%3A%200%2C%22%24_sessionPVTime%22%3A%201576810715%2C%22initial_view_time%22%3A%20%221576116281%22%2C%22initial_referrer%22%3A%20%22%24direct%22%2C%22initial_referrer_domain%22%3A%20%22%24direct%22%2C%22%24recent_outside_referrer%22%3A%20%22%24direct%22%7D',
        }
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        }
        url = 'https://www.vmovier.com/'
        response = await self.request(
            url=url,
            session=session,
            headers=headers,
            cookies=cookies,
        )
        return response

    def extract_tag_pageing_api(self, response, webpage_url):
        datas = Selector(text=response)
        data = datas.xpath('//div[@class="index-main"]/ul/li')
        results = []
        for data_list in data:
            item = dict()
            try:
                item['vid'] = data_list.xpath('./@data-id').extract_first()
                item['cover'] = data_list.xpath('.//img/@src').extract_first()
                item['upload_ts'] = data_list.xpath('.//span[@class="time"]/text()')[1].extract()
                item['title'] = data_list.xpath('.//li[@class="clearfix"]/a/@title').extract_first()
                item['view_count'] = data_list.xpath('.//div[@class="post-ope"]/span[1]/text()').extract_first()
                item['like_count'] = data_list.xpath('.//div[@class="post-ope"]/span[2]/text()').extract_first()
                item['forward_count'] = data_list.xpath('.//div[@class="post-ope"]/a/text()').extract_first()
                item['description'] = data_list.xpath('.//div[@class="index-intro"]/a/text()').extract_first()
                item['playlist_url'] = f"https://www.xinpianchang.com/a{item['vid']}"
                item['webpage_url'] = webpage_url,
                item['from'] = 'xinpianchang'
                results.append(item)
            except:
                traceback.print_exc()
                continue
        return results, True, {}

    def extract_user_pageing(self, response, webpage_url):
        datas = Selector(text=response)
        data = datas.xpath('//ul/li[@class="enter-filmplay"]')
        results = []
        for data_list in data:
            item = dict()
            try:
                item['vid'] = data_list.xpath('./@data-articleid').extract_first()
                item['cover'] = data_list.xpath('.//img[@class="lazy-img"]/@_src').extract_first()
                item['upload_ts'] = data_list.xpath('.//a/div[2]/p/text()').extract()
                item['title'] = data_list.xpath('.//div[1]//p/text()').extract_first()
                item['category'] = data_list.xpath('.//span/text()').extract_first()
                item['view_count'] = data_list.xpath('.//span[1]/text()').extract_first()
                item['like_count'] = data_list.xpath('.//span[2]/text()').extract_first()
                item['author_id'] = data_list.xpath('//@data-userid').extract_first()
                item['author'] = data_list.xpath('.//div[@class="info"]/p/text()').extract()
                item['playlist_url'] = f"https://www.xinpianchang.com/a{item['vid']}?from=ArticleList"
                item['webpage_url'] = webpage_url
                item['from'] = 'xinpianchang'
                results.append(item)
            except:
                traceback.print_exc()
                continue
        return results, True, {}


if __name__ == '__main__':
    from pprint import pprint

    with Breaker() as breaker:
        res = breaker.sync_breakdown(
            webpage_url=Breaker.TEST_CASE[-1],
            # page=2,
        )
        pprint(res)




# 下一页的方法

# page = int(kwargs.pop("page", 1))
# mes = await self.request(
#     url=webpage_url,
#     session=session, )
# html = etree.HTML(mes)
# nextpage = html.xpath('//div[@class="page-wrap"]/div/a[6]/@href')
# next_url = f'https://www.xinpianchang.com/{nextpage}'
# if page > 1:
#     url = next_url
# else:
#     url = webpage_url

