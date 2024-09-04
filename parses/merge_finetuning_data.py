#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# author：samge
# date：2024-09-02 09:28
# describe：


import random
from parses import qas, qautils
from utils import fileutils, timeutils

# 目标目录位置
GOAL_DIR = fileutils.get_cache_dir('qas')


# 生成微调的数据
def gen_finetuning_data(json_data, need_default_prompt=True):
    messages = []
    json_data_list = json_data if isinstance(json_data, list) else [json_data]
    for json_data_item in json_data_list:
        if not qautils.is_qa_item_format(json_data_item):
            continue
        question = json_data_item.get('question')
        answer = json_data_item.get('answer')
        messages.append({"role": "user", "content": question})
        messages.append({"role": "assistant", "content": answer})
        
    if not messages:
        return None
    
    if need_default_prompt:
        messages.insert(0, {"role": "system", "content": "你是智谱MaaS平台的智能客服，你的任务是为用户提供专业、准确的建议。"})
        
    return {"messages": messages}


if __name__ == "__main__":
    
    filter_total = 0
    results = []
    json_list = fileutils.get_files(GOAL_DIR, 'json')
    for json_path in json_list:
        json_str = fileutils.read(json_path)
        json_datas = qas.load_json(json_str)
        for json_data in json_datas:
            finetuning_data = gen_finetuning_data(json_data)
            if not finetuning_data:
                continue
            results.append(finetuning_data)

    # 打乱数据顺序
    random.shuffle(results)
           
    # 保存 
    save_path = f'{fileutils.get_cache_dir()}/finetuning_data.jsonl'
    fileutils.save_jsonl(save_path, results)
    
    timeutils.print_log("\nall done，共移除", filter_total, "条不符合要求的数据")
