import requests

import time
from http.cookiejar import LWPCookieJar
import scrapy
from selenium import webdriver
from pickle import dump,load
from selenium.webdriver.common.keys import Keys
import os
os.path.abspath(os.path.dirname(__file__))

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
        print(response.body.decode("utf-8"))
        pass

    # 获取参数_xsrf
    def get_xsrftoken(self):
        response = requests.session().get("https://www.zhihu.com",headers = self.header)
        return response.cookies['_xsrf']

    #获取验证码
    def get_captcha(self):
        t = str(int(time.time()*1000))
        captcha_url = 'http://www.zhihu.com/captcha.gif?r=' + t + "&type=login"
        response = self.session.get(captcha_url, headers=self.headers)

        pass

    def login(self):
        pass

    def get_cookie(self):
        browser = webdriver.Chrome()
        # browser = webdriver.Chrome(executable_path="./driver/chromedriver.exe")
        browser.get("https://www.zhihu.com/signin")
        browser.find_element_by_name("username").send_keys("18614023195")
        browser.find_element_by_name("password").send_keys("123456abc")
        #browser.find_element_by_class_name("SignFlow-submitButton").send_keys(Keys.ENTER)
        #登录以后再按回车
        input("登录以后再按回车:")
        cookies = browser.get_cookies()
        print(cookies)
        dump(cookies,open(COOKIE_FILE,'wb'))
        browser.close()
        return cookies

zhihu = ZhiHuLoginSpider()
# zhihu.get_cookie()
cookies = load(open(COOKIE_FILE, "rb"))
agent = "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36"
headers = {
    "Host":"www.zhihu.com",
    "Referer":"https://www.zhihu.com",
    "User-Agent":agent,
    "Cookie":COOKIES
}
r = requests.get("https://www.zhihu.com",headers = headers)
print(r.text)




