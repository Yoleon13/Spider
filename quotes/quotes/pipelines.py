# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

from scrapy.exceptions import DropItem
import pymongo

class QuotesPipeline(object):
    def process_item(self, item, spider):
        return item

#实现针对名言截取前面50个字符
class TextPipeline(object):
    def __init__(self):
        self.limit =50
    #处理item的函数
    def process_item(self,item,spider):
        if item:
            if len(item['text']) > self.limit:
                item['text'] = item['text'][:self.limit].strip()+'...'
            return item
        else:
            raise DropItem('没有数据1！！！！')

#保存到数据库
class Mongopipeline(object):
    #初始化
    def __init__(self,mongo_url,mongo_db):
        self.mongo_url=mongo_url
        self.mongo_db = mongo_db

    #从settings里面获取初始的参数
    @classmethod
    def from_crawler(cls,crawler):
        return cls(
            mongo_url=crawler.settings.get('MONGO_URL'),
            mongo_db=crawler.settings.get('MONGO_DB')
        )
    #开启spider时，启用该函数，完成数据库的连接和指明对应的额数据库
    def open_spider(self,spider):
        self.client = pymongo.MongoClient(self.mongo_url)
        self.db = self.client[self.mongo_db]
    #关闭spider时，启动该函数：关闭数据库
    def close_spider(self,spider):
        self.client.close()
    #处理item的函数，将数据存入数据库
    def process_item(self,item,spider):
        name = item.__class__.__name__
        self.db[name].insert(dict(item))
        return item


