#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# author：samge
# date：2024-09-01 01:53
# describe：从已有的qa数据中逐条增强生成新的qa信息

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
    
    for z in range(max_times):
        timeutils.print_log(f"【{z+1}/{max_times}】正在处理：")
        qas.generate_enhanced_text(save_path=save_path, doc_list=doc_list, curr_times=z, max_times=max_times)

    timeutils.print_log("\nall done")