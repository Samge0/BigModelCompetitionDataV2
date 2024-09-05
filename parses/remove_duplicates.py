#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# author：samge
# date：2024-09-05 10:44
# describe：遍历指定目录及其子目录下的所有json文件，移除某字段存在重复的内容


import argparse
import json

from utils import fileutils, md5utils, timeutils


if __name__ == '__main__':
    
    # 创建解析器
    parser = argparse.ArgumentParser(description="脚本接收 -- 参数")
    parser.add_argument('--input_dir', type=str, help='待处理的文件夹目录，多个用|分隔，默认不传则处理.cache目录')
    parser.add_argument('--global_remove', type=str, help='是否全局去重移除，true=从整个文件夹的角度去重，false=从单个文件的角度去重，默认为false')
    parser.add_argument('--key_question', type=str, help='输入的json中对应的question键名')
    parser.add_argument('--key_answer', type=str, help='输入的json中对应的answer键名')
    args = parser.parse_args()
    
    input_dir = args.input_dir or fileutils.get_cache_dir("qas")
    # input_dir = args.input_dir or fileutils.get_cache_dir()
    file_list = fileutils.get_files(input_dir, "json")
    
    key_question = args.key_question or 'question'
    key_answer = args.key_answer or 'answer'
    
    # 是否全局去重
    is_global_remove = args.global_remove == "true"
    
    # 使用集合来跟踪已经添加的QA
    existing_qa_md5s = set()
    
    # 总移除数量
    total_removed = 0
    
    for file_path in file_list:
        qa_api_results = []
        timeutils.print_log(f"正在处理：{file_path}")
        
        if not is_global_remove:
            timeutils.print_log(f"不是全局去重，每次遍历一次文件时需要重置：existing_qa_md5s ")
            existing_qa_md5s = set()
        
        qa_list = fileutils.read_json(file_path)
        for qa in qa_list:
            if not qa:
                total_removed += 1
                continue
            
            if isinstance(qa, str):
                timeutils.print_log("不符合格式要求的Q/A，跳过：" + qa)
                total_removed += 1
                continue
            
            if isinstance(qa, list):
                new_qa_item = [{key_question: tmp_item.get(key_question), key_answer: tmp_item.get(key_answer)} for tmp_item in qa if tmp_item.get(key_question) and tmp_item.get(key_answer)]
            else:
                if not qa.get(key_question) or not qa.get(key_answer):
                    total_removed += 1
                    continue
                new_qa_item = {key_question: qa.get(key_question), key_answer: qa.get(key_answer)}
            
            qa_md5 = md5utils.calculate_md5(json.dumps(new_qa_item))
            
            if qa_md5 in existing_qa_md5s:
                timeutils.print_log(f"已存在该Q/A，跳过：{str(new_qa_item)[:100]}...")
                total_removed += 1
                continue
            
            # 如果问题不在集合中，才添加到结果列表，并且更新集合
            qa_api_results.append(new_qa_item)
            existing_qa_md5s.add(qa_md5)
            
        # 写入文件 
        fileutils.save_json(file_path, qa_api_results)
            
    timeutils.print_log(f"\nall done，共移除{total_removed}条数据")