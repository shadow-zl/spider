import requests

import time
from http.cookiejar import LWPCookieJar
import scrapy
from selenium import webdriver
from pickle import dump,load
import json
import os

current_path = os.path.dirname(__file__)
parent_path = os.path.abspath('..')


path = os.path.join(os.path.abspath(".."),"data")
COOKIE_FILE = path+'/cookie/cookies.pkl'
COOKIES = '_zap=48c91d71-b05d-45cd-9fe2-c3eabd52846c; _xsrf=b2a0ee78-b599-4d7b-aa4b-e210ac943321; d_c0="AMCiUg64zA6PTpLvO8t_K0lFFhK0sYMBOvU=|1547036625"; capsion_ticket="2|1:0|10:1547037987|14:capsion_ticket|44:MTgwYTZmNGQwYzc3NDExYThiZGFiYmIwZDNjZWJjODE=|942e1ca8770d4e64725184e6cf954245ef04dddec299d1a207bc73d15b5a4f85"; tgw_l7_route=80f350dcd7c650b07bd7b485fcab5bf7; z_c0="2|1:0|10:1547042556|4:z_c0|92:Mi4xdlVTQ0RRQUFBQUFBd0tKU0Ryak1EaWNBQUFDRUFsVk5fSXRkWEFCMEN4R2ZzVm1ibDhjUHNSNWliSnl5dzFCWU93|815659a2c6613438c06473f7b0b476b568ecdd682ccfc341c539049ebb01f87f"'
class ZhiHuLoginSpider(scrapy.Spider):
    name = 'zhuhu_login'
    start_urls =['www.zhihu.com']

    def __init__(self):

        self.agent = "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36"
        self.header = {
                        "Host":"www.zhihu.com",
                        "Referer":"https://www.zhihu.com",
                        "User-Agent":self.agent,
                        # 'Connection': 'keep-alive'
        }
        self.session = requests.session()
        self.session.keep_alive = False
        self.session.cookies=LWPCookieJar('cookie')
        # try:
        #         #     self.session.cookies.load(ignore_discard=True)
        #         #     print("Cookie加载成功")
        #         # except IOError:
        #         #     print("Cookie未加载")
        #         # self.signature=None
        #         # self.picture = None

    def parse(self, response):
        # print(response.body.decode("utf-8"))
        pass

    def login(self):
        self.load_cookie()
        self.header['Cookie'] = self.load_cookie()
        try:
            r = requests.get("https://www.zhihu.com",headers = self.header)
        except Exception as e:
            print("cookie过期，重新登录")
            self.get_cookie()
            r = requests.get("https://www.zhihu.com",headers = self.header)
        print(r.text)
        pass

    def get_cookie(self):
        # browser = webdriver.Chrome()
        browser = webdriver.Chrome(executable_path="../driver/chromedriver.exe")
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
        return cookies_json

    def load_cookie(self):
        with open('cookies.json','r',encoding='utf-8') as f:
            cookies_json = json.loads(f.read())
        cookies = [item['name']+"="+item['value'] for item in cookies_json]
        cookies = ';'.join(cookie for cookie in cookies)
        return cookies

zhihu = ZhiHuLoginSpider()
zhihu.login()




