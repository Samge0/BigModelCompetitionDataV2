#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# author：samge
# date：2024-08-31 21:20
# describe：从markdown文档中提取qa格式的文本

import os
import re
from parses import qas
from utils import fileutils, timeutils


def gen_qa_item(text):
    return {'question': '', 'answer': text}

# 将长文档拆分为小块
def split_document(document, max_length=2000):
    return [gen_qa_item(document)] + [gen_qa_item(document[i:i + max_length]) for i in range(0, len(document), max_length)]


if __name__ == '__main__':
    
    data_dir = fileutils.get_cache_dir("zp_docs/markdown")
    save_path = fileutils.get_cache_dir() + "/doc_enhanced_qas.json" 
    
    # 使用 glob 模块获取所有待处理文档文件
    doc_files = fileutils.get_files(data_dir, 'txt,md') or []

    file_total = len(doc_files)
    if file_total == 0:
        raise ValueError(f"在 {data_dir} 目录下没有找到符合要求文档文件") 
    
    # 最大生成次数
    max_times = 100
    for z in range(max_times):
        
        timeutils.print_log(f"【{z+1}/{max_times}】正在处理：")
        
        qa_list = []
        for i in range(file_total):
            file_path = doc_files[i]
            file_path = file_path.replace(os.sep, '/')
            text = fileutils.read(file_path)
            qa_list += split_document(text)
            
        qas.generate_enhanced_text(save_path=save_path, qa_list=qa_list)
    
    timeutils.print_log("\nall done")