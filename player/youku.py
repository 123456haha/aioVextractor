#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 2019/6/20
# IDE: PyCharm


import traceback
import time, json
import jmespath
from scrapy import Selector
import asyncio
from aioVextractor.utils.requests_retry import RequestRetry
from aioVextractor.utils.user_agent import UserAgent
from random import choice


@RequestRetry
async def entrance(iframe_url, session):
    try:
        vid = iframe_url.split('?')[0].split('/')[-1].replace('==', '').lstrip('id_')
    except:
        traceback.print_exc()
        return False
    else:
        webpage_url = "https://v.youku.com/v_show/id_{}".format(vid)
        data = {"video_id": vid,
                "client_id": "b598bfd8ec862716",
                "callback": "f'youkuPlayer_call_{int(time.time() * 1000)}'",
                "type": "pc",
                "embsig": "",
                "version": "1.0",
                "_t": "006315043435963385"}
        yk_url = 'https://api.youku.com/players/custom.json?'
        async with session.get(yk_url, params=data, verify_ssl=False) as res:
            html = await res.text(encoding='utf-8', errors='ignore')
            customdata = json.loads(html)
            # customdata = json.loads(html.replace(data['callback'], '')[1:-2])
            try:
                stealsign = customdata['stealsign']
            except:
                traceback.print_exc()
                return False
            else:
                gather_results = await asyncio.gather(*[
                    extract_info(vid=vid, sign=stealsign, client_id=data['client_id'], session=session),
                    extract_comment_count(vid=vid, session=session),
                    extract_webpage(url=webpage_url, session=session)
                ])
                result = {**{"webpage_url": webpage_url, "vid": vid, },
                          **{**gather_results[0],
                             **gather_results[1]}}
                result['category'] += gather_results[2]['category']
                result['downloader'] = 'ytd'
                return {**gather_results[2], **result}


@RequestRetry(default_exception_return={},
              default_other_exception_return={})
async def extract_info(vid, sign, client_id, session):
    new_parm = {'vid': vid,
                'ccode': '0512',
                'client_ip': '192.168.1.1',
                'utid': 'lwF+FVFsUk4CAXF3uLWWBhbj',
                'client_ts': str(int(time.time())),
                'r': sign,
                'ckey': 'DIl58SLFxFNndSV1GFNnMQVYkx1PP5tKe1siZu/86PR1u/Wh1Ptd+WOZsHHWxysSfAOhNJpdVWsdVJNsfJ8Sxd8WKVvNfAS8aS8fAOzYARzPyPc3JvtnPHjTdKfESTdnuTW6ZPvk2pNDh4uFzotgdMEFkzQ5wZVXl2Pf1/Y6hLK0OnCNxBj3+nb0v72gZ6b0td+WOZsHHWxysSo/0y9D2K42SaB8Y/+aD2K42SaB8Y/+ahU+WOZsHcrxysooUeND',
                'site': '1',
                'wintype': 'BDskin',
                'p': '1',
                'fu': '0',
                'vs': '1.0',
                'rst': 'mp4',
                'dq': 'mp4',
                'os': 'win',
                'osv': '',
                'd': '0',
                'bt': 'pc',
                'aw': 'w',
                'needbf': '1',
                'atm': '',
                'partnerid': client_id,
                'callback': f'youkuPlayer_call_{str(int(time.time() * 1000))}',
                '_t': '08079273092687054'
                }
    headers = {'Host': 'ups.youku.com',
               'Referer': f'https://player.youku.com/embed/XNDIxNTA1MjEwNA==?client_id={client_id}&password=&autoplay=false',
               'User-Agent': choice(UserAgent),
               }
    api = 'https://ups.youku.com/ups/get.json?'
    async with session.get(api, headers=headers, params=new_parm, verify_ssl=False) as response:
        html = await response.text(encoding='utf-8', errors='ignore')
        videodata = json.loads(html.replace(new_parm['callback'], '')[1:-1])
        item = dict()
        item['from'] = "优酷"
        # item['play_addr'] = jmespath.search('data.stream[0].m3u8_url', videodata)
        item['duration'] = jmespath.search('data.video.seconds', videodata)
        item['cover'] = jmespath.search('data.video.logo', videodata)
        item['author'] = jmespath.search('data.uploader.username', videodata)
        item['author_id'] = jmespath.search('data.uploader.uid', videodata)
        item['author_url'] = jmespath.search('data.uploader.homepage', videodata)
        item['author_avatar'] = jmespath.search('data.uploader.avatar.xlarge', videodata)
        item['title'] = jmespath.search('data.video.title', videodata)
        item['category'] = jmespath.search('data.video.subcategories[].name', videodata)
        item['region'] = jmespath.search('data.network.country_code', videodata)
        item['upload_ts'] = jmespath.search('data.ups.ups_ts', videodata)
        try:
            item['height'] = jmespath.search('max_by(data.stream, &size).height', videodata)
            item['width'] = jmespath.search('max_by(data.stream, &size).width', videodata)
            # item['cdn_url'] = jmespath.search('max_by(data.stream, &size).segs[].cdn_url', videodata)
            item['play_addr'] = jmespath.search('max_by(data.stream, &size).segs[].cdn_url', videodata)[0]
        except:
            traceback.print_exc()
            item['height'] = jmespath.search('data.stream[-1].height', videodata)
            item['width'] = jmespath.search('data.stream[-1].width', videodata)
            # item['cdn_url'] = jmespath.search('data.stream[-1].segs[].cdn_url', videodata)
            item['play_addr'] = jmespath.search('data.stream[-1].segs[].cdn_url', videodata)[0]
        return item


@RequestRetry(default_exception_return={},
              default_other_exception_return={})
async def extract_comment_count(vid, session):
    headers = {
        'authority': 'p.comments.youku.com',
        'cache-control': 'max-age=0',
        'upgrade-insecure-requests': '1',
        'user-agent': choice(UserAgent),
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8'}

    params = (
        ('jsoncallback', 'n_commentList'),
        ('app', '100-DDwODVkv'),
        ('objectId', vid),
        ('listType', '0'),
        ('sign', '1bda07104b5c60f24b3ff236d46ee2c5'),
        ('time', '1558691658'),
    )
    api = 'https://p.comments.youku.com/ycp/comment/pc/commentList'
    async with session.get(api, headers=headers, params=params, verify_ssl=False) as response:
        response_text = await response.text()
        response_json = json.loads(response_text[len('  n_commentList('):-1])
        return {'comment_count': jmespath.search('data.totalSize', response_json)}


async def extract_webpage(url, session):
    text = await request_youku_page(url=url, session=session)
    try:
        selector = Selector(text=text)
    except Exception:
        traceback.print_exc()
        return {}
    else:
        category = selector.css('head meta[name*="irCate"]::attr(content)').extract_first()
        category = category.split(',') if category else []
        rating = selector.css('.score').re('<em>(\d)</em>.(\d)</span>')
        tag = selector.css('head meta[name*="keywords"]::attr(content)').extract_first()
        tag = tag.split(',') if tag else None
        description = selector.css('head meta[name*="description"]::attr(content)').extract_first()
        if rating:
            try:
                rating = float('.'.join(rating))
            except Exception:
                traceback.format_exc()
                return {'category': category, "tag": tag, "description": description}
            else:
                return {'category': category, 'rating': rating, "tag": tag, "description": description}
        else:
            return {'category': category, "tag": tag, "description": description}


@RequestRetry
async def request_youku_page(url, session):
    headers = {'authority': 'v.youku.com',
               'cache-control': 'max-age=0',
               'upgrade-insecure-requests': '1',
               'user-agent': choice(UserAgent),
               'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
               'referer': 'https://www.youku.com/',
               'accept-encoding': 'gzip, deflate, br',
               'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8'}
    async with session.get(url, headers=headers) as response:
        response_text = await response.text()
        return response_text


if __name__ == '__main__':
    import aiohttp
    from pprint import pprint

    "https://v.youku.com/v_show/id_XMzg5Mjc5NDExMg==.html?spm=a2h0j.11185381.bpmodule-playpage-segments.5~5~A&&s=1f1b995a017c11df97c0"
    "https://v.youku.com/v_show/id_XNDIyMTIwMjc2MA==.html?spm=a2ha1.12675304.m_2556_c_8261.d_2&s=5b4e34d331864a6d89dc&scm=20140719.manual.2556.show_5b4e34d331864a6d89dc"
    "https://v.youku.com/v_show/id_XNDEyNDE5MzYyOA==.html?spm=a2ha1.12675304.m_2559_c_8263.d_1&scm=20140719.manual.2559.video_XNDEyNDE5MzYyOA%3D%3D"
    "https://v.youku.com/v_show/id_XMzIzNTkyNzYyOA==.html?spm=a2ha1.12675304.m_2561_c_8264.d_1&s=efbfbd043420efbfbdef&scm=20140719.rcmd.2561.show_efbfbd043420efbfbdef"
    "https://v.youku.com/v_show/id_XNDI0MTQ4MzIwMA==.html?spm=a2ha1.12675304.m_5497_c_27681.d_1&scm=20140719.manual.5497.video_XNDI0MTQ4MzIwMA%3D%3D"
    "https://v.youku.com/v_show/id_XMTcxNTA2OTEwNA==.html?spm=a2ha1.12528442.m_4424_c_11054_4.d_5&s=cb4582f4f72011e5a080&scm=20140719.rcmd.4424.show_cb4582f4f72011e5a080"
    "https://v.youku.com/v_show/id_XNDI0ODk0ODUzNg==.html?spm=a2ha1.12675304.m_2556_c_8261.d_1&s=de83005bc0ba4a9284b3&scm=20140719.manual.2556.show_de83005bc0ba4a9284b3"
    "https://v.youku.com/v_show/id_XNDEyNDE5NzQ1Mg==.html?spm=a2ha1.12675304.m_2559_c_8263.d_1&scm=20140719.manual.2559.video_XNDEyNDE5NzQ1Mg%3D%3D"


    async def test():
        async with aiohttp.ClientSession() as session_:
            return await entrance(
                webpage_url="https://v.youku.com/v_show/id_XNDEyNDE5NzQ1Mg==.html?spm=a2ha1.12675304.m_2559_c_8263.d_1&scm=20140719.manual.2559.video_XNDEyNDE5NzQ1Mg%3D%3D",
                session=session_)


    loop = asyncio.get_event_loop()
    pprint(loop.run_until_complete(test()))
