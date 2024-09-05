#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# author：samge
# date：2024-08-23 11:10
# describe：


import glob
import json
import os


# 项目根目录
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))).replace(os.sep, '/')

# data目录
data_dir = f"{root_dir}/datas"

# prompts目录
prompts_dir = f"{root_dir}/prompts"


def get_cache_dir(sub_dir=""):
    cache_dir = f"{root_dir}/.cache"
    if sub_dir:
        cache_dir = f"{cache_dir}/{sub_dir}"
    os.makedirs(cache_dir, exist_ok=True)
    return cache_dir

def read(filepath):
    if not os.path.exists(filepath):
        return None
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()

def save(filepath, content, mode='w'):
    file_dir = os.path.dirname(filepath)
    if not os.path.exists(file_dir):
        os.makedirs(file_dir, exist_ok=True)
    with open(filepath, mode, encoding='utf-8') as f:
        f.write(content)

def save_json(filepath, dict_data, mode='w'):
    file_dir = os.path.dirname(filepath)
    if not os.path.exists(file_dir):
        os.makedirs(file_dir, exist_ok=True)
    with open(filepath, mode, encoding='utf-8') as f:
        json.dump(dict_data, f, ensure_ascii=False, indent=4)

def save_jsonl(filepath, json_list, mode='w'):
    file_dir = os.path.dirname(filepath)
    if not os.path.exists(file_dir):
        os.makedirs(file_dir, exist_ok=True)
    # 打开文件并逐行写入 JSON 对象
    with open(filepath, mode, encoding='utf-8') as file:
        for entry in json_list:
            json_line = json.dumps(entry, ensure_ascii=False)
            file.write(json_line + '\n')

# 读取 jsonl 文件的函数
def read_jsonl(file_path):
    data = []
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            try:
                data.append(json.loads(line))
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON: {e}")
    return data        

def read_json(filepath):
    if not os.path.exists(filepath):
        return None
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"read_json {filepath} 时出错，错误信息：{e}")
        return None

def get_files(doc_dir, doc_suffix) -> list:
    """
    Get all files in the specified directory and its subdirectories.

    This function searches for files with specified extensions in the
    directory specified by `doc_dir` and its subdirectories.

    Parameters:
        doc_dir (str): The directory to search for files.
        doc_suffix (str): The file extensions to search for, separated by comma.

    Returns:
        list: A list of file paths.

    Raises:
        ValueError: If the specified directory does not exist.
    """
    
    if not os.path.exists(doc_dir):
        raise ValueError(f"文档目录（{doc_dir}）不存在")
    
    all_files = []
    
    for ext in doc_suffix.split(','):
        # 使用递归通配符 ** 搜索子目录中的文件
        files = glob.glob(f'{doc_dir}/**/*.{ext.strip()}', recursive=True)
        all_files.extend(files)

    return all_files 


def need_calculate_lines(filepath) -> bool:
    """
    Determine whether the lines of the given file need to be calculated.

    Args:
        filepath (str): The path of the file.

    Returns:
        bool: True if the lines of the file need to be calculated, False otherwise.
    """
    if not filepath:
        return False
    suffix_lst = "txt,md,html".split(",")
    return filepath.split(".")[-1].lower() in suffix_lst


def get_file_lines(file_path) -> int:
    """
    Get the number of lines in a file.

    Args:
        file_path (str): The path of the file.

    Returns:
        int: The number of lines in the file. If an error occurs while
        opening or reading the file, returns 0.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return len(f.readlines())
    except Exception as e:
        print(f"打开文件 {file_path} 时出错，错误信息：{e}")
        return 0
    