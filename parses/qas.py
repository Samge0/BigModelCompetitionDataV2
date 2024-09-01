#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# author：samge
# date：2024-08-30 15:30
# describe：对文本进行增强

import json
import configs
from parses import qa_models
from utils import fileutils, timeutils


@timeutils.monitor
def extract(query):
    """
    对输入的内容输出qa格式的增强文本

    :param query: 需要进行增强的文本
    :return: 
    """
    result = qa_models.get_api_client().send_chat_message(
        query=query,
        user=configs.USER_NAME,
    )
    return result


def load_json(value):
    """
    将json文本解析为Python对象

    :param text: 需要解析的json文本
    :return: 解析后的Python对象
    """
    try:
        if type(value) == dict or type(value) == list:
            return value
        return json.loads(value)
    except json.JSONDecodeError:
        return None


def generate_enhanced_text(save_path: str, qa_list: list):
    """
    对 qa_list 中的每个问题进行 max_times 次增强文本提取

    :param save_path: 保存增强文本的文件路径
    :param qa_list: 需要进行增强的 qa 列表
    :return: 
    """
    gen_result_list = load_json(fileutils.read(save_path) or '[]')
    qa_list_total = len(qa_list)
    for y in range(qa_list_total):
        qa_item = qa_list[y]
        
        check_item_format = isinstance(qa_item, dict) and 'question' in qa_item and 'answer' in qa_item
        if check_item_format is False:
            continue
        
        timeutils.print_log(f"【{y+1}/{qa_list_total}】正在生成增强文本，Q: {qa_item['question']}, A: {qa_item['answer'][:20]}……")
        
        result = extract(str(qa_item))
        if not result:
            timeutils.print_log(f"【{y+1}/{qa_list_total}】生成失败，跳过")
            continue
        
        gen_result_list.append(result)
        fileutils.save_json(save_path, gen_result_list)
    pass


if __name__ == "__main__":
    result = extract("""{'question': '如何划分速率限制的等级？', 'answer': '当前我们基于用户的月度 API 调用消耗金额情况将速率控制分为6种等级。具体来说，根据用户的月度 API 消耗金
额，我们可以划分出不同的使用级别：免费、用量级别1至5。'}""")
    print(result)
    