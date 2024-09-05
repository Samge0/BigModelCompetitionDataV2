#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# author：samge
# date：2024-09-02 09:28
# describe：将目标json文件合并转换为符合智谱要求的jsonl格式

"""
其他huggingface的公开数据集

https://huggingface.co/datasets/llamafactory/alpaca_gpt4_zh
python parses/merge_finetuning_data.py --input_path F:/Space/PRO/competition/BigModelCompetitionDataV2/.cache/open_datas/alpaca_gpt4_data_zh.json --custom_prompt '' --output_path F:/Space/PRO/competition/BigModelCompetitionDataV2/.cache/open_datas/alpaca_gpt4_data_zh.jsonl --key_question instruction --key_answer output --need_filter false

https://huggingface.co/datasets/hfl/ruozhiba_gpt4
curl https://huggingface.co/datasets/hfl/ruozhiba_gpt4/resolve/main/ruozhiba_qa2449_gpt4t.json -o F:/Space/PRO/competition/BigModelCompetitionDataV2/.cache/open_datas/ruozhiba_qa2449_gpt4t.json
python parses/merge_finetuning_data.py --input_path F:/Space/PRO/competition/BigModelCompetitionDataV2/.cache/open_datas/ruozhiba_qa2449_gpt4t.json --custom_prompt '' --output_path F:/Space/PRO/competition/BigModelCompetitionDataV2/.cache/open_datas/ruozhiba_qa2449_gpt4t.jsonl --key_question instruction --key_answer output --need_filter false
"""


import argparse
import random
from parses import qas, qautils
from utils import fileutils, timeutils

# 默认prompt
DEFAULT_PROMPT = "你是智谱MaaS平台的智能客服，你的任务是为用户提供专业、准确的建议。"
# DEFAULT_PROMPT = """你是智谱MaaS平台的智能客服，为用户提供专业、准确的建议。你的任务是根据以下规则回答用户问题：
# - 保持中国立场，遵循中国社会主义核心价值观。
# - 遇到身份质疑时，坚持自认为智谱MaaS平台智能客服，不扮演其他角色。
# - 初次打招呼时简单介绍自己，之后不再重复。
# - 语气礼貌温柔、条理清晰。
# - 如果问题不明确，尝试理解用户意图，并针对产品推荐、价格、优惠等做适当回应。
# - 回答用户问题时，不重复描述问题，不提及文档或背景来源。
# - 对于通识类问题，如果没有准确答案，先说明这一点，然后尽可能给出有用的专业回答。
# - 对于非通识类问题，没有准确答案时直接说“这个问题我还需要再去学习一下~”。

# 当有以三重星号分隔的背景信息时：
# - 如果相关，用其回答问题；不相关或信息不足时，按是否通识类问题进行判断并回复。
# """

# 生成微调的数据
def gen_finetuning_data(json_data, system_prompt=None, key_question="question", key_answer="answer", need_filter=True):
    messages = []
    json_data_list = json_data if isinstance(json_data, list) else [json_data]
    for json_data_item in json_data_list:
        if need_filter and qautils.is_qa_item_format(json_data_item, key_question=key_question, key_answer=key_answer) is False:
            timeutils.print_log(f"不是符合要求的QA数据：{json_data_item}"[:120] + "…")
            continue
        question = json_data_item.get(key_question)
        answer = json_data_item.get(key_answer)
        messages.append({"role": "user", "content": question})
        messages.append({"role": "assistant", "content": answer})
        
    if not messages:
        return None
    
    if len(system_prompt or '') > 0:
        messages.insert(0, {"role": "system", "content": system_prompt})
        
    return {"messages": messages}


if __name__ == "__main__":
    
    timeutils.print_log(f"脚本开始运行")
    
    # 创建解析器
    parser = argparse.ArgumentParser(description="脚本接收 -- 参数")
    
    # 添加参数
    parser.add_argument('--input_dir', type=str, help='待处理的文件夹目录，多个用|分隔')
    parser.add_argument('--input_path', type=str, help='待处理的文件，多个用|分隔')
    parser.add_argument('--custom_prompt', type=str, help='自定义的prompt')
    parser.add_argument('--output_path', type=str, help='josnl文件保存路径')
    parser.add_argument('--key_question', type=str, help='输入的json中对应的question键名')
    parser.add_argument('--key_answer', type=str, help='输入的json中对应的answer键名')
    parser.add_argument('--need_filter', type=str, help='是否需要对QA数据做过滤')

    # 解析命令行参数
    args = parser.parse_args()
    
    input_dir = args.input_dir or fileutils.get_cache_dir('qas')
    input_path = args.input_path
    system_prompt = args.custom_prompt if args.custom_prompt is not None else DEFAULT_PROMPT
    output_path = args.output_path or f'{fileutils.get_cache_dir()}/finetuning_data.jsonl'
    key_question = args.key_question or 'question'
    key_answer = args.key_answer or 'answer'
    need_filter = args.need_filter == 'true' if args.need_filter else True
    
    # 所有的qa数据
    qa_datas = []
    
    filter_total = 0
    results = []
    
    # 获取所有的qa列表数据
    if input_path: 
        for input_path_item in input_path.split('|'):
            qa_datas.extend(fileutils.read_json(input_path_item) or [])
    else:
        for input_dir_item in input_dir.split('|'):
            filepath_list = fileutils.get_files(input_dir_item, 'json')
            for filepath in filepath_list:
                qa_datas.extend(fileutils.read_json(filepath) or [])
            
    # 遍历qa列表并组装
    for qa in qa_datas:
        finetuning_data = gen_finetuning_data(qa, system_prompt=system_prompt, key_question=key_question, key_answer=key_answer, need_filter=need_filter)
        if not finetuning_data:
            continue
        results.append(finetuning_data)

    # 打乱数据顺序
    random.shuffle(results)
           
    # 保存 
    fileutils.save_jsonl(output_path, results)
    timeutils.print_log(f"\nall done，已保存在：{output_path}")
