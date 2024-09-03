#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# author：samge
# date：2024-08-31 21:20
# describe：从markdown文档中提取qa格式的文本

import os
from parses import qas, qautils
from utils import fileutils, timeutils


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
    
    # 记录已处理的下标位置的缓存文件
    index_cache_file = fileutils.get_cache_dir(".index_cache_files") + "/" + os.path.basename(save_path).split('.')[0]
    # 将读取的缓存值分割并转换为整数
    i_index, y_index = map(int, (fileutils.read(index_cache_file) or '0,0').split(','))
    timeutils.print_log(f"从上次处理的位置开始（起始下标为0）：i_index: {i_index}, y_index: {y_index}")
    
    for i in range(i_index, max_times):
        timeutils.print_log(f"【{i+1}/{max_times}】正在处理：")
        
        doc_list = []
        for file_apth in doc_files:
            file_path = file_path.replace(os.sep, '/')
            text = fileutils.read(file_path)
            doc_list += qautils.split_document(text)
            
        qas.generate_enhanced_text(save_path=save_path, doc_list=doc_list, curr_times=i, max_times=max_times, y_index=y_index, index_cache_file=index_cache_file)
        y_index = 0
        
    fileutils.save(index_cache_file, "0,0")   # 全部执行完毕，重置下标索引的缓存
    timeutils.print_log("\nall done")