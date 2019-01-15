# -*- coding: utf-8 -*-
import json
import os
from http.cookiejar import LWPCookieJar
import requests
import scrapy
from selenium import webdriver
from scrapy.http import Request
from urllib import parse
import re
from spider.items import item_loader
from spider import items
import logging

current_path = os.path.dirname(__file__)
parent_path = os.path.abspath('..')
path = os.path.join(os.path.abspath(".."),"data")
session = requests.session()
session.cookies = LWPCookieJar(filename='cookies.txt')

class ZhihuSpider(scrapy.Spider):
    name = 'zhihu'
    allowed_domains = ['www.zhihu.com']
    start_urls = ['https://www.zhihu.com/']
    start_answer_url= "https://www.zhihu.com/api/v4/questions/{0}/answers?include=data%5B%2A%5D.is_normal%2Cadmin_closed_comment%2Creward_info%2Cis_collapsed%2Cannotation_action%2Cannotation_detail%2Ccollapse_reason%2Cis_sticky%2Ccollapsed_by%2Csuggest_edit%2Ccomment_count%2Ccan_comment%2Ccontent%2Ceditable_content%2Cvoteup_count%2Creshipment_settings%2Ccomment_permission%2Ccreated_time%2Cupdated_time%2Creview_info%2Crelevant_info%2Cquestion%2Cexcerpt%2Crelationship.is_authorized%2Cis_author%2Cvoting%2Cis_thanked%2Cis_nothelp%2Cis_labeled%3Bdata%5B%2A%5D.mark_infos%5B%2A%5D.url%3Bdata%5B%2A%5D.author.follower_count%2Cbadge%5B%2A%5D.topics&limit={1}&offset={2}&platform=desktop&sort_by=default"
    start_question_url = "https://www.zhihu.com/api/v3/feed/topstory/recommend?session_token=1e6b57298597662e3259f0bac110fa03&desktop=true&page_number=2&limit=6&action=down&after_id=5"

    def __init__(self):
        self.agent = "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36"
        try:
            self.Cookie = self.load_cookie_dict()
        except Exception:
            self.get_cookie()
            self.Cookie=self.load_cookie_dict()
        self.header = {
            "Host":"www.zhihu.com",
            "Referer":"https://www.zhihu.com",
            "User-Agent":self.agent
        }
    def start_requests(self):
        yield Request("https://www.zhihu.com",headers=self.header,cookies=self.Cookie,callback=self.parse)

    def parse(self, response):
        next_page = re.search(r'.*(\"next\":\"https:.*)(session_token.*after_id=\d+)(\").*', response.text)
        next_page_url = "https://www.zhihu.com/api/v3/feed/topstory/recommend?"+next_page.group(2)
        print(next_page_url)
        urls = response.css('a[data-za-detail-view-element_name]::attr(href)').extract()
        print(urls)
        for url in urls:
            url = parse.urljoin(response.url,url)
            re_url = re.match(r'(.*question/(\d+))(.*answer/\d+)', url)
            if re_url:
                url = re_url.group(1)
                question_id = re_url.group(2)
                yield Request(url=url,headers=self.header,callback=self.parse_question)
        #下一页
        #yield Request(url=next_page_url,headers=self.header)


    def parse_question(self,response):
        question_loader = item_loader(item=items.ZhihuQuestionItem(),response=response)
        question_id = re.match(r'.*/(\d+).*',response.url).group(1)
        question_loader.add_value('id',question_id)
        question_loader.add_css('title','h1.QuestionHeader-title::text')
        question_loader.add_css('topics','.TopicLink div.Popover ::text')
        question_loader.add_css('content','span.RichText ztext[itemprop]::text')
        question_loader.add_css('answer_num','h4.List-headerText span::text')
        question_loader.add_value('url',response.url)
        question_loader.add_css('follower_num','button.Button.NumberBoard-item.Button--plain strong::attr(title)')
        question_loader.add_css('scan_num','div.NumberBoard-item strong::attr(title)')
        question_item = question_loader.load_item()
        yield Request(url = self.start_answer_url.format(question_id,5,0),headers=self.header,callback=self.parse_answer)
        logging.info("question_item:",question_item)
        yield question_item

    def parse_answer(self,response):
        answer_response = json.loads(response.text)
        totals = answer_response['paging']['totals']
        next = answer_response['paging']['next']
        data = answer_response['data']
        for answer in data:
            answer_item = items.ZhihuAnswerItem()
            answer_item['id'] = answer['id']
            answer_item['author_id'] = answer['author']['id'] if "id" in answer['author'] else None
            answer_item['question_id'] = answer['question']['id'] if "id" in answer['question'] else None
            answer_item['url'] = answer['url']
            answer_item['content'] = answer['content'] if 'content' in answer else None
            answer_item['comment_count'] = answer['comment_count']
            answer_item['voteup_count'] = answer['voteup_count']
            yield answer_item
        if not answer_response['paging']['is_end']:
            yield Request(url = next,headers=self.header,callback=self.parse_answer)
        pass

    def login(self):
        self.header['Cookie'] =self.Cookie
        r = session.get("https://www.zhihu.com/inbox",headers = self.header,allow_redirects = False)
        if r.status_code!=200:
            print("cookie过期，重新登录")
            self.get_cookie()
            self.header['Cookie'] = self.load_cookie()
            r = session.get("https://www.zhihu.com",headers = self.header)
        print(r)

    def get_cookie(self):
        browser = webdriver.Chrome()
        browser.get("https://www.zhihu.com/signin")
        browser.find_element_by_name("username").send_keys("18614023195")
        browser.find_element_by_name("password").send_keys("123456abc")

        #登录以后再按回车
        input("扫码登录以后按回车:")
        cookies = browser.get_cookies()
        cookies_json = json.dumps(cookies)
        with open('cookies.json','w') as f:
            f.write(cookies_json)
        browser.close()


    def load_cookie(self):
        with open('cookies.json','r',encoding='utf-8') as f:
            cookies_json = json.loads(f.read())
        cookies = [item['name']+"="+item['value'] for item in cookies_json]
        cookies = ';'.join(cookie for cookie in cookies)
        return cookies

    def load_cookie_dict(self):
        with open('cookies.json','r',encoding='utf-8') as f:
            cookies_json = json.loads(f.read())
        return cookies_json

