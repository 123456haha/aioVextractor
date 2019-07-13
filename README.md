# aioVextractor
Extractor video info asynchronously


##### TEST_CASE：

1. 'https://www.bilibili.com/video/av5546345?spm_id_from=333.334.b_62696c695f646f756761.4'
2. '#在抖音，记录美好生活#球球老婆怀孕之后就爱睡这个洗脸巢睡姿也太可爱了8#猫http://v.douyin.com/hd9sb3/复制此链接，打开【抖音短视频】，直接观看视频！'
3. 'http://v.douyin.com/hd9sb3/'
4. 'https://www.eyepetizer.net/detail.html?vid=119611&utm_campaign=routine&utm_medium=share&utm_source=others&uid=0&resourceType=video&udid=1bb9f2f14545490c9168f7b99d89136e8ff14724&vc=443&vn=4.9.1&size=1080X1920&deviceModel=vivo%20X9&first_channel=eyepetizer_vivo_market&last_channel=eyepetizer_vivo_market&system_version_code=25'
5. 'https://v.qq.com/x/page/s0886ag14xn.html'
6. 'https://v.qq.com/x/cover/bzfkv5se8qaqel2.html'
7. 'http://www.tvcf.co.kr/YCf/V.asp?Code=A000363280'
8. 'https://play.tvcf.co.kr/750556'
9. 'https://vimeo.com/281493330'
10. 'https://www.xinpianchang.com/a10475334?from=ArticleList'
11. 'https://v.youku.com/v_show/id_XMzg5Mjc5NDExMg==.html?spm=a2h0j.11185381.bpmodule-playpage-segments.5~5~A&&s=1f1b995a017c11df97c0'
12. 'https://www.youtube.com/watch?v=tofSaLB9kwE'

###### 测试Demo
```python
from aioVextractor.extract import extract
import aiohttp
import asyncio
from pprint import pprint
async def test():
    async with aiohttp.ClientSession() as session:
        return await extract('http://v.douyin.com/hd9sb3/', session)
res = asyncio.run(test())
print(res)
```



PLAYLIST_TEST_CASE：
1. 'https://vimeo.com/alitasmitmedia'
3. 'https://www.youtube.com/playlist?list=PLohYzz4btpaSt2T0rcfmF8wfQzuW_6JTv'
4. 'https://www.youtube.com/channel/UC36FGmBEGfmOV2T5QVNI9ew'
5. 'https://www.xinpianchang.com/u10539256?from=userList'


###### 测试Demo
```python
from aioVextractor.breakdown import breakdown
import asyncio
from pprint import pprint
async def test():
    result = [ele async for ele in breakdown('https://vimeo.com/alitasmitmedia')]
    return result
res = asyncio.run(test())
pprint(res)
```