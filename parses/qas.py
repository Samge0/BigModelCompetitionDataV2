#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# author：samge
# date：2024-08-30 15:30
# describe：对文本进行增强

import json
import os
import configs
from parses import qa_models, qautils
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
        json_format=True
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


def generate_enhanced_text(save_path: str, doc_list: list, curr_times: int = 0, max_times: int = 50, y_index: int=0, index_cache_file: str=None):
    
    """
    生成增强后的qa列表

    :param save_path: 生成的数据保存的路径
    :param doc_list: 需要进行增强的qa列表
    
    :param curr_times: 仅供内部打印日志使用，当前已经生成的次数
    :param max_times: 仅供内部打印日志使用，最大生成次数
    :param y_index: 仅供内部使用，表示最后一次处理的下标
    :param index_cache_file: 仅供内部使用，表示记录已处理的下标位置的缓存文件
    
    :return:
    """

    gen_result_list = load_json(fileutils.read(save_path) or '[]')
    qa_list_total = len(doc_list)
    for y in range(y_index, qa_list_total):
        if index_cache_file:
            fileutils.save(index_cache_file, f"{curr_times},{y}")
        
        _text = doc_list[y]
        
        times_tip = f"【{curr_times}/{max_times}】" if curr_times > 0 else ""
        timeutils.print_log(f"{times_tip}【{y+1}/{qa_list_total}】正在生成增强文本，{_text[:100]}……")
        
        result = extract(str(_text))
        if isinstance(result, list):
            for qa_item in result:
                if not qautils.is_qa_item_format(qa_item):
                    continue
                gen_result_list.append(qa_item)
        elif isinstance(result, dict):
            if qautils.is_qa_item_format(qa_item):
                gen_result_list.append(result)
                
        fileutils.save_json(save_path, gen_result_list)
    pass


if __name__ == "__main__":
    result = extract("""{'question': '如何划分速率限制的等级？', 'answer': '当前我们基于用户的月度 API 调用消耗金额情况将速率控制分为6种等级。具体来说，根据用户的月度 API 消耗金
额，我们可以划分出不同的使用级别：免费、用量级别1至5。'}""")
    print(result)
    