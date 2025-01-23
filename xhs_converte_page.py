import os
import json
import requests
import time
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass
from dotenv import load_dotenv
import sys

# 加载环境变量
load_dotenv()

# 设置基础保存路径
BASE_SAVE_PATH = r"E:\fy\智企内推\data"

@dataclass
class PageContent:
    title: str
    text: str
    images: List[str]
    save_dir: str

@dataclass
class XHSContent:
    title: str
    content: str
    save_path: str

class PageCrawler:
    def __init__(self):
        """初始化爬虫"""
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
    def download_image(self, url: str, save_path: str) -> bool:
        """下载图片"""
        try:
            response = requests.get(url, headers=self.headers, verify=False)
            if response.status_code == 200:
                with open(save_path, 'wb') as f:
                    f.write(response.content)
                return True
        except Exception as e:
            print(f"下载图片失败: {str(e)}")
        return False
        
    def process_url(self, url: str) -> Optional[PageContent]:
        """处理URL，获取页面内容"""
        try:
            print(f"\n开始处理URL: {url}")
            
            # 发送请求
            print("正在访问页面...")
            response = requests.get(url, headers=self.headers, verify=False)
            response.encoding = 'utf-8'
            
            if response.status_code != 200:
                print(f"访问页面失败: {response.status_code}")
                return None
                
            # 解析页面
            print("解析页面内容...")
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 获取标题
            title = soup.find('h1').get_text().strip()
            
            # 获取正文内容
            content_elements = soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
            text_content = []
            
            for element in content_elements:
                text = element.get_text().strip()
                if text and not text.startswith(('Copyright', '联系方式')):
                    text_content.append(text)
            
            text = '\n\n'.join(text_content)
            
            # 创建保存目录
            save_dir = os.path.join(BASE_SAVE_PATH, title)
            os.makedirs(save_dir, exist_ok=True)
            
            # 下载图片
            images_dir = os.path.join(save_dir, "images")
            os.makedirs(images_dir, exist_ok=True)
            
            image_urls = []
            for img in soup.find_all('img'):
                src = img.get('src')
                if src and not src.startswith('data:'):
                    image_urls.append(urljoin(url, src))
            
            saved_images = []
            for i, image_url in enumerate(image_urls, 1):
                print(f"正在下载第 {i}/{len(image_urls)} 张图片...")
                image_path = os.path.join(images_dir, f"image_{i}.jpg")
                if self.download_image(image_url, image_path):
                    saved_images.append(image_path)
                    print(f"图片已保存: {image_path}")
            
            print(f"共保存 {len(saved_images)} 张图片")
            
            return PageContent(
                title=title,
                text=text,
                images=saved_images,
                save_dir=save_dir
            )
            
        except Exception as e:
            print(f"处理页面时出错: {str(e)}")
            return None

class XHSConverter:
    def __init__(self, api_key: Optional[str] = None):
        """初始化转换器"""
        self.api_key = api_key or os.getenv('ZHI_API_KEY')
        self.base_url = os.getenv('BASE_URL')
        
        if not self.api_key:
            raise ValueError("需要设置ZHI_API_KEY环境变量或在初始化时提供api_key")
        if not self.base_url:
            raise ValueError("需要在环境变量中设置 BASE_URL")
            
    def get_prompt(self, title: str, content: str) -> str:
        """生成Prompt模板"""
        return f"""你是一位小红书爆款写作专家，请将以下产品介绍页面转换成小红书风格的内容。

一、首先，请基于原文生成5个小红书风格的标题（含emoji表情），要求：
1. 采用二极管标题法
2. 使用吸引人的特点和爆款关键词
3. 符合小红书平台特性
4. 标题要简短有力，突出重点

二、然后，请基于原文生成小红书风格的正文，要求：
1. 采用轻松活泼的写作风格，介绍产品的特点和优势
2. 开篇要抓人眼球，引发读者兴趣
3. 文本结构清晰，分段要合理
4. 加入互动引导，增加用户参与感
5. 每段话都要口语化、简短
6. 在每段话的开头、中间和结尾使用合适的emoji表情
7. 最后加入3-6个相关的话题标签
8. 正文最后显示"了解更多详情，请访问网易数智官网"

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
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'messages': [
                    {'role': 'system', 'content': '你是一个专业的小红书内容创作者，擅长将产品介绍转换成吸引人的小红书风格。'},
                    {'role': 'user', 'content': prompt}
                ],
                'model': 'qwen-max',
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
                print(f"API响应内容: {result}")
                
                if 'choices' not in result:
                    print("API响应格式错误")
                    return None
                    
                return result['choices'][0]['message']['content']
            else:
                print(f"API调用失败: {response.status_code}")
                print(f"错误信息: {response.text}")
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
            
            prompt = self.get_prompt(title, content)
            converted_content = self.call_openai_api(prompt)
            
            if not converted_content:
                return None
                
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
    if len(sys.argv) < 2:
        print("请提供要转换的URL")
        print("使用方法: python xhs_converte_page.py <url>")
        return
        
    url = sys.argv[1]
    print(f"开始处理URL: {url}")
    
    # 1. 获取页面内容
    crawler = PageCrawler()
    page = crawler.process_url(url)
    
    if not page:
        print("获取页面内容失败！")
        return
        
    # 2. 转换为小红书风格
    converter = XHSConverter()
    xhs_content = converter.convert(page.title, page.text, page.save_dir)
    
    if xhs_content:
        print("\n转换完成！")
        print(f"小红书风格内容已保存到：{xhs_content.save_path}")
    else:
        print("\n转换失败！")

if __name__ == "__main__":
    main() 