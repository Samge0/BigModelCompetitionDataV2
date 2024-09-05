#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# author：samge
# date：2024-09-05 16:42
# describe：处理智谱批量任务的jsonl文件（QA增强）的生成结果

"""
返回的jsonl文件格式如下：
{"response":{"status_code":200,"body":{"created":1725532787,"usage":{"completion_tokens":386,"prompt_tokens":377,"total_tokens":763},"model":"glm-4-0520","id":"8994562567833972547","choices":[{"finish_reason":"stop","index":0,"message":{"role":"assistant","content":"```json\n[\n  {\n    \"question\": \"Batch API是用来做什么的？\",\n    \"answer\": \"Batch API是一种批量处理工具，适用于处理不需要即时响应的大规模请求。用户可以通过它提交任务，系统将在24小时内处理完毕并返回结果。针对未能按时完成的批次，我们会提供相应的处理方案。如果涉及到费用，将根据实际使用的资源进行计算。\"\n  },\n  {\n    \"question\": \"如何使用Batch API处理大量任务？\",\n    \"answer\": \"使用Batch API，用户可以上传包含多个任务的文件，系统会在24小时内处理这些任务。已完成和未完成的请求可以通过API的状态查询功能来区分。获取结果时，用户需要通过请求ID来下载相应的结果文件。如果遇到延迟，我们会提供补偿措施。\"\n  },\n  {\n    \"question\": \"Batch API处理任务的时效是多久？\",\n    \"answer\": \"Batch API承诺在24小时内完成任务的处理。如果任务未能按时完成，我们会通知用户并提供后续的处理方案。对于已完成任务的结果获取，用户可以通过API提供的接口进行下载。费用方面，会按照实际资源使用情况进行收费。\"\n  },\n  {\n    \"question\": \"Batch API完成任务后如何获取结果？\",\n    \"answer\": \"一旦Batch API处理完任务，用户可以通过提供的API接口，使用请求ID来获取结果文件。如果任务未能按时完成，我们会提供解决方案。需要注意的是，获取结果不额外收费，但提交任务时可能会产生一定的费用。\"\n  },\n  {\n    \"question\": \"使用Batch API需要支付哪些费用？\",\n    \"answer\": \"使用Batch API时，用户需根据实际使用的资源支付费用。这包括处理任务所需的计算资源和存储资源。如果批次未能按时完成，不会产生额外费用，我们会根据情况提供补偿。用户可以通过API获取费用详情和处理状态。\"\n  }\n]\n```"}}],"request_id":"request-0"}},"custom_id":"request-0","id":"batch_1831642912733933568"}
"""

import argparse
import json
import os
from utils import fileutils, timeutils

# 是否每次轮询保存一次，True=每次都保存，False=执行完毕后保存一次即可（避免反复写入的耗时）
save_every_polling = False
# 是否打印每次轮询的log
print_every_polling_log = False


if __name__ == '__main__':
    
    # 创建解析器
    parser = argparse.ArgumentParser(description="脚本接收 -- 参数")
    
    # 添加参数
    parser.add_argument('--origin_qa_path', type=str, help='待处理的原始qa-json列表文件')
    parser.add_argument('--batch_result_jsonl_path', type=str, help='智谱批处理执行完毕后返回的jsonl文件')
    parser.add_argument('--output_dir', type=str, help='输出目录')

    # 解析命令行参数
    args = parser.parse_args()
    
    origin_qa_path = args.origin_qa_path or fileutils.get_cache_dir("qa_judge_output") + "/good_qa.json"
    batch_result_jsonl_path = args.batch_result_jsonl_path or fileutils.get_cache_dir("qa_judge_output") + "/good_qa_batch_result.jsonl"
    
    if not origin_qa_path or not os.path.exists(origin_qa_path):
        raise ValueError("请输入有效的 待处理的原始qa-json列表文件")
    
    if not batch_result_jsonl_path or not os.path.exists(batch_result_jsonl_path):
        raise ValueError("请输入有效的 智谱批处理执行完毕后返回的jsonl文件")
    
    # 输出目录
    output_dir = args.output_dir or fileutils.get_cache_dir("qa_robustness_output")
    # 独立QA保存路径
    qa_single_path = os.path.join(output_dir, "qa_single.json")
    qa_single_list = fileutils.read_json(qa_single_path) or []
    # 多轮对话的QA保存路径
    qa_messages_path = os.path.join(output_dir, "qa_messages.json")
    qa_messages_list = fileutils.read_json(qa_messages_path) or []
    
    qa_lst = fileutils.read_json(origin_qa_path) or []
    qa_total = len(qa_lst)
    
    qa_result_lst = fileutils.read_jsonl(batch_result_jsonl_path) or []
    qa_result_total = len(qa_result_lst)
    
    timeutils.print_log(f"正在处理{qa_result_total}条数据，请稍后……")
        
    # 遍历qa，进行数据增强
    for i in range(qa_result_total):
        if print_every_polling_log:
            timeutils.print_log(f"【{i+1}/{qa_result_total}】正在处理……")
        
        qa_result = qa_result_lst[i]
        custom_id = qa_result.get("custom_id")
        real_index = int(custom_id.replace("request-", ""))
        
        # 解析真实的索引
        if real_index >= qa_total:
            timeutils.print_log(f"real_index({real_index}) >= qa_total({qa_total}), skip")
            continue
        qa = qa_lst[real_index]
        
        # 解析生成的结果列表
        result_content = qa_result.get("response").get("body").get("choices")[0].get("message").get("content")
        result_content = result_content.replace("```json", "").replace("```", "")
        try:
            result_list = json.loads(result_content)
        except Exception as e:
            continue
        
        # 保存单轮QA数据
        qa_single_list.extend(result_list)
        if save_every_polling:
            fileutils.save_json(qa_single_path, qa_single_list)
        
        # 保存多轮QA数据
        qa_messages_list.append(result_list)
        if save_every_polling:
            fileutils.save_json(qa_messages_path, qa_messages_list)
        
    
    # 最后保存一次
    if not save_every_polling:
        fileutils.save_json(qa_single_path, qa_single_list)
        fileutils.save_json(qa_messages_path, qa_messages_list)
        
    timeutils.print_log("\nall done，qa_single_list:", len(qa_single_list), "qa_messages_list:", len(qa_messages_list))
    
    