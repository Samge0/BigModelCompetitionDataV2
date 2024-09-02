#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# author：samge
# date：2024-09-02 14:00
# describe：使用智谱的api对文本进行QA提取


# 提问的范围列表
import json
import re
from zhipuai import ZhipuAI
import configs
from utils import fileutils, timeutils


scope_list = [
    "你是专业且温柔的客服，帮忙根据提供的文本提取专业且温柔的广泛的问题和答案，涵盖内容的主要概念、定义和大致用途。确保问题涵盖文本的核心信息。",
    "你是专业且温柔的客服，帮忙根据提供的文本提取专业且温柔的更细致的QA对，重点关注具体内容、步骤、注意事项和细节，尽可能细致地提问。",
    "你是专业且温柔的客服，帮忙根据提供的文本提取专业且温柔的针对不同受众（如初学者、专家、普通用户、付费用户、开发者或其他特定行业人员）的QA对，确保问题从不同的视角进行提问。",
    "你是专业且温柔的客服，帮忙根据提供的文本提取专业且温柔的QA对，重点关注定义和基本概念，确保问题涵盖核心定义和基本解释。",
    "你是专业且温柔的客服，帮忙根据提供的文本提取专业且温柔的更细致的QA对，重点关注具体内容和组成部分，挖掘详细信息。",
    "你是专业且温柔的客服，帮忙根据提供的文本提取专业且温柔的QA对，重点关注步骤和流程，详细说明操作过程和顺序。",
    "你是专业且温柔的客服，帮忙根据提供的文本提取专业且温柔的QA对，强调适用范围和条件，明确何时或在什么条件下适用。",
    "你是专业且温柔的客服，帮忙根据提供的文本提取专业且温柔的QA对，重点关注优点和好处，挖掘出有利之处。",
    "你是专业且温柔的客服，帮忙根据提供的文本提取专业且温柔的QA对，重点关注缺点和限制，识别潜在的问题或局限。",
    "你是专业且温柔的客服，帮忙根据提供的文本提取专业且温柔的QA对，突出常见问题和解决方案，帮助识别可能遇到的挑战及其应对方法。",
    "你是专业且温柔的客服，帮忙根据提供的文本提取专业且温柔的QA对，着重于使用案例和实际应用，探索现实生活中的应用场景。",
    "你是专业且温柔的客服，帮忙根据提供的文本提取专业且温柔的QA对，重点关注潜在风险和注意事项，探讨可能的风险点和规避方法。",
    "你是专业且温柔的客服，帮忙根据提供的文本提取专业且温柔的QA对，对比和比较不同选项或元素，探讨其异同点。",
    "你是专业且温柔的客服，帮忙根据提供的文本提取专业且温柔的QA对，回顾背景和历史，了解内容的起源和发展历程。",
    "你是专业且温柔的客服，帮忙根据提供的文本提取专业且温柔的QA对，聚焦于影响和效果，探讨其对相关方面的影响程度。",
    "你是专业且温柔的客服，帮忙根据提供的文本提取专业且温柔的QA对，解释相关术语和概念，帮助澄清专业术语。",
    "你是专业且温柔的客服，帮忙根据提供的文本提取专业且温柔的QA对，提供操作指南和方法，详细描述如何进行操作或实现。",
    "你是专业且温柔的客服，帮忙根据提供的文本提取专业且温柔的QA对，分享最佳实践和建议，提出实用性高的建议。",
    "你是专业且温柔的客服，帮忙根据提供的文本提取专业且温柔的QA对，关注误区和常见错误，帮助识别和避免常见的陷阱。",
    "你是专业且温柔的客服，帮忙根据提供的文本提取专业且温柔的QA对，分析影响因素和依赖性，明确哪些因素会影响结果。",
    "你是专业且温柔的客服，帮忙根据提供的文本提取专业且温柔的QA对，讨论更新和变化，探讨内容的最新变化和趋势。",
    "你是专业且温柔的客服，帮忙根据提供的文本提取专业且温柔的QA对，针对适用人群和目标受众，明确谁是主要受众或用户群。",
    "你是专业且温柔的客服，帮忙根据提供的文本提取专业且温柔的QA对，模拟情景假设和假设条件，探索假设情况下的可能性。",
    "你是专业且温柔的客服，帮忙根据提供的文本提取专业且温柔的QA对，讨论费用和成本相关，关注相关的经济因素。",
    "你是专业且温柔的客服，帮忙根据提供的文本提取专业且温柔的QA对，分析时间要求和时间表，确定所需的时间因素。",
    "你是专业且温柔的客服，帮忙根据提供的文本提取专业且温柔的QA对，探讨如何进行改进或优化，寻找提升的方法和建议。",
    "你是专业且温柔的客服，帮忙根据提供的文本提取专业且温柔的QA对，检查法律和合规性，确保内容符合相关法规。",
    "你是专业且温柔的客服，帮忙根据提供的文本提取专业且温柔的QA对，聚焦数据和统计，寻找与内容相关的数据信息。",
    "你是专业且温柔的客服，帮忙根据提供的文本提取专业且温柔的QA对，关注用户体验和反馈，挖掘用户对内容的反应和意见。",
    "你是专业且温柔的客服，帮忙根据提供的文本提取专业且温柔的QA对，讨论未来趋势和预测，探讨未来的可能走向。",
    "你是专业且温柔的客服，帮忙根据提供的文本提取专业且温柔的QA对，分析与其他选择的对比，帮助理解不同选项的优势和劣势。",
    "你是专业且温柔的客服，帮忙根据提供的文本提取专业且温柔的QA对，探讨技术细节和实现方式，了解实现过程中的技术细节。",
    "你是专业且温柔的客服，帮忙根据提供的文本提取专业且温柔的QA对，考察市场需求和竞争情况，分析当前市场的供求状况。",
    "你是专业且温柔的客服，帮忙根据提供的文本提取专业且温柔的QA对，讨论内容的重要性和深远影响，强调其重大意义。",
    "你是专业且温柔的客服，帮忙根据提供的文本提取专业且温柔的QA对，专注于挑战和解决方案，分析遇到的挑战及应对策略。",
    "你是专业且温柔的客服，帮忙根据提供的文本提取专业且温柔的QA对，探索合作与协作机会，寻找可能的合作领域。",
    "你是专业且温柔的客服，帮忙根据提供的文本提取专业且温柔的QA对，分享成功案例与失败案例，提供实战经验和教训。",
    "你是专业且温柔的客服，帮忙根据提供的文本提取专业且温柔的QA对，讨论环保和可持续性，了解其对环境的影响。",
    "你是专业且温柔的客服，帮忙根据提供的文本提取专业且温柔的QA对，分析个性化和定制化选项，讨论定制化的可能性。",
    "你是专业且温柔的客服，帮忙根据提供的文本提取专业且温柔的QA对，列出相关工具和资源，提供有助于实现目标的工具。",
    "你是专业且温柔的客服，帮忙根据提供的文本提取专业且温柔的QA对，说明如何获取支持和帮助，提供获得协助的方式。",
    "你是专业且温柔的客服，帮忙根据提供的文本提取专业且温柔的QA对，探讨下一步行动和发展方向，明确后续的可能步骤。"
]


common_tip = "answer字段请用专业且温柔的客服口吻回答。返回一个JSON格式的QA列表。示例：[{\"question\": \"...\", \"answer\": \"...\"}]"


# 将长文档拆分为小块
def split_document(document, max_length=2000):
    return [document[i:i + max_length] for i in range(0, len(document), max_length)] + [document]


def gen_qa_list(text, prompt):
    client = ZhipuAI(api_key=configs.ZHI_PU_API_KEY)
    response = client.chat.completions.create(
        model=configs.ZHI_PU_MODEL,
        messages=[
            {"role": "user", "content": prompt},
            {"role": "assistant", "content": "好的，请提供需要解析的文本，我会帮您解析为JSON格式的QA列表，且answer字段会用专业且温柔的客服口吻回答。"},
            {"role": "user", "content": text},
        ],
        stream=False,
        max_tokens=2095,
        temperature=0.95,
        top_p=0.70,
    )
    try:
        content = response.choices[0].message.content
        content = content.replace("\n", " ").replace("```json", "").replace("```", "")
        return json.loads(content)  
    except Exception as e:
        timeutils.print_log(f"gen_qa_lists error: {e}\ntext[:100]...", )
        return None


if __name__ == '__main__':
    save_path = fileutils.get_cache_dir() + "/qa_api_result.json"
    qa_api_results = json.loads(fileutils.read(save_path) or "[]")
    
    file_suffix = "txt,md"
    filepath_list = fileutils.get_files(fileutils.data_dir, file_suffix) + fileutils.get_files(fileutils.get_cache_dir("zp_docs/markdown"), file_suffix)
    scope_total = len(scope_list)
    filepath_total = len(filepath_list)
    
    for i in range(scope_total):
        scope = scope_list[i]
        prompt = scope + common_tip
        
        for y in range(filepath_total):
            filepath = filepath_list[y]
            doc_list = split_document(fileutils.read(filepath))
            doc_total = len(doc_list)
            
            for z in range(doc_total):
                text = doc_list[z]
                timeutils.print_log(f"【{i+1}/{scope_total}】【{y+1}/{filepath_total}】【{z+1}/{doc_total}】正在处理{filepath}的分块：{text[:100]}……")
                qa_list = gen_qa_list(text, prompt) or []
                if not qa_list:
                    continue
                qa_api_results += qa_list
                fileutils.save_json(save_path, qa_api_results)
                
    timeutils.print_log("\nall done")
