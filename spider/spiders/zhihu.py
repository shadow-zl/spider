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

current_path = os.path.dirname(__file__)
parent_path = os.path.abspath('..')
path = os.path.join(os.path.abspath(".."),"data")
session = requests.session()
session.cookies = LWPCookieJar(filename='cookies.txt')

class ZhihuSpider(scrapy.Spider):
    name = 'zhihu'
    allowed_domains = ['www.zhihu.com']
    start_urls = ['https://www.zhihu.com/']

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
        yield Request("https://www.zhihu.com/",headers=self.header,cookies=self.Cookie,callback=self.parse)

    def parse(self, response):
        urls = response.css('a[data-za-detail-view-element_name]::attr(href)').extract()
        for url in urls:
            url = parse.urljoin(response.url,url)
            re_url = re.match(r'(.*question/(\d+))(.*answer/\d+)', url)
            if re_url:
                url = re_url.group(1)
                question_id = re_url.group(2)
                yield Request(url=url,headers=self.header,callback=self.parse_detail)
            pass

    def parse_detail(self,response):
        question_loader = item_loader(item=items.ZhihuQuestionItem(),response=response)
        # answer_loader = item_loader(item=items.ZhihuAnswerItem(),response=response)
        question_loader.add_value('id',re.match(r'.*/(\d+).*',response.url).group(1))
        question_loader.add_css('title','h1.QuestionHeader-title::text')
        question_loader.add_css('topics','.TopicLink div.Popover ::text')
        question_loader.add_css('content','span.RichText ztext[itemprop]::text')
        question_loader.add_css('answer_num','h4.List-headerText span::text')
        question_loader.add_value('url',response.url)
        question_loader.add_css('follower_num','button.Button.NumberBoard-item.Button--plain strong::attr(title)')
        question_loader.add_css('scan_num','div.NumberBoard-item strong::attr(title)')
        item = question_loader.load_item()
        yield item

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

