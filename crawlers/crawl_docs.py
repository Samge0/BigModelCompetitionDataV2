#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# author：samge
# date：2024-08-26 14:44
# describe：抓取智谱的新闻稿信息

import urllib3
# Suppress only the specific InsecureRequestWarning from urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import os
from bs4 import BeautifulSoup
from base_doc_crawler import BaseDocCrawler
from utils import fileutils, strutils, timeutils

# api文档的地址
_API_DOC_URL = 'https://bigmodel.cn/dev/api'


class ZpCrealer(BaseDocCrawler):
    
    USE_SELENIUM = True
    
    def get_index_url(self):
        return ''
    
    def get_html_save_dir(self):
        return fileutils.get_cache_dir('zp_docs/html')
    
    def get_markdown_save_dir(self):
        return fileutils.get_cache_dir('zp_docs/markdown')
    
    def get_item_list(self, response, soup: BeautifulSoup):
        if response.url == _API_DOC_URL:
            return [{'text': '智谱bigmodel接口文档', 'link': _API_DOC_URL} ]
        
        lst = [{'text': a.text.strip(), 'link': a['href']} for a in soup.find_all('a', class_='side-bar-item', href=True) if a['href'].strip() ]
        return lst
    
    def get_replace_content(self, soup: BeautifulSoup):
        # 获取标签名为 'main' 的文本
        main_tag = soup.select_one('div.how-use-content') or soup.select_one('div.page-api-right')
        if not main_tag:
            return ''

        return main_tag
    
    def get_filename(self, text, link):
        return text or os.path.basename(link)
    
    
if __name__ == '__main__':
    url_lst = [
      "https://bigmodel.cn/dev/howuse/introduction",    # 智谱bigmodel介绍
      _API_DOC_URL,
    ]
    for url in url_lst:
        timeutils.print_log("crawling: ", url)
        crawl_status = ZpCrealer().crawl(custom_url=url)
        if not crawl_status:
            break
    timeutils.print_log("\nall done")