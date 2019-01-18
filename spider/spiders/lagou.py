# -*- coding: utf-8 -*-

from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from spider.items import item_loader
from spider import items
from scrapy import Request
from selenium import webdriver
import json
import os
from spider.utils.common import md5

class LagouSpider(CrawlSpider):
    name = 'lagou'
    allowed_domains = ['www.lagou.com']
    start_urls = ['https://www.lagou.com']

    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self.headers = {
            "Host": 'www.lagou.com',
            "Origin": 'https://www.lagou.com',
            "Referer": "https://www.lagou.com/jobs/list_python",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36",
        }
        self.cookie = self.load_cookie()

    def login(self):
        browser = webdriver.Chrome("E:\\chromedriver.exe")
        browser.get("https://passport.lagou.com/login/login.html")
        input("手机验证码登陆后按回车")
        cookie = browser.get_cookies()
        cookie_json = json.dumps(cookie)
        with open("lagou_cookie.json",'w') as f:
            f.write(cookie_json)

    def load_cookie(self):
        path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "lagou_cookie.json")
        with open(path,'r',encoding="utf-8") as f:
            return json.loads(f.read())

    # def start_requests(self):
    #     yield Request(url = "https://www.lagou.com",cookies=self.cookie,headers=self.headers)

    rules = (
        # Rule(LinkExtractor(allow=r'jobs/\d+.html'), callback='parse_item', follow=True),
        # Rule(LinkExtractor(allow=r'gongsi/j\d+.html'), callback='parse_item', follow=True),
        Rule(LinkExtractor(allow=r'zhaopin/.*'), callback='parse_item', follow=True),
    )
    def parse_item(self, response):
        job_urls = response.css("a.position_link::attr(href)").extract()
        for job_url in job_urls:
            yield Request(url=job_url, headers=self.headers,callback=self.parse_job)

    def parse_job(self,response):
        lagou_loader = item_loader(item=items.LagouItem(),response=response)
        lagou_loader.add_css("title","div.job-name::attr(title)")
        lagou_loader.add_value("url",response.url)
        lagou_loader.add_value("url_md5_id",md5(response.url))
        lagou_loader.add_css("salary","span.salary::text")
        lagou_loader.add_css("job_city","p span.salary + span::text ")
        lagou_loader.add_css("work_year","dd.job_request p span:nth-child(3)::text")
        lagou_loader.add_css("degree_need","dd.job_request p span:nth-child(4)::text")
        lagou_loader.add_css("job_type","dd.job_request p span:nth-child(5)::text")
        lagou_loader.add_css("publish_time",".publish_time::text")
        lagou_loader.add_css("job_advantage","span.advantage + p::text")
        lagou_loader.add_css("job_desc",".job_bt div.job-detail")
        lagou_loader.add_css("work_addr","div.work_addr a::text")
        lagou_loader.add_css("work_addr_detail", "div.work_addr::text")
        lagou_loader.add_css("company_url","dl.job_company dt a::attr(href)")
        lagou_loader.add_css("company_name","dl.job_company dt a div h2::text")
        lagou_loader.add_css("tags","ul.position-label.clearfix li::text")
        lagou_item = lagou_loader.load_item()
        print(lagou_item)
        pass
        #i = {}
        #return i
# lagou = LagouSpider()
# lagou.login()