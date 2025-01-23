# 微信公众号转小红书工具

这是一个能够将微信公众号文章自动转换为小红书风格并发布的工具。

## 功能特点

- 自动抓取微信公众号文章内容和图片
- 使用 OpenAI API 将文本转换为小红书风格
- 自动发布内容到小红书平台

## 项目结构

```
.
├── weixin_crawler.py   # 微信文章抓取模块
├── xhs_converter.py    # 小红书内容转换模块
├── xhs_publisher.py    # 小红书发布模块
├── requirements.txt    # 项目依赖
└── .env               # 环境变量配置
```

## 安装步骤

1. 创建虚拟环境：
```bash
python -m venv venv
```

2. 激活虚拟环境：
```bash
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. 安装依赖：
```bash
pip install -r requirements.txt
```

4. 配置环境变量：
创建 `.env` 文件并添加以下内容：
```
OPENAI_API_KEY=your_openai_api_key_here
```

## 使用方法

1. 抓取微信文章：
```bash
python weixin_crawler.py
```

2. 转换为小红书风格：
```bash
python xhs_converter.py
```

3. 发布到小红书：
```bash
python xhs_publisher.py
```

## 注意事项

- 需要 Python 3.7 或更高版本
- 需要 OpenAI API 密钥
- 首次发布到小红书时需要手动登录
- 请遵守相关平台的使用规则和版权规定

## 数据保存

抓取的内容将保存在 `data` 目录下，结构如下：
```
data/
└── 文章标题/
    ├── original.txt      # 原始文章内容
    ├── xiaohongshu.txt  # 转换后的小红书内容
    └── images/          # 图片目录
        ├── image_1.jpg
        └── ...
```

## 待完善功能

- [ ] 完善小红书发布API的实现
- [ ] 添加更多文案风格转换选项
- [ ] 支持批量处理多篇文章
- [ ] 添加更多图片滤镜效果 