#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# author：samge
# date：2024-09-05 14:14
# describe：合并qa列表


from utils import fileutils, timeutils


if __name__ == '__main__':
    cache_dir = fileutils.get_cache_dir()
    
    input_dir = fileutils.get_cache_dir("qas")
    file_lst = fileutils.get_files(input_dir, "json")
    
    save_path = fileutils.get_cache_dir("allqas") + "/all_qa_list.json"
    messages_save_path = fileutils.get_cache_dir("allqas") + "/all_messages_qa_list.json"

    results = []
    messages_results = []
    
    for filepath in file_lst:
        timeutils.print_log(f"正在处理：{filepath}")
        for item in fileutils.read_json(filepath):
            if isinstance(item, dict):
                results.append(item)
            elif isinstance(item, list):
                messages_results.append(item)
    
    fileutils.save_json(save_path, results)
    fileutils.save_json(messages_save_path, messages_results)
    
    timeutils.print_log(f"合并qa列表完成，单项QA总数：{len(results)}, 多轮消息QA总数：{len(messages_results)}")
