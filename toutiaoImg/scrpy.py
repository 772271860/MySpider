import requests
import json
from requests.exceptions import RequestException
import re

def get_top(start):
    url = "https://movie.douban.com/j/chart/top_list?"
    param = {
        'type': '13',
        'interval_id': '100:90',
        'action' : '',
        'start': start,
        'limit': '20'
    }
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36'
    }
    try:
        response = requests.get(url=url, params=param, headers=headers)
        if response.status_code == 200:
            return response.text
        return None
    except RequestException:
        print('Error')



def write2file(html):
    #json.dumps()将字典转为json格式字符串
    with open('rank.txt','a',encoding='utf-8') as r:
        r.write(html+'\n')
        r.close()
for i in range(1,100,10):
    pattern = re.compile('\{\"rating.*?\}')
    text = pattern.findall(get_top(i))
    list = []
    for item in text:
        dic = json.loads(item)
        str = json.dumps(dic,ensure_ascii=False)
        list.append(str)

    for str in list:
        write2file(str)