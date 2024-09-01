#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# author：samge
# date：2024-08-26 14:44
# describe：抓取智谱的新闻稿信息

import json
import urllib3
# Suppress only the specific InsecureRequestWarning from urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import os
from bs4 import BeautifulSoup
from base_doc_crawler import BaseDocCrawler
from utils import fileutils, strutils, timeutils


class QzCrealer(BaseDocCrawler):
    
    def __init__(self) -> None:
        super().__init__()
        self.html_template = """<html>
  <head>
    <meta charset="UTF-8" />
    <title>智谱AI</title>
    <meta name="keywords" content="智谱AI、数据与知识双轮驱动" />
    <meta name="viewport" content="width=device-width, user-scalable=no" />
    <!-- <meta name='viewport' content="width=device-width,initial-scale=1.0" /> -->
    <meta
      name="description"
      content="智谱AI是由清华大学计算机系技术成果转化而来的公司，致力于打造新一代认知智能通用模型。公司合作研发了双语千亿级超大规模预训练模型GLM-130B，并构建了高精度通用知识图谱，形成数据与知识双轮驱动的认知引擎，基于此模型打造了ChatGLM（chatglm.cn）。此外，智谱AI还推出了认知大模型平台Bigmodel.ai，包括CodeGeeX和CogView等产品，提供智能API服务，链接物理世界的亿级用户、赋能元宇宙数字人、成为具身机器人的基座，赋予机器像人一样“思考”的能力。"
    />
    <link rel="icon" type="image/png" href="/assets/images/page_logo2.png" />

    <link rel="stylesheet" href="/assets/images/js/css/index.css" />
    <link rel="stylesheet" href="/umi.b70826a1.css" />
    <script>
      window.routerBase = "/";
    </script>
    <script>
      //! umi version: 3.5.39
    </script>
  </head>

  <body style="-webkit-font-smoothing: antialiased">
    <div id="root">{body_content}</div>
    <link rel="stylesheet" href="/medical/assets/css/font-awesome.min.css" />
    <script
      async=""
      src="https://www.googletagmanager.com/gtag/js?id=G-SRG7VN5G3M"
    ></script>
    <script
      async=""
      src="//at.alicdn.com/t/c/font_4009508_jptiugy0x5l.js"
    ></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag() {
        dataLayer.push(arguments);
      }
      gtag("js", new Date());

      gtag("config", "G-SRG7VN5G3M");
    </script>

    <script src="/umi.68bec7bd.js"></script>
  </body>
</html>
"""
    
    def get_index_url(self):
        return ''
    
    def get_html_save_dir(self):
        return fileutils.get_cache_dir('zp/html')
    
    def get_markdown_save_dir(self):
        return fileutils.get_cache_dir('zp/markdown')
    
    def get_item_list(self, response, soup: BeautifulSoup):
        # 如果 soup 是 JSON 数据，先将其转换为字符串
        
        lst = []
        try:
            # 解析 JSON 字符串
            data = response.json()
            # 假设 JSON 数据是一个包含项目列表的字典
            item_list = data.get('results', [])  # 根据 JSON 结构提取需要的数据
            for node in item_list:
                _title = node.get('title')
                _link = None
                _date = node.get('pub_date').replace(' ', '').replace(':', '').replace('-', '')
                _text = strutils.sanitize_filename(f"{_date}-新闻稿-{_title}")
                
                _content = node.get('content')
                # 替换原来 'body' 里面的内容
                _content = self.html_template.replace('{body_content}', _content)
                
                lst.append({'text': _text, 'link': _link, 'content': _content})
        except json.JSONDecodeError as e:
            timeutils.print_log(f"JSON decoding failed: {e}")
        return lst
    
    def get_replace_content(self, soup: BeautifulSoup):
        # 获取标签名为 'main' 的文本
        main_tag = soup.select_one('div.n-content')
        if not main_tag:
            return ''

        return main_tag
    
    def get_filename(self, text, link):
        return text or os.path.basename(link)
    
    
if __name__ == '__main__':
    url_template = 'https://zhipuaiadmin.aminer.cn/api/blog/get_blog_list?page={page}&size=9&category=新闻稿'
    for i in range(1, 1000000):
        url = url_template.format(page=i)
        timeutils.print_log("crawling: ", url)
        crawl_status = QzCrealer().crawl(custom_url=url)
        if not crawl_status:
            break
    timeutils.print_log("\nall done")