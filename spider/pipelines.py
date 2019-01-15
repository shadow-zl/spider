# -*- coding: utf-8 -*-

from scrapy.pipelines.images import ImagesPipeline
import codecs
import json
import MySQLdb
from scrapy.exporters import JsonItemExporter
from twisted.enterprise import adbapi
from MySQLdb.cursors import DictCursor



class ArticlePipeline(object):
    def process_item(self, item, spider):
        return item

class ImagePipeline(ImagesPipeline):
    def item_completed(self, results, item, info):
        for k,v in results:
            img_path = v['path']
        item['img_path'] = img_path
        return item

class JsonPipeline(object):
    def __init__(self):
        self.file = codecs.open('article.json','w',encoding='utf-8')
    def process_item(self, item, spider):
        line = json.dumps(dict(item),ensure_ascii=False)+"\n"
        self.file.write(line)
        return item
    def spider_closed(self,spider):
        self.file.close()

class JsonItemExporterPipeline():
    def __init__(self):
        self.file = open('article.json','wb')
        self.exporter = JsonItemExporter(self.file,encoding = "utf-8",ensure_ascii = False)
        self.exporter.start_exporting()

    def close_spider(self,spider):
        self.exporter.finish_exporting()
        self.file.close()

    def process_item(self,item,spider):
        self.exporter.export_item(item)
        return  item

class MysqlPipeline(object):
    def __init__(self):
        self.conn = MySQLdb.connect("192.168.0.190","devdb","waQ,qR%be2","python",charset="utf8",use_unicode=True)
        self.cursor = self.conn.cursor()
    def process_item(self,item,spider):
        sql = "insert into scrapy(title,url_md5,url,date,tags,praise,store,comment,img_url) values(%s,%s,%s,%s,%s,%s,%s,%s,%s) "
        self.cursor.execute(sql,(item['title'],item['url_md5'],item['url'],item['date'],item['tags'],item['praise'],item['store'],item['comment'],item['img_url']))
        self.conn.commit()
        return item


class MysqlAsynPipeline(object):
    def __init__(self,dbpool):
        self.dbpool = dbpool
    @classmethod
    def from_settings(cls,settings):
        params = dict(
            host = settings["MYSQL_HOST"],
            user = settings['MYSQL_USER'],
            passwd = settings['MYSQL_PASSWORD'],
            db = settings['MYSQL_DBNAMW'],
            charset = "utf8",
            cursorclass = DictCursor,
            use_unicode = True
        )
        dbpool = adbapi.ConnectionPool("MySQLdb",**params)
        return cls(dbpool)

    def process_item(self,item,spider):
        interaction = self.dbpool.runInteraction(self.insert, item)
        interaction.addErrback(self.handle_error)

    def handle_error(self,failure):
        print(failure)


    def insert(self,tx,item):
        sql,params = item.sql()
        tx.execute(sql,params)



class ZhiHuPipeline(object):
    def process_item(self, item, spider):
        with open('answer.txt','a',encoding='utf-8') as f:
            f.write((str(item['question_id'])+item['content']))
            f.write("\n")
        return item