#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# author：samge
# date：2024-09-02 14:00
# describe：使用智谱的api对文本进行QA提取
import argparse
import json
import os
from zhipuai import ZhipuAI
import configs
from parses import qautils
from utils import fileutils, timeutils


zhipu_client = None


def get_zhipu_client():
    global zhipu_client
    if zhipu_client is None:
        zhipu_client = ZhipuAI(api_key=configs.ZHI_PU_API_KEY)
    return zhipu_client


def gen_qa_list(text, prompt):
    try:
        response = get_zhipu_client().chat.completions.create(
            model=configs.ZHI_PU_MODEL,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": text},
            ],
            stream=False,
            max_tokens=2095,
            temperature=0.95,
            top_p=0.70,
        )
        content = response.choices[0].message.content
        content = content.replace("\n", " ").replace("```json", "").replace("```", "")
        return json.loads(content)  
    except Exception as e:
        timeutils.print_log(f"gen_qa_lists error: {e}\ntext[:100]...", )
        return None


if __name__ == '__main__':
    
     # 创建解析器
    parser = argparse.ArgumentParser(description="示例脚本接收 -- 参数")
    
    # 添加参数
    parser.add_argument('--output_path', type=str, help='输出文件路径')
    parser.add_argument('--input_dir', type=str, help='待处理的文件夹目录，多个用|分隔')

    # 解析命令行参数
    args = parser.parse_args()
    
    save_path = args.output_path or fileutils.get_cache_dir() + "/qa_api_result.json"
    qa_api_results = json.loads(fileutils.read(save_path) or "[]")
    
    file_suffix = "txt,md"
    
    input_dir_lst = []
    if args.input_dir:
        input_dir_lst = args.input_dir.split("|")
    else:
        input_dir_lst = [
            fileutils.get_cache_dir("zp_docs/markdown"),
            fileutils.get_cache_dir("zp/markdown"),
            fileutils.data_dir
        ]
        
    filepath_list = []
    for _dir in input_dir_lst:
        filepath_list += fileutils.get_files(_dir, file_suffix)
    
    scope_total = len(qautils.SCOPE_LIST)
    filepath_total = len(filepath_list)
    
    for i in range(scope_total):
        scope = qautils.SCOPE_LIST[i]
        prompt = scope + qautils.COMMON_TIP
        
        for y in range(filepath_total):
            filepath = filepath_list[y]
            doc_list = qautils.split_document(fileutils.read(filepath))
            doc_total = len(doc_list)
            
            for z in range(doc_total):
                text = doc_list[z]
                timeutils.print_log(f"【{i+1}/{scope_total}】【{y+1}/{filepath_total}】【{z+1}/{doc_total}】正在处理{filepath}的分块：{text[:100]}……")
                
                qa_list = gen_qa_list(text, prompt) or []
                if not qa_list or not isinstance(qa_list, list):
                    continue
                
                if qautils.IS_COMBINE:
                     # 拼装qa列表，为了后续组装历史问答类型的qa
                    qa_list.insert(0, {"question": f"请阅读我提供给你的这篇文档（{os.path.basename(filepath)}），然后回答相关问题", "answer": "好的，我将会为您解答相关问题。"})
                    qa_api_results.append(qa_list) 
                else:
                    qa_api_results += qa_list # 拼装独立的qa
                
                fileutils.save_json(save_path, qa_api_results)
                
    timeutils.print_log("\nall done")
