# -*- coding: utf-8 -*-
import scrapy
from quotes.items import QqItem


class QqSpider(scrapy.Spider):
    name = 'qq'#独一无二
    # allowed_domains = ['www.baidu.com']
    start_urls = ['http://quotes.toscrape.com/']#初始请求对应的url

    def parse(self, response):
        quotes = response.css('.quote')
        for quote in quotes:
            item = QqItem()
            item['text']=quote.css('.text::text').extract_first()#名言
            item['author']=quote.css('.author::text').extract_first()#作者
            item['tags']=quote.css('.tags .tag::text').extract()#标签
            yield item

        #翻页
        base_url = response.xpath('//li[@class="next"]/a/@href').extract_first()
        page_url = response.urljoin(base_url)
        yield scrapy.Request(url=page_url,callback=self.parse)
