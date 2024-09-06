#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# author：samge
# date：2024-09-05 16:42
# describe：生成智谱批量任务的jsonl文件（QA增强），利用智谱平台的batch api批量执行，详情见：https://bigmodel.cn/dev/howuse/batchapi

import argparse
import os
from utils import fileutils, timeutils


default_prompt = """你是一位专业的AI助手，目标是帮助用户生成多个问题的变体表达，并为每个变体提供适应不同场景的稳健答案，增强鲁棒性。在处理文本格式时，请必须提取关键信息并以结构化的方式呈现。下面是原始的问答数据格式：
{\"question\": \"...\", \"answer\": \"...\"}
请生成多个变体的表达方式，使得这些问题涵盖各种可能的用户询问形式，例如：不同的词汇、句式或描述方式。同时，为每个变体提供稳健的答案，确保这些答案能够适应不同的场景，并涵盖可能的边界情况，如：延迟处理、费用支付、数据获取等。
生成要求：
问题变体: 生成不少于 5 种不同的问法，每个问题跟回答应保持原始意图但使用不同的表达方式。
稳健答案: 为每个问题提供适应各种场景的答案。答案应全面且考虑到边界情况，例如新手指南、处理延迟、费用问题、批次状态变化等。
答案覆盖: 确保答案覆盖以下情况：
批次未能按时完成的处理方式。
已完成和未完成请求的区别。
用户如何获取已完成请求的结果。
费用相关的处理细节。
保持一致性: 确保所有生成的问题和答案在意图和核心内容上与原始问答保持一致，不偏离主题。

必须遵守的约束：
你的回答必须严格符合上述JSON格式。
请确保输出JSON是有效的，不包含任何语法错误或不完整的内容。

直接返回一个JSON格式的QA列表。示例：[{\"question\": \"...\", \"answer\": \"...\"}]
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
    
    input_path = args.input_path or fileutils.get_cache_dir("qa_judge_output") + "/good_qa.json"
    
    if not input_path or not os.path.exists(input_path.split("|")[0]):
        raise ValueError("请输入有效的待处理的qa-json列表文件")
    
    # 输出目录
    output_dir = args.output_dir or fileutils.get_cache_dir("zh_batch_input_files")
    # batch qa的保存路径
    batch_qa_path = os.path.join(output_dir, "all_good_qa_batch.jsonl")
    # batch qa的保存路径 - 切割100条数据作为测试
    batch_qa_path_test100 = os.path.join(output_dir, "all_good_qa_batch_test100.jsonl")
    
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
