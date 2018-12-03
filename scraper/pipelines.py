# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymysql as pymysql
from twisted.enterprise import adbapi

from sqlalchemy.orm import sessionmaker
from .models import Article, db_connect, create_table


class ScraperPipeline(object):
    def process_item(self, item, spider):
        return item


class ArticlePipeline(object):
    def __init__(self):
        """
        Initializes database connection and sessionmaker.
        Creates deals table.
        """
        engine = db_connect()
        create_table(engine)
        self.Session = sessionmaker(bind=engine)

    def process_item(self, item, spider):
        """
        Save deals in the database.
        This method is called for every item pipeline component.
        """
        session = self.Session()
        article = Article()
        article.title = item["title"]
        article.content = item['content']
        article.url = item['url']
        article.type = item['type']

        try:
            session.add(article)
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()

        return item


# # 保存到数据库的方法
# class ArticlePipeline(object):
#
#     # 这个是类方法而不是实例方法
#     @classmethod
#     def from_settings(cls, settings):
#         dbparams = dict(
#             host=settings['MYSQL_HOST'],
#             db=settings['MYSQL_DBNAME'],
#             user=settings['MYSQL_USER'],
#             passwd=settings['MYSQL_PASSWD'],
#             charset='utf8',
#             cursorclass=pymysql.cursors.DictCursor,
#             use_unicode=False
#         )
#
#         dbpool = adbapi.ConnectionPool('pymysql', **dbparams)
#         return cls(dbpool)
#
#     # 得到连接池
#     def __init__(self, dbpool):
#         self.dbpool = dbpool
#
#     # pipeline默认调用
#     def process_item(self, item, spider):
#         query = self.dbpool.runInteraction(self._conditional_insert, item)  # 调用插入的方法
#         query.addErrback(self._handle_error, item, spider)  # 调用异常处理方法
#         return item
#
#     # 写入数据库中
#     def _conditional_insert(self, tx, item):
#         sql = "insert into " + item["table_name"] + " (title,content,url,type) values(%s,%s,%s,%s)"
#         params = (item["title"], item["content"], item["url"], item["type"])
#         tx.execute(sql, params)
#
#     # 错误处理方法
#     def _handle_error(self, failue, item, spider):
#         print('--------------database operation exception!!-----------------')
#         print('-------------------------------------------------------------')
#         print(failue)
