#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2018-12-19 10:05:17
# Project: mafengwo

from pyspider.libs.base_handler import *
from pyspider.libs.header_switch import HeadersSelector
from pyquery import PyQuery as pq
import json

main_url = "http://www.mafengwo.cn/"
class Handler(BaseHandler):
    crawl_config = {
        'itag': 'v1',
        "user_agent": "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36",
        "timeout": 120,
        "connect_timeout": 60,
        "retries": 5,
        "auto_recrawl": True,
    }

    #@every(minutes=1)
    def on_start(self):
        header_slt = HeadersSelector()
        header = header_slt.select_header()  # 获取一个新的 header
        # header["X-Requested-With"] = "XMLHttpRequest"
        header["Host"] = "www.mafengwo.cn"
        self.crawl('http://www.mafengwo.cn/', callback=self.index_page,
                   headers=header)

    @config(age=1)
    def index_page(self, response):
        header_slt = HeadersSelector()
        header = header_slt.select_header()  # 获取一个新的 header
        # header["X-Requested-With"] = "XMLHttpRequest"
        header["Host"] = "www.mafengwo.cn"
        if response.cookies:
            header["Cookies"] = response.cookies
        for each in response.doc('a[href^="http://www.mafengwo.cn/traveller/"]').items():
            self.crawl(each.attr.href, callback=self.tdetail_page,
                  headers=header)
        for each in response.doc('a[href^="http://www.mafengwo.cn/i/"]').items():
            self.crawl(each.attr.href, callback=self.idetail_page,
                   headers=header)
            
        base_url = "http://pagelet.mafengwo.cn/note/pagelet/recommendNoteApi?callback=jQuery18108796192355544348_1545187965755&params=%7B%22type%22%3A0%2C%22objid%22%3A0%2C%22page%22%3A"
        final_url="%2C%22ajax%22%3A1%2C%22retina%22%3A1%7D&_=1545191377450"
            
        for page_num in range(1, 90):
            page_url = base_url + '{}&'.format(page_num) + final_url
            #print page_url
            self.crawl(page_url, callback=self.parse_page, method='GET')
            
    def parse_page(self, response):
        #print response.text
        nPos=response.text.index("(")+1
        nEnd=response.text.rfind(")")
        response.text[nPos:nEnd]
        #print response.text[nPos:nEnd]
        
        params = json.loads(response.text[nPos:nEnd])
        #print params['data']['html']
        d = pq(params['data']['html'])
        for each in d('a[href^="\/i"]').items():
            url = each.attr.href
            print main_url + url
            self.crawl(main_url +url, callback=self.idetail_page, method='GET')

    @config(priority=2)
    def idetail_page(self, response):
        print response
        cost = response.doc('.cost').text()
        people = response.doc('.people').text()
        time = response.doc('ul > .time').text()
        day = response.doc('.day').text()
        content = response.doc('html > body > .main > .view > .view_con > .vc_article > ._j_master_content').html()
        return {
            'url': response.url,
            "title": response.doc('title').text(),
            'cost': cost,
            'time': time,
            'day': day,
            'people': people,
            'content': content
        }
    
    @config(priority=1)
    def tdetail_page(self, response):
        title = response.doc('.h1').text()
        content = response.doc('.ac_body > p').text()
        return {
            "url": response.url,
            "title": response.doc('title').text(),
            'cost': '',
            'time': '',
            'day': '',
            'people': '',
            "content":content
        }

