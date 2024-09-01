#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# author：samge
# date：2024-09-01 01:53
# describe：

from parses import qas
from utils import fileutils, timeutils


if __name__ == "__main__":
    
    # 待处理的qa列表数据
    text = fileutils.read(f"{fileutils.get_cache_dir()}/qa.json")
    qa_list = qas.load_json(text)
    
    # 生成数据的保存路径
    save_path = f"{fileutils.get_cache_dir()}/enhanced_qas.json"
    
    # 最大生成次数
    max_times = 100
    
    for z in range(max_times):
        timeutils.print_log(f"【{z+1}/{max_times}】正在处理：")
        qas.generate_enhanced_text(save_path=save_path, qa_list=qa_list)

    timeutils.print_log("\nall done")