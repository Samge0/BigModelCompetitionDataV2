#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# author：samge
# date：2024-09-05 14:31
# describe：QA审判长 - 初步非人工干预，快速判断qa是否合格，直接回复“优质”或“丢弃”

import argparse
import os
import configs
from parses import qa_models
from utils import fileutils, timeutils


api_client = None

def get_api_client():
    global api_client
    if not api_client:
        api_client = qa_models.ChatMessageAPI(
            base_url=f'{configs.API_URL}/chat-messages',
            api_key=configs.AUTHORIZATION_QA_JUDGE
        )
    return api_client


@timeutils.monitor
def extract(query):
    try:
        result = get_api_client().send_chat_message(
            query=query,
            user=configs.USER_NAME,
            json_format=False
        )
        return result
    except Exception as e:
        timeutils.print_log(f"extract error: {e}\ntext[:100]...", )
        return None


if __name__ == '__main__':
    
    # 创建解析器
    parser = argparse.ArgumentParser(description="脚本接收 -- 参数")
    
    # 添加参数
    parser.add_argument('--input_path', type=str, help='待处理的qa-json列表文件，多个用|分隔')
    parser.add_argument('--output_dir', type=str, help='输出目录')

    # 解析命令行参数
    args = parser.parse_args()
    
    input_path = args.input_path or fileutils.get_cache_dir("allqas") + "/all_qa_list.json"
    
    if not input_path or not os.path.exists(input_path.split("|")[0]):
        raise ValueError("请输入有效的待处理的qa-json列表文件")
    
    # 输出目录
    output_dir = args.output_dir or fileutils.get_cache_dir("qa_judge_output")
    # 优质qa保存路径
    good_qa_path = os.path.join(output_dir, "good_qa.json")
    good_qa_list = fileutils.read_json(good_qa_path) or []
    # 丢弃qa保存路径
    bad_qa_path = os.path.join(output_dir, "bad_qa.json")
    bad_qa_list = fileutils.read_json(good_qa_path) or []
    
    qa_lst = []
    for filepath in input_path.split("|"):
        qa_lst.extend(fileutils.read_json(filepath) or [])
        
    qa_total = len(qa_lst or [])
    
    # 记录已处理的下标位置的缓存文件
    index_cache_file = fileutils.get_cache_dir(".index_cache_files") + "/" + os.path.basename(input_path.split("|")[0]).split('.')[0]
    # 将读取的缓存值分割并转换为整数
    i_index, = map(int, (fileutils.read(index_cache_file) or '0').split(','))
    timeutils.print_log(f"从上次处理的位置开始（起始下标为0）：i_index: {i_index}")
        
    # 遍历qa，判断是否合格
    for i in range(i_index, qa_total):
        # 记录下标位置
        fileutils.save(index_cache_file, f"{i}")
        
        qa = qa_lst[i]
        qa_str = str(qa)
        timeutils.print_log(f"【{i+1}/{qa_total}】正在处理{qa_str[:100]}……")
        result = extract(qa_str)
        timeutils.print_log(f"【{result}】{qa_str[:100]}……")
        
        if not result or "优质" not in result:
            bad_qa_list.append(qa)
            fileutils.save_json(bad_qa_path, bad_qa_list)
            continue
        good_qa_list.append(qa)
        fileutils.save_json(good_qa_path, good_qa_list)
        
    fileutils.save(index_cache_file, "0")   # 全部执行完毕，重置下标索引的缓存
    timeutils.print_log("\nall done，good_qa_list:", len(good_qa_list), "bad_qa_list:", len(bad_qa_list))
    
    
    

# 记录一下再dify中用到的【QA审判长】提示词
"""
你是一位数据评估专家，目标是帮助用户判断给定的QA数据集是否优质。每个QA数据包括一个问题和对应的答案。请根据以下标准评估数据集的质量：
评估标准：
相关性: 答案必须直接回答问题，并与问题的内容高度相关。
完整性: 答案应全面覆盖问题中提到的内容或意图，考虑到可能的边界情况。
准确性: 答案应准确无误，避免含糊、错误或误导性的内容。
表达清晰度: 答案应易于理解，使用简洁明了的语言，无语法错误或冗余信息。
标签定义：
优质: 数据符合上述所有标准，且答案完整、准确、相关且表达清晰。
丢弃: 数据不符合上述标准之一或多个，答案不完整、与问题无关、不准确或表达不清晰。
根据上述标准，为每个给定的数据集提供评估标签​，直接回复“优质”或“丢弃”。
"""
    