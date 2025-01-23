import os
import json
import requests
from typing import Optional, Dict, Any
from dataclasses import dataclass

@dataclass
class XHSContent:
    title: str
    content: str
    save_path: str

class XHSConverter:
    def __init__(self, api_key: Optional[str] = None):
        """初始化转换器
        api_key: 大模型API密钥（如OpenAI API Key）
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("需要设置OPENAI_API_KEY环境变量或在初始化时提供api_key")
            
    def get_prompt(self, title: str, content: str) -> str:
        """生成Prompt模板"""
        return f"""请将以下文章转换成小红书风格的内容。要求：
1. 标题要吸引人，突出文章重点，并适当使用emoji
2. 开头要活泼有趣，吸引读者继续阅读
3. 正文要简明扼要，突出重点
4. 分段要清晰，每段都要有重点
5. 结尾要有总结和号召性语言
6. 适当使用emoji增加活力
7. 添加3-5个相关的话题标签
8. 整体风格要符合小红书平台的调性

原文标题：{title}

原文内容：
{content}

请按照小红书的风格重新编写这篇文章。"""

    def call_openai_api(self, prompt: str) -> Optional[str]:
        """调用OpenAI API"""
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'model': 'gpt-3.5-turbo',
                'messages': [
                    {'role': 'system', 'content': '你是一个专业的小红书内容创作者，擅长将普通文章改写成小红书风格。'},
                    {'role': 'user', 'content': prompt}
                ],
                'temperature': 0.7
            }
            
            response = requests.post(
                'https://api.openai.com/v1/chat/completions',
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            else:
                print(f"API调用失败: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"调用OpenAI API时出错: {str(e)}")
            return None
            
    def save_content(self, save_dir: str, content: str) -> str:
        """保存转换后的内容"""
        save_path = os.path.join(save_dir, 'xiaohongshu.txt')
        with open(save_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return save_path
        
    def convert(self, title: str, content: str, save_dir: str) -> Optional[XHSContent]:
        """转换内容为小红书风格"""
        try:
            print("正在生成小红书风格内容...")
            
            # 生成prompt
            prompt = self.get_prompt(title, content)
            
            # 调用API
            converted_content = self.call_openai_api(prompt)
            if not converted_content:
                return None
                
            # 保存内容
            save_path = self.save_content(save_dir, converted_content)
            
            return XHSContent(
                title=title,
                content=converted_content,
                save_path=save_path
            )
            
        except Exception as e:
            print(f"转换内容时出错: {str(e)}")
            return None

def main():
    # 测试代码
    from weixin_crawler import WeixinCrawler
    
    url = input("请输入微信公众号文章URL：")
    
    # 1. 获取文章内容
    crawler = WeixinCrawler()
    article = crawler.process_url(url)
    
    if not article:
        print("获取文章失败！")
        return
        
    # 2. 转换为小红书风格
    converter = XHSConverter()
    xhs_content = converter.convert(article.title, article.text, article.save_dir)
    
    if xhs_content:
        print("\n转换完成！")
        print(f"小红书风格内容已保存到：{xhs_content.save_path}")
    else:
        print("\n转换失败！")

if __name__ == "__main__":
    main() 