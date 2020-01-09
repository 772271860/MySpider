import requests
import re
import json
import time
import os
from multiprocessing import Pool


headers = {
    'accept': 'application/json, text/javascript',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'zh-CN,zh;q=0.9',
    'content-type': 'application/x-www-form-urlencoded',
    'cookie': 'tt_webid=6778000217683674637; csrftoken=cbfe67ef0e54c07f9c202e8d2ce67b63; tt_webid=6778000217683674637; sessionid=89747365b90fc1a0ef9e35492084258f; sid_tt=89747365b90fc1a0ef9e35492084258f; uid_tt=1e4ea0da52f152508348fb898e3874f6; sid_guard=89747365b90fc1a0ef9e35492084258f%7C1578128343%7C5184000%7CWed%2C+04-Mar-2020+08%3A59%3A03+GMT; toutiao_sso_user=1e4566965a502d0ef16db7e419c3ee7c; sso_uid_tt=ff4fc3f7f0f4b6b6fcbc0a6175cf52b9; WEATHER_CITY=%E5%8C%97%E4%BA%AC; __tasessionId=ivejvhxf11578137503782; s_v_web_id=8b36daa788b788dd3ec946c2dd078fec; _ga=GA1.2.178959084.1578128537',
    'referer': 'https://www.toutiao.com/search/?keyword=%E8%A1%97%E6%8B%8D',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
    'x-requested-with': 'XMLHttpRequest'
}
base_url = 'https://www.toutiao.com/api/search/content/?'


def get_page_index(base_url, offset, keyword, timestamp): 
    """通过自己构建data来获取需要的ajax请求后的网页"""
    data = {   #构造data把要请求的参数在网页的请求参数里复制过来
        'aid': '24',
        'app_name': 'web_search',
        'offset': offset,
        'format': 'json',
        'keyword': keyword,
        'autoload': 'true',
        'count': '20',
        'en_qc': '1',
        'cur_tab': '1',
        'from': 'search_tab',
        'pd': 'synthesis',
        'timestamp': timestamp #时间戳，现在的今日头条的url最后会有一个13位的时间戳
    }
    try:
        response = requests.get(base_url, params=data, headers=headers)
        if response.status_code == 200:
            return response.json()
        return("debug1")
    except Exception:
        return('debug2')


def parse_page_index(html):
    """article_url , has_gallery --> yield"""
    if 'data' in html:
        for item in html.get('data'):
            if 'article_url' in item:
                yield{
                    'article_url':item.get('article_url'),
                    'has_gallery':item.get('has_gallery'),
                    'id':item.get('id')
                }


def get_detail_page(url, has_gallery):
    response = requests.get(url, headers=headers)
    try:
        if response.status_code == 200:
            html = response.text
            if has_gallery:         #处理has_gallery为True的网页源码
                con = re.search(r'gallery: JSON.parse\(([\s\S]*?)\)', response.text).group(1)
                con2 = json.loads(con)
                con3 = json.loads(con2)  #不知道为什么第一次返回loads之后还是str所以loads两次
                a = con3['sub_images']
                for i in range(len(a)):
                    yield(a[i]['url'])    #获取到每张图片的url
            else:           #处理has_gallery为Fasle的网页源码)
                #html / text都没有问题，应该是正则表达式的问题
                text = re.search(r'articleInfo: {[\s\S]*?(content: [\s\S]*?).slice', html).group(1)
                img_li = re.findall(r"img src&#x3D;\\&quot;([\s\S]*?)\\&quot", text)
                #得到像这样的结果http:\u002F\u002Fp9.pstatp.com\u002Flarge\u002Fpgc-image\u002Fd22aba0d85b7482cb46632b49d4ec890
                #其中的\u002F代表的是斜杠 /
                for img in img_li:
                    img_url = img.replace("\\u002F", "/")
                    yield(img_url)
        else:
            return('else')
    except:
        return("except")


def save_img(url, id, name):
    try:
        img_source = requests.get(url, headers=headers)
        if img_source.status_code == 200:
            if not os.path.exists('./toutiao_imgs/' + '/' + str(id)):
                os.makedirs('./toutiao_imgs/' + str(id))
            with open('./toutiao_imgs/' + str(id) + '/' + str(name) + '.jpg', 'wb')as f:
                for chunk in img_source.iter_content(chunk_size=2048):
                    f.write(chunk)
            print(str(name) + 'finished')
        return("debug3")
    except:
        print('failed')


def main(offset):
    timestamp = int(time.time()*100)
    keyword = "街拍"
    html = get_page_index(base_url, offset, keyword, timestamp)
    name = 0
    for item in parse_page_index(html):
        url = item.get('article_url')
        has_gallery = item.get('has_gallery')
        id = item.get('id')
        # print(get_detail_page(url, has_gallery))
        for url in get_detail_page(url, has_gallery):
            name += 1
            save_img(url, id, name)


if __name__ == "__main__":
    main(0)
    # offset = [20*i for i in range(5)]
    # pool = Pool()
    # pool.map(main, offset)