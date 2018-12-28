#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2018-12-19 10:05:17
# Project: mafengwo

from pyspider.libs.base_handler import *
from pyspider.libs.header_switch import HeadersSelector
from pyquery import PyQuery as pq
from pyspider.libs.utils import md5string
from random import choice
import json
import time
import re

main_url = "http://www.mafengwo.cn/"

class Handler(BaseHandler):
    file = open("/usr/lib/python2.7/site-packages/pyspider/proxy_ip.txt","r")
    filecontent = file.readlines()
    
    header_slt = HeadersSelector()
    header = header_slt.select_header()  # 获取一个新的 header
    header["X-Requested-With"] = "XMLHttpRequest"
    header["Host"] = "pagelet.mafengwo.cn"
    
    crawl_config = {
        "itag":"v12",
        #"proxy":choice(filecontent).strip('\r\n'),
        "timeout": 120,
        "connect_timeout": 60,
        "retries": 5,
        "auto_recrawl": True,
        "process_time_limit":120
    }
    
    #def get_taskid(self,task):
        #return md5string(task['url']+json.dumps(task['fetch'].get('data','')))

    @every(minutes=24*60)
    @config(age=10*60*60)
    def on_start(self):
        base_url = "http://pagelet.mafengwo.cn/note/pagelet/recommendNoteApi?callback=jQuery18106975500853167276_1545707077976&params=%7B%22type%22%3A0%2C%22objid%22%3A0%2C%22page%22%3A"
        final_url="%2C%22ajax%22%3A1%2C%22retina%22%3A1%7D&_=1545707093353"
            
        for page_num in range(1, 90):
            time.sleep(1)
            page_url = base_url + '{}&'.format(page_num) + final_url
            #print page_url
            self.crawl(page_url, callback=self.index_page)

    @config(age=10*60*60)
    def index_page(self, response): 
        #header_slt = HeadersSelector()
        #header = header_slt.select_header()  # 获取一个新的 header
        # header["X-Requested-With"] = "XMLHttpRequest"
        #header["Host"] = "www.mafengwo.cn"
        #if response.cookies:
            #header["Cookies"] = response.cookies
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
            print main_url + url[1:]
            self.crawl(main_url +url[1:]+"?static_url=true", callback=self.idetail_page)

    @config(priority=3)
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
    
    
