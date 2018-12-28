#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2018-08-03 09:59:05
# Project: TripAdcisor
 
from pyspider.libs.base_handler import *
from pyspider.libs.header_switch import HeadersSelector
from random import choice
#import ssl
#import pymongo

#ssl._create_default_https_context=ssl._create_unverified_context
 
class Handler(BaseHandler):
    file = open("/usr/lib/python2.7/site-packages/pyspider/proxy_ip.txt","r")
    filecontent = file.readlines()
    
    crawl_config = {
        "itag":"v2",
        #"proxy":choice(filecontent).strip('\r\n'),
        "timeout": 120,
        "connect_timeout": 60,
        "retries": 5,
        "auto_recrawl": True,
        "process_time_limit":120
    }
    
    @every(minutes=24 * 60)
#on_start 启动目标主网站,validate_cert = False跳过证书检测,callback回调函数
    def on_start(self):
        header_slt = HeadersSelector()
        header = header_slt.select_header()  # 获取一个新的 header
        #header["X-Requested-With"] = "XMLHttpRequest"
        header["Host"] = "www.tripadvisor.cn"
        self.crawl('https://www.tripadvisor.cn/TourismBlog-g294217-Hong_Kong.html', callback=self.index_page,validate_cert = False,headers=header)
 
    @config(age=10 * 24 * 60 * 60)
#通过内置pyquery 获取目标网页的连接遍历 分别访问,并回调
    def index_page(self, response):
        header_slt = HeadersSelector()
        header = header_slt.select_header()  # 获取一个新的 header
        #header["X-Requested-With"] = "XMLHttpRequest"
        header["Host"] = "www.tripadvisor.cn"
        for each in response.doc('a[href^="https://www.tripadvisor.cn/TourismBlog-g"]').items():
            if each.attr.href == response.url:
                continue
            else:
                self.crawl(each.attr.href, callback=self.index_page,validate_cert = False,headers=header)
        for each in response.doc('a[href^="https://www.tripadvisor.cn/TourismBlog"]').items():
            self.crawl(each.attr.href, callback=self.detail_page,validate_cert = False,headers=header,save={'categrey': response.url})
 
    @config(priority=2)
#获得每个链接的的详细信息返回
    def detail_page(self, response):
        url = response.url
        content = response.text
        line = response.doc('.trip-path').text()
        title = response.doc('.title-text').text()
        actor = response.doc('.strategy-info > a').text()
        categrey = response.save['categrey']
        
        return {  
            'categrey':categrey,
            'title':title,
            'actor':actor,
            'line':line,
            'content':content,
            'url':url
        }
