#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# author：samge
# date：2024-09-05 16:42
# describe：处理智谱批量任务的jsonl文件（QA审判）的生成结果

"""
返回的jsonl文件格式如下：
{"response":{"status_code":200,"body":{"created":1725528240,"usage":{"completion_tokens":3,"prompt_tokens":252,"total_tokens":255},"model":"glm-4-0520","id":"8994562567834144886","choices":[{"finish_reason":"stop","index":0,"message":{"role":"assistant","content":"优质"}}],"request_id":"request-99"}},"custom_id":"request-99","id":"batch_1831622926102036480"}
"""

import argparse
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
    
    origin_qa_path = args.origin_qa_path or fileutils.get_cache_dir("allqas") + "/all_qa_list.json"
    batch_result_jsonl_path = args.batch_result_jsonl_path or fileutils.get_cache_dir("allqas") + "/all_qa_list_batch_result.jsonl"
    
    if not origin_qa_path or not os.path.exists(origin_qa_path):
        raise ValueError("请输入有效的 待处理的原始qa-json列表文件")
    
    if not batch_result_jsonl_path or not os.path.exists(batch_result_jsonl_path):
        raise ValueError("请输入有效的 智谱批处理执行完毕后返回的jsonl文件")
    
    # 输出目录
    output_dir = args.output_dir or fileutils.get_cache_dir("qa_judge_output")
    # 优质qa保存路径
    good_qa_path = os.path.join(output_dir, "good_qa.json")
    good_qa_list = fileutils.read_json(good_qa_path) or []
    # 丢弃qa保存路径
    bad_qa_path = os.path.join(output_dir, "bad_qa.json")
    bad_qa_list = fileutils.read_json(bad_qa_path) or []
    
    qa_lst = fileutils.read_json(origin_qa_path) or []
    qa_total = len(qa_lst or [])
    
    qa_result_lst = fileutils.read_jsonl(batch_result_jsonl_path) or []
    qa_result_total = len(qa_result_lst or [])
    
    if qa_total != qa_result_total:
        raise ValueError(f"qa_total: {qa_total} != qa_result_total: {qa_result_total}")
        
    timeutils.print_log(f"正在处理{qa_total}条数据，请稍后……")
    
    # 遍历qa，判断是否合格
    for i in range(qa_total):
        if print_every_polling_log:
            timeutils.print_log(f"【{i+1}/{qa_total}】正在处理……")
        
        qa = qa_lst[i]
        result = qa_result_lst[i].get("response").get("body").get("choices")[0].get("message").get("content")
        if not result or "优质" != result:
            bad_qa_list.append(qa)
            if save_every_polling:
                fileutils.save_json(bad_qa_path, bad_qa_list)
            continue
        
        good_qa_list.append(qa)
        if save_every_polling:
            fileutils.save_json(good_qa_path, good_qa_list)
        
    
    # 最后保存一次
    if not save_every_polling:
        fileutils.save_json(bad_qa_path, bad_qa_list)
        fileutils.save_json(good_qa_path, good_qa_list)
        
    timeutils.print_log("\nall done，good_qa_list:", len(good_qa_list), "bad_qa_list:", len(bad_qa_list))
    