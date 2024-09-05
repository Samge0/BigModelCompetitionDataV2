## BigModelCompetitionDataV2
智谱模型微调比赛的测试脚本，仅用来记录一些数据的获取与测试

[点击查看比赛说明>>](tips/比赛说明.md)

[点击查看比赛提供的默认prompt>>](prompts/prompt.md)

### 创建env环境
```shell
conda create -n BigModelCompetitionDataV2 python=3.10.13 -y
```

### 安装依赖
```shell
pip install -r requirements.txt
```

## 复制并配置[configs.py](configs.py)
```shell
cp configs.demo.py configs.py
```

### 运行

- 抓取智谱的新闻通告页面数据
    ```shell
    python crawlers/crawl_news.py
    ```

- 抓取智谱的使用文档&api文档页面数据
    ```shell
    python crawlers/crawl_docs.py
    ```

- 将比赛提供的几个默认文档数据提取为QA格式数据
    ```shell
    python parses/extract_qa.py
    ```

- 遍历已有的QA数据，调用dify中的接口获取增强的QA数据
    ```shell
    python parses/gen_enhance_qa.py
    ```

- 遍历抓取的文档并根据指定长度切片，调用dify中的接口获取增强的QA数据
    ```shell
    python parses/gen_enhance_qa_by_split_doc.py
    ```

- 使用智谱的api提取文本块中的qa列表信息
    ```shell
    python parses/gen_qa_with_zp_api.py
    ```

    可以指定输入路径、输出路路径
    ```shell
    python parses/gen_qa_with_zp_api.py --input_dir xxx/xxx|yyy/yyy --output_path xxx/xxx.json
    ```

- 使用本地的api（这里默认用的dify+ollama+qwen2的组合）提取文本块中的qa列表信息
    ```shell
    python parses/gen_qa_with_local_api.py
    ```

    可以指定输入路径、输出路路径
    ```shell
    python parses/gen_qa_with_local_api.py --input_dir xxx/xxx|yyy/yyy --output_path xxx/xxx.json
    ```

- 将指定目录下的所有qa数据合并为符合微调要求的格式，[参考>>](https://bigmodel.cn/dev/howuse/finetuning/dataset)
    ```shell
    python parses/merge_finetuning_data.py
    ```

### 相关截图
![image](https://github.com/user-attachments/assets/f292cf88-b255-4bba-992f-aa3fdcb73bb8)
![image](https://github.com/user-attachments/assets/1201ad3b-a9af-419c-aaaa-b4da1c7ae032)
![image](https://github.com/user-attachments/assets/965492dc-33ba-44f3-8a48-014345995b1f)
![image](https://github.com/user-attachments/assets/f9166fae-0cd2-45bf-9588-f5b57784078a)
![image](https://github.com/user-attachments/assets/9ee323a9-8559-4c1e-9434-550434600028)



