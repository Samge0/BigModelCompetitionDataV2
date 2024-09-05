#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# author：samge
# date：2024-09-05 20:25
# describe：

import hashlib

def calculate_md5(input_string):
    # 创建一个 md5 对象
    md5_obj = hashlib.md5()
    # 更新对象以包含输入字符串的字节
    md5_obj.update(input_string.encode('utf-8'))
    # 返回十六进制格式的哈希值
    return md5_obj.hexdigest()


if __name__ == "__main__":
    # 示例用法
    input_data = "Hello, World!"
    md5_hash = calculate_md5(input_data)
    print(f"The MD5 hash of '{input_data}' is: {md5_hash}")
