# -*- coding: utf-8 -*-
import scrapy
import json
import re
from Jd.items import JdbraItem

#分析网页的主要思路
    #（1）我们主要是为了获取商品的销售数据（评论数据），首先找到商品的销售数据，跟网页呈现的相同
    #（2）找到对应的链接，分析链接里面包含的主要信息：有商品的ID——ProductId、评论数据的页码——page
    #（3）接下来主要考虑不同的商品对应的ID，看网站的URL会发现有ProductID的信息，就可以以此确定通过京东搜索页面，
    #     输入关键字，我们可以基于呈现的页面来分析，可以获取商品的ProductID

#爬虫的主要思路：
    #（1）通过搜索商品关键字，来得到关于商品的页面，点击“销量”进行排序，基于该页面的URL完成，发送请求，获取商品ProductID
    #（2）得到商品ProductID之后，构建评论数据对应的链接，进行请求，获得该商品的评论数据最大页码maxpage
    #（3）得到最大页码之后，可以重新基于商品ProductId和页数page，重新构建评论数据的URL，进行请求，获得每个商品，每页下面的销售数据
    #（4）获得响应进行解析，提取感兴趣的数据，并进行保存。

class JdbraSpider(scrapy.Spider):
    name = 'jdbra'
    # allowed_domains = ['www.jd.com']
    start_urls = ['http://www.jd.com/']
    #初始URL和初始请求
    url ='https://search.jd.com/Search?keyword=%E8%83%B8%E7%BD%A9&enc=utf-8&qrst=1&rt=1&stop=1&vt=2&suggest=2.def.0.V00&wq=xiong&psort=3&click=0'
    def start_requests(self):
        yield scrapy.Request(url=self.url,callback=self.parse_product)

    #解析获得产品id,构建url用来请求获得每个产品下的评论页码数
    def parse_product(self, response):
        #获取产品ID,并用set进行去重
        products=list(set(response.xpath('//li[@class="gl-item"]/@data-sku').extract()))
        #针对每个产品
        for product in products:
            url = 'https://sclub.jd.com/comment/productPageComments.action?callback=fetchJSON_comment98vv3&productId='+product+'&score=0&sortType=5&page=0&pageSize=10&isShadowSku=0&fold=1'
            #请求
            yield scrapy.Request(url=url,callback=self.parse_page,meta={'product':product})
    #解析获取每个产品的评论页数，构建url来请求获得每页的评论
    def parse_page(self, response):
        #将响应体的结果变成类似json的字符串
        js = response.text.replace('fetchJSON_comment98vv3(','').replace(');','')
        comments=json.loads(js)#转化为字典
        page = comments['maxPage']#页码数
        product=response.meta['product']#从请求传过来的productId
        # print(re.search(r'productId=(.*?)&',response.url,re.S).group(1))
        for pn in range(page):
            url = 'https://sclub.jd.com/comment/productPageComments.action?callback=fetchJSON_comment98vv3&productId=' + product + '&score=0&sortType=5&page='+str(pn)+'&pageSize=10&isShadowSku=0&fold=1'
            yield scrapy.Request(url=url,callback=self.parse_comment,dont_filter=True)
    #解析获得每条评论的信息
    def parse_comment(self, response):
        js = response.text.replace('fetchJSON_comment98vv3(', '').replace(');', '')
        results = json.loads(js)
        comments = results['comments']
        for comment in comments:#每页的每条评论
            item = JdbraItem()
            item['content']=comment['content']#评价
            item['id']=comment['id']#id
            item['productColor'] = comment['productColor']#颜色
            item['productSize'] = comment['productSize']#尺寸
            item['referenceName'] = comment['referenceName']#产品描述
            item['userClientShow'] = comment['userClientShow']#客户来源
            yield item