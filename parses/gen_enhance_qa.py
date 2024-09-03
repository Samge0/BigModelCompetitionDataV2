#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# author：samge
# date：2024-09-01 01:53
# describe：从已有的qa数据中逐条增强生成新的qa信息

import os
from parses import qas
from utils import fileutils, timeutils


if __name__ == "__main__":
    
    # 待处理的qa列表数据
    text_qa = fileutils.read(f"{fileutils.get_cache_dir()}/qa.json")
    text_qa_custom = fileutils.read(f"{fileutils.get_cache_dir()}/qa_custom.json")
    doc_list = [str(item) for item in qas.load_json(text_qa)] + [str(item) for item in qas.load_json(text_qa_custom)]
    
    # 生成数据的保存路径
    save_path = f"{fileutils.get_cache_dir()}/enhanced_qas_merge.json"
    
    # 最大生成次数
    max_times = 50
    
    # 记录已处理的下标位置的缓存文件
    index_cache_file = fileutils.get_cache_dir(".index_cache_files") + "/" + os.path.basename(save_path).split('.')[0]
    # 将读取的缓存值分割并转换为整数
    i_index, y_index = map(int, (fileutils.read(index_cache_file) or '0,0').split(','))
    timeutils.print_log(f"从上次处理的位置开始（起始下标为0）：i_index: {i_index}, y_index: {y_index}")
    
    for i in range(i_index, max_times):
        timeutils.print_log(f"【{i+1}/{max_times}】正在处理：")
        qas.generate_enhanced_text(save_path=save_path, doc_list=doc_list, curr_times=i, max_times=max_times, y_index=y_index, index_cache_file=index_cache_file)

    fileutils.save(index_cache_file, "0,0")   # 全部执行完毕，重置下标索引的缓存
    timeutils.print_log("\nall done")