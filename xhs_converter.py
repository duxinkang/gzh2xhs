import os
import json
import requests
from typing import Optional, Dict, Any
from dataclasses import dataclass
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

@dataclass
class XHSContent:
    title: str
    content: str
    save_path: str

class XHSConverter:
    def __init__(self, api_key: Optional[str] = None):
        """初始化转换器
        api_key: API密钥
        """
        self.api_key = api_key or os.getenv('ZHI_API_KEY')
        self.base_url = os.getenv('BASE_URL')
        
        if not self.api_key:
            raise ValueError("需要设置ZHI_API_KEY环境变量或在初始化时提供api_key")
        if not self.base_url:
            raise ValueError("需要在环境变量中设置 BASE_URL")
            
    def get_prompt(self, title: str, content: str) -> str:
        """生成Prompt模板"""
        return f"""你是一位小红书爆款写作专家，请将以下文章改写成小红书风格的内容。

一、首先，请基于原文生成5个小红书风格的标题（含emoji表情），要求：
1. 采用二极管标题法
2. 使用吸引人的特点和爆款关键词
3. 符合小红书平台特性
4. 标题要简短有力，突出重点

二、然后，请基于原文生成小红书风格的正文，要求：
1. 采用轻松活泼的写作风格
2. 开篇要抓人眼球
3. 文本结构清晰，分段要合理
4. 加入互动引导
5. 每段话都要口语化、简短
6. 在每段话的开头、中间和结尾使用合适的emoji表情
7. 最后加入3-6个相关的话题标签
8. 正文最后显示转载自微信公众号：网易智企

原文标题：{title}

原文内容：
{content}

请按照如下格式输出：
一. 标题
[5个标题，每行一个]

二. 正文
[正文内容]
标签：[标签列表]"""

    def call_openai_api(self, prompt: str) -> Optional[str]:
        """调用API"""
        try:
            headers = {
                'Authorization': self.api_key,
                'Content-Type': 'application/json'
            }
            
            data = {
                'model': 'gpt-4',
                'messages': [
                    {'role': 'system', 'content': '你是一个专业的小红书内容创作者，擅长将普通文章改写成小红书风格。'},
                    {'role': 'user', 'content': prompt}
                ],
                'temperature': 0.7
            }
            
            response = requests.post(
                f'{self.base_url}/chat/completions',
                headers=headers,
                json=data,
                timeout=60,
                verify=False
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"API响应内容: {result}")  # 添加调试信息
                
                # 检查响应格式
                if 'choices' not in result:
                    print(f"API响应格式错误，缺少 'choices' 字段")
                    return None
                    
                if not result['choices'] or 'message' not in result['choices'][0]:
                    print(f"API响应格式错误，无法获取生成的内容")
                    return None
                    
                return result['choices'][0]['message']['content']
            else:
                print(f"API调用失败: {response.status_code}")
                print(f"错误信息: {response.text}")
                return None
                
        except requests.exceptions.Timeout:
            print("API请求超时，请检查网络连接或稍后重试")
            return None
        except requests.exceptions.ConnectionError:
            print("连接错误，请检查API地址是否正确")
            return None
        except json.JSONDecodeError as e:
            print(f"API响应解析失败: {str(e)}")
            print(f"原始响应: {response.text}")
            return None
        except Exception as e:
            print(f"调用API时出错: {str(e)}")
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