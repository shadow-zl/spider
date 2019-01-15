# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Item
import scrapy
import datetime
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose,TakeFirst,Join
import re
#点赞，评论处理
def num_processor(num):
    if re.match(r'.*?(\d+).*',num):
        num = int(re.match(r'.*?(\d+).*',num).group(1))
    else:
        num=0
    return num
    pass
#标签处理
def tags_processor(tag):
    if "评论" in tag:
        return ""
    else:
        return tag
    pass

def return_value(value):
    return value

def date_processor(date):
    try:
        date = datetime.strptime(date,"%Y/%m/%d").date()
    except Exception as e:
        date = datetime.datetime.now().date()
    return date

#自定义item_loader
class item_loader(ItemLoader):
    default_output_processor = TakeFirst()
    pass

class AriticleItem(scrapy.Item):
    url_md5 = scrapy.Field()
    title = scrapy.Field()
    comment = scrapy.Field(input_processor =MapCompose(num_processor))
    date  =scrapy.Field(input_processor=MapCompose(date_processor))
    tags = scrapy.Field(input_processor=MapCompose(tags_processor),output_processor =Join(","))
    praise = scrapy.Field()
    store = scrapy.Field(input_processor =MapCompose(num_processor))
    article = scrapy.Field()
    #img_url = scrapy.Field(input_processor = MapCompose(img_url_processor))
    img_url = scrapy.Field()
    url = scrapy.Field()
    img_path = scrapy.Field()

    def sql(self):
        sql = "insert into scrapy(title,url_md5,url,date,tags,img_url,praise,store,comment) values(%s,%s,%s,%s,%s,%s,%s,%s,%s) "
        params = (self['title'],self['url_md5'],self['url'],self['date'],self['tags'],self['img_url'],self['praise'],self['store'],self['comment'])
        return sql,params


def answer_process(answer_num):
    if ',' in answer_num:
        return answer_num.replace(',','')
    else:
        return answer_num


class ZhihuQuestionItem(Item):
    id = scrapy.Field()
    topics = scrapy.Field(output_processor = Join(','))
    url = scrapy.Field()
    title = scrapy.Field()
    answer_num = scrapy.Field(input_processor =MapCompose(answer_process))
    follower_num = scrapy.Field()
    scan_num = scrapy.Field()
    content = scrapy.Field()
    def sql(self):
        sql = "insert into zhihu(id,topics,url,title,answer_num,follower_num,scan_num) values(%s,%s,%s,%s,%s,%s,%s) "
        params = (self['id'],self['topics'],self['url'],self['title'],self['answer_num'],self['follower_num'],self['scan_num'])
        return sql,params
    pass

class ZhihuAnswerItem(Item):
    id = scrapy.Field()
    author_id = scrapy.Field()
    question_id = scrapy.Field()
    url = scrapy.Field()
    content = scrapy.Field()
    voteup_count = scrapy.Field()
    comment_count = scrapy.Field()
    def sql(self):
        sql = "insert into zhihu_answer(id,author_id,question_id,url,content,voteup_count,comment_count) values(%s,%s,%s,%s,%s,%s,%s) "
        params = (self['id'],self['author_id'],self['question_id'],self['url'],self['content'],self['voteup_count'],self['comment_count'])
        return sql,params
    pass