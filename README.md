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
