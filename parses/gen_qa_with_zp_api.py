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
        content = content.replace("```json", "").replace("```", "")
        return json.loads(content)  
    except Exception as e:
        timeutils.print_log(f"gen_qa_lists error: {e}\ntext[:100]...", )
        return None


if __name__ == '__main__':
    
    # 创建解析器
    parser = argparse.ArgumentParser(description="脚本接收 -- 参数")
    
    # 添加参数
    parser.add_argument('--output_path', type=str, help='输出文件路径')
    parser.add_argument('--input_dir', type=str, help='待处理的文件夹目录，多个用|分隔')
    parser.add_argument('--input_path', type=str, help='待处理的文件，多个用|分隔')
    parser.add_argument('--custom_prompt', type=str, help='自定义的prompt')
    parser.add_argument('--combine', type=str, help='是否组装QA问答历史列表模式，true/false')

    # 解析命令行参数
    args = parser.parse_args()
    
    # 结果保存的文件路径
    save_path = args.output_path or fileutils.get_cache_dir() + "/qa_api_result.json"
    
    # 所有的生成结果
    qa_api_results = json.loads(fileutils.read(save_path) or "[]")
    
    # 读取的后缀
    file_suffix = "txt,md"
    
    input_dir_lst = []
    if args.input_dir:
        input_dir_lst = args.input_dir.split("|")
    elif not args.input_path:
        input_dir_lst = [
            fileutils.get_cache_dir("zp_docs/markdown"),
            fileutils.get_cache_dir("zp/markdown"),
            fileutils.data_dir
        ]
        
    filepath_list = []
    for _dir in input_dir_lst:
        filepath_list += fileutils.get_files(_dir, file_suffix)
    
    if args.input_path:
        for input_path in args.input_path.split("|"):
            filepath_list.insert(0, input_path)
    
    scope_total = len(qautils.SCOPE_LIST)
    filepath_total = len(filepath_list)
    
    # 记录已处理的下标位置的缓存文件
    index_cache_file = fileutils.get_cache_dir(".index_cache_files") + "/" + os.path.basename(save_path).split('.')[0]
    # 将读取的缓存值分割并转换为整数
    i_index, y_index, z_index = map(int, (fileutils.read(index_cache_file) or '0,0,0').split(','))
    timeutils.print_log(f"从上次处理的位置开始（起始下标为0）：i_index: {i_index}, y_index: {y_index}, z_index: {z_index}")
    
    # 如果有自定义提示，则不需要根据默认的scope进行拼接
    if args.custom_prompt:
        i_index = 0
        scope_total = 1
        
    # 是否组装
    is_combine = args.combine == "true" if args.combine else qautils.IS_COMBINE
    
    # 使用集合来跟踪已经添加的问题
    existing_qa_infos = set()
    
    for i in range(i_index, scope_total):
        scope = qautils.SCOPE_LIST[i]
        prompt = args.custom_prompt or f"{scope}{qautils.COMMON_TIP}"
        
        for y in range(y_index, filepath_total):
            filepath = filepath_list[y]
            doc_list = qautils.split_document(fileutils.read(filepath))
            doc_total = len(doc_list)
            
            for z in range(z_index, doc_total):
                # 记录下标位置
                fileutils.save(index_cache_file, f"{i},{y},{z}")
                
                text = doc_list[z]
                timeutils.print_log(f"【{i+1}/{scope_total}】【{y+1}/{filepath_total}】【{z+1}/{doc_total}】正在处理{filepath}的分块：{text[:100]}……")
                
                qa_list = gen_qa_list(text, prompt) or []
                if not qa_list or not isinstance(qa_list, list):
                    continue
                
                if is_combine:
                     # 拼装qa列表，为了后续组装历史问答类型的qa
                    qa_list.insert(0, {"question": f"请阅读我提供给你的这篇文档（{os.path.basename(filepath)}），然后回答相关问题", "answer": "好的，我将会为您解答相关问题。"})
                    qa_api_results.append(qa_list) 
                else:
                    # 拼装独立的qa
                    for qa in qa_list:
                        question = qa.get("question")
                        answer = qa.get("answer")
                        if question in existing_qa_infos or answer in existing_qa_infos:
                            timeutils.print_log("已存在该Q/A，跳过：" + question)
                            continue
                        # 如果问题不在集合中，才添加到结果列表，并且更新集合
                        qa_api_results.append(qa)
                        existing_qa_infos.add(question)
                        existing_qa_infos.add(answer)
                
                fileutils.save_json(save_path, qa_api_results)
            z_index = 0
        y_index = 0
                
    fileutils.save(index_cache_file, "0,0,0")   # 全部执行完毕，重置下标索引的缓存
    timeutils.print_log("\nall done")
