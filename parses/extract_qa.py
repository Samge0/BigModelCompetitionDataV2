#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# author：samge
# date：2024-08-31 21:20
# describe：从markdown文档中提取qa格式的文本

import os
import re
from utils import fileutils, timeutils


@timeutils.monitor
def extract_qa_from_markdown(filename, markdown_text) -> list:
    
    tmp_split_tag = '|||'
    markdown_text = re.sub(r'#+', tmp_split_tag, markdown_text)
    lst = markdown_text.split(tmp_split_tag)
    
    title_prefix = markdown_text.split('\n')[0].replace(tmp_split_tag, '').strip()

    # 将提取的标题和内容块拆分为问答格式
    qa_datas = []
    for match in lst:
        lines = match.strip().split('\n')
        question = lines[0].strip()  # 取第一行作为问题
        answer = '\n'.join(lines[1:]).strip()  # 取标题后的内容作为答案
        
        if not question or not answer:
            continue
        
        qa_datas.append({'question': f"{filename.split('.')[0]}-{title_prefix}-{question}", 'answer': answer})

    return qa_datas


if __name__ == '__main__':
    
    data_dir = fileutils.data_dir
    save_path = fileutils.get_cache_dir() + "/qa.json" 
    
    # 使用 glob 模块获取所有 .md 文件
    doc_files = fileutils.get_files(data_dir, 'txt,md') or []

    file_total = len(doc_files)
    if file_total == 0:
        raise ValueError(f"在 {data_dir} 目录下没有找到符合要求文档文件") 
    
    result_lst = []
    # 打印找到的所有 .md 文件
    for i in range(file_total):
        
        file_path = doc_files[i]
        file_path = file_path.replace(os.sep, '/')
        filename = os.path.basename(file_path)
        
        timeutils.print_log(f"【{i+1}/{file_total}】正在处理：{file_path}")
        
        text = fileutils.read(file_path)
        # 提取 QA 数据
        qa_datas = extract_qa_from_markdown(filename, text)
        
        result_lst += qa_datas

        # 打印提取的 QA 数据
        for qa in qa_datas:
            print(f"Q: {qa['question']}")
            print(f"A: {qa['answer']}\n")

    # 保存json数据
    fileutils.save_json(save_path, result_lst)
    
    timeutils.print_log("\nall done")