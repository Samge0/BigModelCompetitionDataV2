#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# author：samge
# date：2024-09-02 09:28
# describe：


from parses import qas
from utils import fileutils, timeutils

# 目标目录位置
GOAL_DIR = fileutils.get_cache_dir('qas')

# 需要过滤的关键词
leaders = [
    "习近平", "李强", "赵乐际", "王沪宁", "蔡奇", "丁薛祥", "李希",
    
    "李克强", "栗战书", "汪洋", "王岐山", "胡锦涛", "温家宝", 
    "吴邦国", "贾庆林", "曾庆红", "朱镕基", "李鹏", "乔石",
    
    "江泽民", "邓小平", "胡耀邦", "华国锋", "周恩来", 
    "毛泽东", "刘少奇", "林彪", "彭德怀", "陈云", 
    "李先念", "叶剑英", "董必武", "张闻天", "陈独秀",
    
    "宋庆龄", "张澜", "李济深", "何香凝", "冯玉祥",
    
    "聂荣臻", "徐向前", "罗荣桓", "贺龙", "叶挺", "粟裕", "刘伯承", "邓子恢", 
    
    "习仲勋", "薄一波", "田纪云", "王震", "宋平", "尉健行", "黄菊", "李瑞环"
]
FILTER_WORDS = ['鸭', 'by_train', 'by_car', '中国队'] + leaders


def is_int(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

# 是否如何要求的数据格式
def is_qa_item_format(item):
    
    question = item.get('question') or ''
    answer = item.get('answer') or ''
    
    is_ok = isinstance(item, dict) \
        and 'question' in item and 'answer' in item \
        and len(question) >= 6 and (len(answer) >= 10 or is_int(answer)) \
        and answer != '{search_result}'
        
    if not is_ok:
        return False
        
    for key in FILTER_WORDS:
        if (key in question and '你好' not in question) or (key in answer and 'description": "交通方式，' not in answer):
            return False
        
    return is_ok


# 生成微调的数据
def gen_finetuning_data(question, answer, need_default_prompt=True):
    messages = []
    if need_default_prompt:
        messages.append({"role": "system", "content": "你是智谱MaaS平台的智能客服，你的任务是为用户提供专业、准确的建议。"})
    messages.append({"role": "user", "content": question})
    messages.append({"role": "assistant", "content": answer})
    return {"messages": messages}


if __name__ == "__main__":
    
    filter_total = 0
    results = []
    json_list = fileutils.get_files(GOAL_DIR, 'json')
    for json_path in json_list:
        json_str = fileutils.read(json_path)
        json_datas = qas.load_json(json_str)
        for json_data in json_datas:
            if is_qa_item_format(json_data) is False:
                timeutils.print_log("不符合要求的数据，跳过：", json_data)
                filter_total += 1
                continue
            
            question = json_data.get('question')
            answer = json_data.get('answer')
            results.append(gen_finetuning_data(question, answer))
            
    save_path = f'{fileutils.get_cache_dir()}/finetuning_data.jsonl'
    fileutils.save_jsonl(save_path, results)
    
    timeutils.print_log("\nall done，共移除", filter_total, "条不符合要求的数据")
