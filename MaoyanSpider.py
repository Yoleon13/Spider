import requests
import re
import pymongo
import time

MONGO_URL = 'localhost'
MONGO_DB = 'MOVIES'
MONGO_COLLECTION = 'Maoyan'

client = pymongo.MongoClient(host=MONGO_URL,port=27017)
db = client[MONGO_DB]

def save_to_mongo(info):
    if db[MONGO_COLLECTION].update({'name':info['name']},{'$set':info},True):
        print('保存成功',info)
    else:
        print('保存失败',info)

#请求函数
def get_response(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'
    }
    response = requests.get(url,headers=headers).text#请求，获得响应
    time.sleep(1)
    return response

#提取信息函数
def get_info(html):
    #正则模式
    pattern=re.compile(r'<dd>.*?class="name".*?title="(.*?)".*?class="star">(.*?)</p>.*?"releasetime">'
                       r'(.*?)</p>.*?"integer">(.*?)</i>.*?"fraction">(.*?)</i>',re.S)
    #正则提取信息
    results = re.findall(pattern,html)
    for result in results:
        movie = {
            'name':result[0],#电影名
            'actor':result[1].strip()[3:],#主演
            'releasetime':result[2].strip()[5:],#上映时间
            'score':result[3]+result[4]#分数

        }
        save_to_mongo(movie)#保存

#主体程序
def main():
    #进行翻页
    for page in range(10):
        url = 'http://maoyan.com/board/4?offset='+str(page*10)#url
        html = get_response(url)#获得响应
        get_info(html)#提取信息，并进行保存

if __name__=='__main__':
    main()