#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# author：samge
# date：2024-08-23 16:49
# describe：

API_URL = 'http://localhost:80/v1'                      # dify的api地址，请替换为实际的服务器地址
AUTHORIZATION = 'xxx'                                   # dify的api鉴权token
USER_NAME = 'xxx'                                       # dify的api请求用户名

# 待处理的文档目录
DOC_DIR = "xxx"  
# 指定文档后缀，暂时只支持文本类型                            
DOC_SUFFIX = 'md,txt'    
# 文档最少行数，低于该值的文档则被忽略，该参数仅作用于 txt,md,html 后缀文件
DOC_MIN_LINES = 6

# 替换为你本地的 ChromeDriver 路径
CHROME_DRIVER_PATH = "xxx/chromedriver-win64/chromedriver.exe"
# 是否以无头模式运行，避免弹窗
CHROME_HEADLESS = True

# 智谱平台的apikey
ZHI_PU_API_KEY = ""
# 智谱平台的模型名
ZHI_PU_MODEL = ""