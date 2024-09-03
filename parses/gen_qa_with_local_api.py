#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# author：samge
# date：2024-09-02 14:00
# describe：使用智谱的api对文本进行QA提取


import json
import os
import configs
from parses import qa_models, qautils
from utils import fileutils, timeutils


api_client = None

def get_api_client(api_key=None):
    global api_client
    if not api_client:
        api_client = qa_models.ChatMessageAPI(
            base_url=f'{configs.API_URL}/chat-messages',
            api_key=api_key or configs.AUTHORIZATION
        )
    return api_client


@timeutils.monitor
def extract(query):
    """
    对输入的内容输出qa格式的增强文本

    :param query: 需要进行增强的文本
    :return: 
    """
    result = get_api_client().send_chat_message(
        query=query,
        user=configs.USER_NAME,
    )
    return result


def gen_qa_list(text, prompt):
    query = f"{text}\n\n{prompt}"
    try:
        return extract(query) 
    except Exception as e:
        timeutils.print_log(f"gen_qa_lists error: {e}\ntext[:100]...", )
        return None


if __name__ == '__main__':
    save_path = fileutils.get_cache_dir() + "/qa_api_result_local.json"
    qa_api_results = json.loads(fileutils.read(save_path) or "[]")
    
    file_suffix = "txt,md"
    filepath_list = fileutils.get_files(fileutils.data_dir, file_suffix) + fileutils.get_files(fileutils.get_cache_dir("zp_docs/markdown"), file_suffix) + fileutils.get_files(fileutils.get_cache_dir("zp/markdown"), file_suffix)
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
                if not qa_list:
                    continue
                
                if qautils.IS_COMBINE:
                     # 拼装qa列表，为了后续组装历史问答类型的qa
                    qa_list.insert(0, {"question": f"请阅读我提供给你的这篇文档（{os.path.basename(filepath)}），然后回答相关问题", "answer": "好的，我将会为您解答相关问题。"})
                    qa_api_results.append(qa_list) 
                else:
                    qa_api_results += qa_list # 拼装独立的qa
                
                fileutils.save_json(save_path, qa_api_results)
                
    timeutils.print_log("\nall done")
