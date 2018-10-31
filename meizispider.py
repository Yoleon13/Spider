import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import os
import time

ua = UserAgent()

#获得包含许多妹子图片的主体的url函数
def get_info_url(url):
    info_urls = []
    html=requests.get(url).content.decode('utf-8')#对首页进行请求
    soup = BeautifulSoup(html,'html.parser')
    results = soup.select('.pic ul li > a')#定位到包含url位置
    for result in results:
        info_urls.append(result.attrs['href'])#获得url
    return info_urls

#对获得图片链接，并进行保存的函数
def get_img_url(info_urls,url):
    for info_url in info_urls:
        #进行请求，并获得页码信息
        html=requests.get(info_url).text
        soup = BeautifulSoup(html,'html.parser')
        for i in range(1,int(soup.select('#page a')[-2].string)+1):#对页码进行循环
            page_url = info_url+'/'+str(i)#每页包含图片的url
            html = requests.get(page_url).text#进行请求
            soup1 = BeautifulSoup(html,'html.parser')
            img_url=soup1.select('#content a img')[0].attrs['src']#获得图片链接
            img_name=img_url.split('/')[-2]+'_'+img_url.split('/')[-1]#图片的名字，保证独一无二
            #因为涉及到重定向，需要构建请求头**重要**
            headers ={
                'User-Agent':ua.random,
                'Referer':page_url
            }
            img=requests.get(img_url,headers=headers,allow_redirects=False).content#获得图片的二进制流
            time.sleep(1)
            #进行保存
            with open('xxoo/'+img_name,'wb') as f:
                f.write(img)

#主体函数
def main():
    if not os.path.exists('xxoo'):
        os.mkdir('xxoo')
    url = 'http://www.mmjpg.com/tag/xinggan'
    info_urls=get_info_url(url)#获得按钮下面的链接
    get_img_url(info_urls)#获得图片链接，并进行请求，最后保存图片

if __name__=='__main__':
    main()