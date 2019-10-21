#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 2019/6/20
# IDE: PyCharm

from aioVextractor.player import youku
from aioVextractor.extractor.base_extractor import (
    BaseExtractor,
    validate,
    RequestRetry
)


class Extractor(BaseExtractor):
    target_website = [
        "http[s]?://v\.youku\.com/v_show/id_\w{10,36}",
    ]

    TEST_CASE = [
        "https://v.youku.com/v_show/id_XMzg5Mjc5NDExMg==.html?spm=a2h0j.11185381.bpmodule-playpage-segments.5~5~A&&s=1f1b995a017c11df97c0",
        "https://v.youku.com/v_show/id_XNDIyMTIwMjc2MA==.html?spm=a2ha1.12675304.m_2556_c_8261.d_2&s=5b4e34d331864a6d89dc&scm=20140719.manual.2556.show_5b4e34d331864a6d89dc",
        "https://v.youku.com/v_show/id_XNDEyNDE5MzYyOA==.html?spm=a2ha1.12675304.m_2559_c_8263.d_1&scm=20140719.manual.2559.video_XNDEyNDE5MzYyOA%3D%3D",
        "https://v.youku.com/v_show/id_XMzIzNTkyNzYyOA==.html?spm=a2ha1.12675304.m_2561_c_8264.d_1&s=efbfbd043420efbfbdef&scm=20140719.rcmd.2561.show_efbfbd043420efbfbdef",
        "https://v.youku.com/v_show/id_XNDI0MTQ4MzIwMA==.html?spm=a2ha1.12675304.m_5497_c_27681.d_1&scm=20140719.manual.5497.video_XNDI0MTQ4MzIwMA%3D%3D",
        "https://v.youku.com/v_show/id_XMTcxNTA2OTEwNA==.html?spm=a2ha1.12528442.m_4424_c_11054_4.d_5&s=cb4582f4f72011e5a080&scm=20140719.rcmd.4424.show_cb4582f4f72011e5a080",
        "https://v.youku.com/v_show/id_XNDI0ODk0ODUzNg==.html?spm=a2ha1.12675304.m_2556_c_8261.d_1&s=de83005bc0ba4a9284b3&scm=20140719.manual.2556.show_de83005bc0ba4a9284b3",
        "https://v.youku.com/v_show/id_XNDEyNDE5NzQ1Mg==.html?spm=a2ha1.12675304.m_2559_c_8263.d_1&scm=20140719.manual.2559.video_XNDEyNDE5NzQ1Mg%3D%3D",
    ]

    def __init__(self, *args, **kwargs):
        BaseExtractor.__init__(self, *args, **kwargs)
        self.from_ = "youku"

    @validate
    @RequestRetry
    async def entrance(self, webpage_url, session):
        return await youku.entrance(iframe_url=webpage_url, session=session)


if __name__ == '__main__':
    from pprint import pprint

    with Extractor() as extractor:
        res = extractor.sync_entrance(webpage_url="https://v.youku.com/v_show/id_XNDEyNDE5NzQ1Mg")
        pprint(res)
