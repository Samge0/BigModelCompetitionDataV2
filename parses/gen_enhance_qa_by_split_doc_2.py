#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# author：samge
# date：2024-08-31 21:20
# describe：从markdown文档中提取qa格式的文本

import os
import re
from parses import qas, qautils
from utils import fileutils, timeutils


if __name__ == '__main__':
    
    data_dir = fileutils.get_cache_dir("zp/markdown")
    save_path = fileutils.get_cache_dir() + "/news_enhanced_qas.json" 
    
    # 使用 glob 模块获取所有待处理文档文件
    doc_files = fileutils.get_files(data_dir, 'txt,md') or []

    file_total = len(doc_files)
    if file_total == 0:
        raise ValueError(f"在 {data_dir} 目录下没有找到符合要求文档文件") 
    
    # 最大生成次数
    max_times = 100
    for z in range(max_times):
        
        timeutils.print_log(f"【{z+1}/{max_times}】正在处理：")
        
        doc_list = []
        for i in range(file_total):
            file_path = doc_files[i]
            file_path = file_path.replace(os.sep, '/')
            text = fileutils.read(file_path)
            doc_list += qautils.split_document(text)
            
        qas.generate_enhanced_text(save_path=save_path, doc_list=doc_list, curr_times=z, max_times=max_times)
    
    timeutils.print_log("\nall done")