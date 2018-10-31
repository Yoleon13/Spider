from urllib import request
from urllib import parse
import json
from math import ceil
import pymongo
import time

KEYWORD = '机器学习'#搜索关键字
CITY = '深圳'#搜索的城市

MONGODB_URL = 'localhost'#数据所在的位置
MONGODB_DB = 'Lagou'#数据库的名字
MONGODB_NAME = KEYWORD#collection的名字

client = pymongo.MongoClient(host=MONGODB_URL,port=27017)#连接数据库，创建客户端
db = client[MONGODB_DB]#指明到对应数据库，如果该数据库不存在，则创建

#保存到数据库的函数
def save_info_mongo(info):
    if db[MONGODB_NAME].insert(info):#保存数据，并判断是否保存成功
        print('保存成功：',info)
    else:
        print('保存失败:',info)

#请求函数
def get_response(url,pn=1):
    #请求体
    data = {
        'first': 'true',
        'pn': pn,
        'kd': KEYWORD
    }
    data = bytes(parse.urlencode(data),encoding='utf-8')
    #请求头
    headers ={
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Connection': 'keep-alive',
        'Content-Length': 55,
        'Cookie': 'user_trace_token=20180507142833-3f6332a8-307d-45d6-9aba-303973fa79bb; _ga=GA1.2.1059277566.1525674496; LGUID=20180507142833-dddd64b2-51bf-11e8-8ff7-525400f775ce; _gid=GA1.2.1501567499.1540776584; index_location_city=%E6%B7%B1%E5%9C%B3; JSESSIONID=ABAAABAAAGGABCB1D722FAF7530C73EB3AA533A24B69DD3; Hm_lvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1540776583,1540861866; TG-TRACK-CODE=search_code; SEARCH_ID=c61a74c76d7e4be6a36908790cd7b161; _gat=1; Hm_lpvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1540866156; LGSID=20181030102238-abd488b2-dbea-11e8-b6d4-525400f775ce; PRE_UTM=; PRE_HOST=; PRE_SITE=; PRE_LAND=https%3A%2F%2Fwww.lagou.com%2Fjobs%2Flist_%25E6%2595%25B0%25E6%258D%25AE%25E5%2588%2586%25E6%259E%2590%3Fpx%3Ddefault%26city%3D%25E6%25B7%25B1%25E5%259C%25B3; LGRID=20181030102238-abd48a54-dbea-11e8-b6d4-525400f775ce',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Referer': 'https://www.lagou.com/jobs/list_'+parse.quote(KEYWORD)+'?px=default&city='+parse.quote(CITY),
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'
    }
    _request=request.Request(url,data=data,headers=headers)#构建Request对象
    response = request.urlopen(_request).read().decode('utf-8')#进行请求并获得响应体
    time.sleep(5)#休眠5秒，避免太过频繁的请求
    return response

#获取岗位页数的函数
def get_page(url):
    response = get_response(url)#请求得到响应
    results = json.loads(response)#将json字符串转化为字典形式
    pageSize=results['content']['pageSize']
    totalCount=results['content']['positionResult']['totalCount']
    page = ceil(totalCount/pageSize)#计算得到页数
    return page

#获取岗位信息的函数
def get_info(url,i):
    response = get_response(url,i)#请求得到响应
    comment = json.loads(response)#将json字符串转化为字典形式
    results = comment['content']['positionResult']['result']#岗位信息所在的位置
    for result in results:
        position ={
            'city':result['city'],#城市
            'companyFullName':result['companyFullName'],#公司全称
            'education':result['education'],#所需学历
            'industryField':result['industryField'],#行业
            'jobNature':result['jobNature'],#岗位类型
            'positionName':result['positionName'],#岗位的名称
            'salary':result['salary'],#薪酬
            'workYear':result['workYear']#工作经验
        }
        save_info_mongo(position)#保存到数据库


#主体函数
def main():
    #目标url
    url = 'https://www.lagou.com/jobs/positionAjax.json?px=default&city='+parse.quote(CITY)+'&needAddtionalResult=false'
    page = get_page(url)#获取对应岗位的页数
    for i in range(1,page+1):#进行翻页
        get_info(url,i)#获取招聘信息

if __name__=='__main__':
    main()