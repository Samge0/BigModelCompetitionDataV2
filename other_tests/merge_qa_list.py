#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# author：samge
# date：2024-09-05 14:14
# describe：合并qa列表


from utils import fileutils, timeutils


if __name__ == '__main__':
    cache_dir = fileutils.get_cache_dir()
    input_dir = fileutils.get_cache_dir("qas")
    save_path = fileutils.get_cache_dir("allqas") + "/all_qa_list.json"

    file_lst = fileutils.get_files(input_dir, "json")

    results = []
    for filepath in file_lst:
        timeutils.print_log(f"正在处理：{filepath}")
        for item in fileutils.read_json(filepath):
            # 只合并dict格式的
            if not isinstance(item, dict):
                continue
            results.append(item)
    
    fileutils.save_json(save_path, results)
    
    timeutils.print_log(f"合并qa列表完成，总数：{len(results)}")
