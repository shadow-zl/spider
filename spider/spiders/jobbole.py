# -*- coding: utf-8 -*-
import scrapy
import re
from scrapy.http import Request
from urllib import parse
import sys
from spider.items import AriticleItem
from spider.utils.common import md5
import datetime
from scrapy.loader import ItemLoader
from spider.items import item_loader
sys.setrecursionlimit(1000000)

class JobboleSpider(scrapy.Spider):
    name = 'jobbole'
    allowed_domains = ['blog.jobbole.com']
    start_urls = ['http://blog.jobbole.com/all-posts/']

    def parse(self, response):
        # title = response.xpath('//*[@id="post-113532"]/div[1]/h1/text()').extract()[0]
        # date = response.xpath('//*[@id="post-113532"]/div[2]/p/text()[1]').extract()[0].strip().replace(' ·', '')
        # tags = response.xpath('//*[@id="post-113532"]/div[2]/p/a/text()').extract()
        # #endswith()
        # tags = [tag for tag in tags if not  tag.strip().endswith('评论')]
        # #join()
        # tags = ",".join(tags)
        # praise = response.xpath('//*[@id="113532votetotal"]/text()').extract()[0]
        # collect = response.xpath('//span[contains(@class,"bookmark-btn ")]/text()').extract()[0]
        # if re.match(r'.*(\d+)(.*)', collect):
        #     collect = re.match(r'.*?(\d+)(.*)', collect).group(1)
        # comment = response.xpath('//*[@id="post-113532"]/div[3]/div[3]/a/span/text()').extract()[0]
        # if re.match(r'.*(\d+)(.*)', comment):
        #     comment = re.match(r'.*?(\d+)(.*)', comment).group(1)
        # article = response.xpath('//*[@class="entry"]').extract()[0]

        """下载URL"""
        post_nodes = response.css('#archive .floated-thumb .post-thumb a')
        for post_node in post_nodes:
             img_url = post_node.css('img::attr(src) ').extract_first("" )
             post_url = post_node.css('::attr(href)').extract_first(" ")
             yield Request(url=parse.urljoin(response.url,post_url),meta={'img_url':img_url},callback=self.parse_detail)


        """下一页"""
        next_url = response.css('a.next.page-numbers::attr(href)').extract_first()
        if next_url:
            yield Request(url = parse.urljoin(response.url,next_url),callback=self.parse)

    def parse_detail(self,response):

        title = response.css("div.entry-header h1::text").extract_first("")  #extract_first()
        print(title)
        date = response.css('p.entry-meta-hide-on-mobile::text').extract_first("").strip().replace('·','').strip()
        tags = response.css('p.entry-meta-hide-on-mobile a::text').extract()
        tags = [tag.strip() for tag in tags if not tag.strip().endswith('评论')]   #endswith()
        tags = ",".join(tags)
        article = response.css('div.entry').extract_first("")
        praise = response.css('span.vote-post-up h10::text').extract_first("")
        store = response.css('span.bookmark-btn::text').extract_first("")
        if re.match(r'.*?(\d+).*',store):
            store = re.match(r'.*?(\d+).*',store).group(1)
        else:
            store=0
        comment = response.css('a[href="#article-comment"] span.btn-bluet-bigger::text').extract_first("")
        if re.match(r'.*?(\d+).*',comment):
            comment = int(re.match(r'.*?(\d+).*',comment).group(1))
        else:
            comment=0
        img_url = response.meta.get('img_url',"")

        # item = AriticleItem()
        # item['url'] = url
        # item['url_md5'] = md5(response.url)
        # item['title'] = title
        # try:
        #     date = datetime.strptime(date,"%Y/%m/%d").date()
        # except Exception as e:
        #     date = datetime.datetime.now().date()
        # item['date'] = date
        # item['tags'] = tags
        # item['article'] = article
        # item['praise'] = praise
        # item['store'] = store
        # item['comment'] = comment
        # item['img_url'] = [img_url]

        """itemloader★★"""
        loader = item_loader(item = AriticleItem(),response=response)
        loader.add_css("title","div.entry-header h1::text")
        loader.add_value('url',response.url)
        loader.add_value("url_md5",md5(response.url))
        loader.add_css("date","p.entry-meta-hide-on-mobile::text")
        loader.add_css("tags","p.entry-meta-hide-on-mobile a::text")
        loader.add_css('article','div.entry')
        loader.add_css('praise','span.vote-post-up h10::text')
        loader.add_css('store','span.bookmark-btn::text')
        loader.add_css('comment','a[href="#article-comment"] span.btn-bluet-bigger::text')
        loader.add_value('img_url',response.meta.get('img_url',""))
        item = loader.load_item()
        yield item
        pass


