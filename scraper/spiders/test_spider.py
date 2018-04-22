from functools import reduce

import scrapy
from scraper.helpers.dbhelper import dbHelper
from scraper.helpers.rule import Rule


# 测试用的爬虫
class Spider(scrapy.Spider):
    name = "test_spider"

    # 这里放你要爬取的网站的ＵＲＬ
    start_urls = ["http://renjian.163.com", ]

    # 初始化爬虫,先获取爬取规则
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.rule = Rule()
        self.rule.url = self.start_urls[0]
        self.rule.loop_rule = "//h3/a[@class='tit']"
        self.rule.title_rule = "text()"
        self.rule.content_rule = "//div[@id='endText']/p/text()"
        self.rule.type_rule = "null"
        self.rule.url_rule = "@href"
        self.rule.table_name = "renjian"
        self.rule.type = "article_no_content"

        # 请帮我放到数据库
        # dbHelper.setRule(self.rule)

        self.parses = dict(
            article=self.article_parse,
            article_no_content=self.article_no_content_parse,
            picture=self.picture_parse
        )

    # 这里是如何处理你爬取回来的信息
    def parse(self, response):
        # pass
        yield scrapy.Request(self.rule.url, callback=self.parses[self.rule.type])

    # 关于图片的爬取
    def picture_parse(self, response):
        pass

    # 处理内容的parse
    def content_parse(self, response):
        article = response.meta['article']
        url = article.xpath(self.rule.url_rule).extract_first()
        talbe_name = self.rule.table_name
        title = article.xpath(self.rule.title_rule).extract_first()
        type = article.xpath(self.rule.type_rule).extract()
        content = response.xpath(self.rule.content_rule).extract()

        try:
            type = str(reduce(lambda x, y: str(x) + " " + str(y), type))
        except Exception as e:
            print(e)

        try:
            if (url[0] == '/'):
                url = self.start_urls[0] + url
        except Exception as e:
            print(e)

        try:
            content = str(reduce(lambda x, y: str(x) + str(y), content))
        except Exception  as e:
            print(e)

        if not content:
            return

        if len(content) > 800:
            content = content[:800] + "..."

        yield {
            'table_name': str(talbe_name),
            'title': str(title),
            'content': str(content),
            'type': str(type),
            'url': str(url)
        }

    # 内容要去特地查找内容的文章
    def article_no_content_parse(self, response):
        articles = response.xpath(self.rule.loop_rule)

        for article in articles:
            url = article.xpath(self.rule.url_rule).extract_first()

            try:
                if (url[0] == '/'):
                    url = self.start_urls[0] + url
            except Exception as e:
                print(e)

            # content的内容要特地去爬取
            yield scrapy.Request(url, callback=self.content_parse, meta={'article': article})

    # 第一类普通的文章
    def article_parse(self, response):
        articles = response.xpath(self.rule.loop_rule)

        for article in articles:
            url = article.xpath(self.rule.url_rule).extract_first()
            talbe_name = self.rule.table_name
            title = article.xpath(self.rule.title_rule).extract_first()
            content = article.xpath(self.rule.content_rule).extract()
            type = article.xpath(self.rule.type_rule).extract()

            try:
                type = str(reduce(lambda x, y: str(x) + " " + str(y), type))
            except Exception as e:
                print(e)

            try:
                if (url[0] == '/'):
                    url = self.start_urls[0] + url
            except Exception as e:
                print(e)

            try:
                content = str(reduce(lambda x, y: str(x) + str(y), content))

            except Exception as e:
                print(e)

            yield {
                'table_name': str(talbe_name),
                'title': str(title),
                'content': str(content),
                'type': str(type),
                'url': str(url)
            }
