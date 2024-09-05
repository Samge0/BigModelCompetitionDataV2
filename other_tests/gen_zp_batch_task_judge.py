#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# author：samge
# date：2024-09-05 16:42
# describe：生成智谱批量任务的jsonl文件（QA审判），利用智谱平台的batch api批量执行，详情见：https://bigmodel.cn/dev/howuse/batchapi

import argparse
import os
from utils import fileutils, timeutils


default_prompt = """你是一位数据评估专家，目标是帮助用户判断给定的QA数据集是否优质。每个QA数据包括一个问题和对应的答案。请根据以下标准评估数据集的质量：
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

# model = "glm-4-0520"     # 默认 0.1/1000tokens => batch 0.05/1000tokens
model = "glm-4-flash"    # 免费 https://bigmodel.cn/pricing


def gen_batch_request_item(qa, index, custom_prompt):
    return {"custom_id": f"request-{index}", "method": "POST", "url": "/v4/chat/completions", "body": {"model": model, "messages": [{"role": "system", "content": custom_prompt or default_prompt},{"role": "user", "content": str(qa)}]}}


if __name__ == '__main__':
    
    # 创建解析器
    parser = argparse.ArgumentParser(description="脚本接收 -- 参数")
    
    # 添加参数
    parser.add_argument('--input_path', type=str, help='待处理的qa-json列表文件，多个用|分隔')
    parser.add_argument('--output_dir', type=str, help='输出目录')
    parser.add_argument('--custom_prompt', type=str, help='自定义的prompt')

    # 解析命令行参数
    args = parser.parse_args()
    
    input_path = args.input_path or fileutils.get_cache_dir("allqas") + "/all_qa_list.json"
    
    if not input_path or not os.path.exists(input_path.split("|")[0]):
        raise ValueError("请输入有效的待处理的qa-json列表文件")
    
    # 输出目录
    output_dir = args.output_dir or fileutils.get_cache_dir("zh_batch_input_files")
    # batch qa的保存路径
    batch_qa_path = os.path.join(output_dir, "all_qa_list_batch.jsonl")
    # batch qa的保存路径 - 切割100条数据作为测试
    batch_qa_path_test100 = os.path.join(output_dir, "all_qa_list_batch_test100.jsonl")
    
    qa_lst = []
    for filepath in input_path.split("|"):
        qa_lst.extend(fileutils.read_json(filepath) or [])
    
    batch_qa_list = []    
    
    # 遍历qa，判断是否合格
    for i in range(len(qa_lst)):
        qa = qa_lst[i]
        result = gen_batch_request_item(qa, i, args.custom_prompt)
        batch_qa_list.append(result)
        
    fileutils.save_jsonl(batch_qa_path, batch_qa_list)
    fileutils.save_jsonl(batch_qa_path_test100, batch_qa_list[:100])
    timeutils.print_log("\nall done")
