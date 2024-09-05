#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# author：samge
# date：2024-09-05 14:31
# describe：QA增强 - 在dify中部署的含有知识库的应用，调用api输入一个qa字符文本，自动从多角度扩散，增强数据，返回新的QA列表

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
            api_key=configs.AUTHORIZATION_QA_ROBUSTNESS
        )
    return api_client


@timeutils.monitor
def extract(query):
    try:
        result = get_api_client().send_chat_message(
            query=query,
            user=configs.USER_NAME,
            json_format=True
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
    
    input_path = args.input_path or fileutils.get_cache_dir("qa_judge_output") + "/good_qa.json"
    
    if not input_path or not os.path.exists(input_path.split("|")[0]):
        raise ValueError("请输入有效的待处理的qa-json列表文件")
    
    # 输出目录
    output_dir = args.output_dir or fileutils.get_cache_dir("qa_robustness_output")
    # 独立QA保存路径
    qa_single_path = os.path.join(output_dir, "qa_single.json")
    qa_single_list = fileutils.read_json(qa_single_path) or []
    # 多轮对话的QA保存路径
    qa_messages_path = os.path.join(output_dir, "qa_messages.json")
    qa_messages_list = fileutils.read_json(qa_messages_path) or []
    
    qa_lst = []
    for filepath in input_path.split("|"):
        qa_lst.extend(fileutils.read_json(filepath) or [])
        
    qa_total = len(qa_lst or [])
    
    # 记录已处理的下标位置的缓存文件
    index_cache_file = fileutils.get_cache_dir(".index_cache_files") + "/" + os.path.basename(input_path.split("|")[0]).split('.')[0]
    # 将读取的缓存值分割并转换为整数
    i_index, = map(int, (fileutils.read(index_cache_file) or '0').split(','))
    timeutils.print_log(f"从上次处理的位置开始（起始下标为0）：i_index: {i_index}")
        
    # 遍历qa，进行数据增强
    for i in range(i_index, qa_total):
        # 记录下标位置
        fileutils.save(index_cache_file, f"{i}")
        
        qa = qa_lst[i]
        qa_str = str(qa)
        
        timeutils.print_log(f"【{i+1}/{qa_total}】正在处理{qa_str[:100]}……")
        result = extract(qa_str)
        if not result: continue
        result_list = result if isinstance(result, list) else [result]
        
        # 保存单轮QA数据
        qa_single_list.extend(result_list)
        fileutils.save_json(qa_single_path, qa_single_list)
        
        # 保存多轮QA数据
        qa_messages_list.append(result_list)
        fileutils.save_json(qa_messages_path, qa_messages_list)
        
    # fileutils.save(index_cache_file, "0")   # 全部执行完毕，重置下标索引的缓存，因为相关数据在持续生成中，这里暂时不自动重置下标缓存
    timeutils.print_log("\nall done，qa_single_list:", len(qa_single_list), "qa_messages_list:", len(qa_messages_list))
    
    
    

# 记录一下再dify中用到的【QA增强】提示词
"""
你是一位专业的AI助手，目标是帮助用户生成多个问题的变体表达，并为每个变体提供适应不同场景的稳健答案，增强鲁棒性。在处理文本格式时，请必须提取关键信息并以结构化的方式呈现。下面是原始的问答数据格式：
{\"question\": \"...\", \"answer\": \"...\"}
请生成多个变体的表达方式，使得这些问题涵盖各种可能的用户询问形式，例如：不同的词汇、句式或描述方式。同时，为每个变体提供稳健的答案，确保这些答案能够适应不同的场景，并涵盖可能的边界情况，如：延迟处理、费用支付、数据获取等。
生成要求：
问题变体: 生成不少于 5 种不同的问法，每个问题跟回答应保持原始意图但使用不同的表达方式。
稳健答案: 为每个问题提供适应各种场景的答案。答案应全面且考虑到边界情况，例如处理延迟、费用问题、批次状态变化等。
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
    