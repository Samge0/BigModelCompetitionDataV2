#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# author：samge
# date：2024-09-05 02:52
# describe：将某目录下.md文件转为.txt

import os
import shutil

from utils import fileutils


if __name__ == "__main__":
    # Define the directory paths
    cache_dir = fileutils.get_cache_dir()
    output_dir = os.path.join(cache_dir, "other_docs/texts")
    input_dir = fileutils.data_dir

    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Get the list of markdown files in the input directory
    lst = fileutils.get_files(input_dir, "md")

    # Iterate over each markdown file
    for filepath in lst:
        print(filepath)
        # Extract the filename without extension and change extension to .txt
        filename = os.path.basename(filepath)
        txt_filename = os.path.splitext(filename)[0] + ".txt"
        txt_filepath = os.path.join(output_dir, txt_filename)

        # Copy the markdown file content to a text file
        shutil.copyfile(filepath, txt_filepath)
        print(f"Copied to {txt_filepath}")
