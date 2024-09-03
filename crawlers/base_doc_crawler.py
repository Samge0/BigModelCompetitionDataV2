import os
import random
import time
import html2text
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from requests.models import Response
import time

import configs
from utils import fileutils, timeutils, uautils

def selenium_to_requests_response(driver, url):
    """
    将 Selenium 的页面源代码转化为 requests.Response 对象。

    :param driver: Selenium WebDriver 实例
    :param url: 请求的 URL
    :return: requests.Response 对象
    """
    page_source = driver.page_source
    
    # 创建一个新的 requests.Response 对象
    response = Response()

    # 设置页面内容
    response._content = page_source.encode('utf-8')

    # 设置响应状态码为 200 (假设成功)
    response.status_code = 200

    # 设置请求的 URL
    response.url = url

    # 设置请求头（可选）
    response.headers['Content-Type'] = 'text/html; charset=utf-8'

    # 设置 cookies (可选)
    cookies_dict = {cookie['name']: cookie['value'] for cookie in driver.get_cookies()}
    response.cookies.update(cookies_dict)

    # 设置历史记录（如果有重定向等情况）
    response.history = []

    return response

class BaseDocCrawler(object):
    
    # 是否需要替换已存在的文件
    NEED_REPLACE = False
    
    # 是否使用Selenium方式进行请求（处理那些js动态渲染的页面）
    USE_SELENIUM = False
    
    # Selenium等待页面加载完成的时间（秒）
    CHROME_SLEEP_TIME = 5
 
    def get_header(self):
        """
        Get the header to use.

        Returns:
            dict: A dictionary of header, where the key is the header name and the value is the header value.
        """
        return {'User-Agent': uautils.random_one()}

    def get_proxies(self):
        """
        Get the proxies to use.

        Returns:
            dict: A dictionary of proxies, where the key is the protocol and the value is the proxy URL.
        """
        return {'http': None, 'https': None}
    
    @timeutils.monitor
    def get_response(self, link, max_retries=5):
        """
        Try to get the response of a link with a maximum number of retries.

        Args:
            link (str): The link to get the response from.
            max_retries (int, optional): The maximum number of retries. Defaults to 5.

        Returns:
            requests.Response: The response of the link.

        Raises:
            Exception: Raises an exception if all retries failed.
        """
        if not link or not link.startswith('http'):
            return None
        
        try:
            if self.USE_SELENIUM:
                # 设置 ChromeDriver 路径
                service = Service(configs.CHROME_DRIVER_PATH)  
               
                # Create Chrome options
                chrome_options = Options()
                
                # 设置无头模式
                if configs.CHROME_HEADLESS:
                    chrome_options.add_argument("--headless")  # 以无头模式运行，避免弹窗

                # Set User-Agent
                user_agent = (self.get_header() or {}).get('User-Agent')
                chrome_options.add_argument(f"user-agent={user_agent}")

                # Set proxy
                proxy = (self.get_proxies() or {}).get('http')
                if proxy:
                    chrome_options.add_argument(f'--proxy-server={proxy}')

                # Initialize the Chrome driver with options
                driver = webdriver.Chrome(service=service, options=chrome_options)

                # 打开目标网页
                driver.get(link)  # 替换为你的目标网址

                # 等待页面加载完成（可以根据具体情况调整时间或使用显式等待）
                time.sleep(self.CHROME_SLEEP_TIME)

                # 获取页面的渲染后的 HTML
                link_response = selenium_to_requests_response(driver, link)
                
            else:
                link_response = requests.get(link, headers=self.get_header(), proxies=self.get_proxies(), timeout=20, verify=False)
                
            return link_response
        
        except Exception as e:
            if max_retries > 0:
                sleep_time = random.randint(1, 5)
                timeutils.print_log(f"Error: {str(e):100}... Retrying...[{max_retries}]...随机休眠{sleep_time}秒后继续")
                time.sleep(sleep_time)
                return self.get_response(link, max_retries - 1)
            else:
                raise e

    @timeutils.monitor
    def htmlpath2md(self, htmlpath, filename):
        """
        读取HTML文件，使用html2text将其转换为markdown并保存

        :param htmlpath:  HTML文件的路径
        :param filename:  文件名
        :return:
        """
        md_save_path = f"{self.get_markdown_save_dir()}/{filename}.md"
        if self.NEED_REPLACE is False and os.path.exists(md_save_path):
            timeutils.print_log(f"exists, skip: {md_save_path}")
            return
            
        content = fileutils.read(htmlpath)
        md_context = html2text.html2text(content)
        fileutils.save(md_save_path, md_context)
        timeutils.print_log(f"{htmlpath}\n转为 markdown 文件=> {md_save_path}")
        
    def get_filename(self, text, link):
        """
        Get the filename of the link.

        :param link: The link to get the filename of.
        :return: The filename of the link.
        """
        return os.path.basename(link)
    
    def get_html_save_dir(self):
        return fileutils.get_cache_dir('default_doc/html')
    
    def get_markdown_save_dir(self):
        return fileutils.get_cache_dir('default_doc/markdown')
    
    def get_item_list(self, response, soup: BeautifulSoup):
        return []
    
    @timeutils.monitor
    def crawl(self, custom_url=None) -> bool:
        """
        Get the index page of the documentation and traverse the link list to get the content of each page and save it to a file.

        :param custom_url:  user defined url
        :return: is the data being captured normally
        """
        
        index_url = custom_url or self.get_index_url()
        response = self.get_response(index_url)
        soup = BeautifulSoup(response.text, 'html.parser')

        # 获取所有文档item列表，返回格式为：[{'text':'xxx', 'link':'http://xxx'}……]
        lst = self.get_item_list(response, soup)
        if not lst:
            timeutils.print_log(f"解析的列表为空，跳过")
            return False

        # 遍历 lst
        for item in lst:
            text = item.get('text')
            content = item.get('content')
            link = urljoin(index_url, item.get('link'))
            
            if not link or not link.startswith('http'):
                continue
            
            # 自定义文件名
            filename = self.get_filename(text,link)  
            filename = filename.split('?')[0]
            
            if text and text not in filename:
                filename += f"-{text}"

            filename = filename.replace(' ', '-').replace('/', 'or')
            save_path = f"{self.get_html_save_dir()}/{filename}.html"
            if self.NEED_REPLACE is False and os.path.exists(save_path):
                timeutils.print_log(f"exists, skip: {save_path}")
                self.htmlpath2md(save_path, filename)
                continue
            
            if content:
                replace_content = content
                item_soup = BeautifulSoup(replace_content, 'html.parser')
            else:
                # 获取每个链接的响应内容
                link_response = self.get_response(link)
                text = link_response.text if link_response else ''
                item_soup = BeautifulSoup(text, 'html.parser')
                
                # 获取标签名需要替换body的内容
                replace_content = self.get_replace_content(item_soup)

                # 替换原来 'body' 里面的内容
                body_tag = item_soup.find('body')
                if body_tag:
                    body_tag.clear()
                    body_tag.append(replace_content)
            
            # 自动补全所有链接（a、link、script、img等）
            for tag in item_soup.find_all(['a', 'link', 'script', 'img']):
                if tag.name == 'a' and tag.get('href'):
                    tag['href'] = urljoin(index_url, tag['href'])
                elif tag.name == 'link' and tag.get('href'):
                    tag['href'] = urljoin(index_url, tag['href'])
                elif tag.name == 'script' and tag.get('src'):
                    tag['src'] = urljoin(index_url, tag['src'])
                elif tag.name == 'img' and tag.get('src'):
                    tag['src'] = urljoin(index_url, tag['src'])
                    
            fileutils.save(save_path, item_soup.prettify())
                
            self.htmlpath2md(save_path, filename)

            timeutils.print_log(f"Saved: {save_path}")
        
        return True