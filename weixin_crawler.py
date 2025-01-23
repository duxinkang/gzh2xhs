import os
import re
import requests
from io import BytesIO
from bs4 import BeautifulSoup
from PIL import Image
from fake_useragent import UserAgent
from dataclasses import dataclass
from typing import List, Dict, Optional

@dataclass
class ArticleContent:
    title: str
    text: str
    images: List[str]
    save_dir: str

class WeixinCrawler:
    def __init__(self, base_save_path: str = r"E:\fy\智企内推\data"):
        self.headers = {
            'User-Agent': UserAgent().random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        self.base_save_path = base_save_path
        
    def create_save_directory(self, title: str) -> str:
        """创建保存目录"""
        safe_title = re.sub(r'[\\/:*?"<>|]', '_', title)
        save_dir = os.path.join(self.base_save_path, safe_title)
        
        # 创建目录
        os.makedirs(save_dir, exist_ok=True)
        os.makedirs(os.path.join(save_dir, 'images'), exist_ok=True)
        
        return save_dir
        
    def save_content(self, save_dir: str, content: str) -> None:
        """保存原始文本内容"""
        with open(os.path.join(save_dir, 'original.txt'), 'w', encoding='utf-8') as f:
            f.write(content)
            
    def save_images(self, save_dir: str, images: List[str]) -> List[str]:
        """下载并保存图片"""
        saved_images = []
        for i, img_url in enumerate(images):
            try:
                print(f"正在下载第 {i+1}/{len(images)} 张图片...")
                response = requests.get(img_url, headers=self.headers)
                img = Image.open(BytesIO(response.content))
                
                # 如果图片是RGBA模式，转换为RGB
                if img.mode == 'RGBA':
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    background.paste(img, mask=img.split()[3])
                    img = background
                elif img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # 保存图片
                save_path = os.path.join(save_dir, 'images', f'image_{i+1}.jpg')
                img.save(save_path, 'JPEG', quality=95)
                saved_images.append(save_path)
                print(f"图片已保存: {save_path}")
                
            except Exception as e:
                print(f"处理第 {i+1} 张图片时出错: {str(e)}")
                continue
                
        return saved_images
        
    def get_article_content(self, url: str) -> Optional[ArticleContent]:
        """获取微信公众号文章内容"""
        try:
            print("正在访问文章链接...")
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            print("解析文章内容...")
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 获取文章内容
            content_div = soup.find(id="js_content")
            if not content_div:
                raise Exception("未找到文章内容")
                
            # 获取文章标题
            title = soup.find(class_="rich_media_title").get_text().strip() if soup.find(class_="rich_media_title") else ""
                
            # 提取文本和图片
            text_content = []
            images = []
            seen_texts = set()  # 用于去重
            
            # 提取文本
            for p in content_div.find_all(['p', 'span']):
                text = p.get_text().strip()
                if text and text not in seen_texts:
                    text_content.append(text)
                    seen_texts.add(text)
                    
            # 提取图片
            for img in content_div.find_all('img'):
                img_url = img.get('data-src')
                if img_url and img_url not in images:  # 去重
                    images.append(img_url)
                    
            # 创建保存目录
            save_dir = self.create_save_directory(title)
            
            # 构建返回对象
            article = ArticleContent(
                title=title,
                text='\n'.join(text_content),
                images=images,
                save_dir=save_dir
            )
            
            return article
            
        except Exception as e:
            print(f"获取微信文章失败: {str(e)}")
            return None
            
    def process_url(self, url: str) -> Optional[ArticleContent]:
        """处理单个URL"""
        print(f"\n开始处理URL: {url}")
        
        # 1. 获取文章内容
        article = self.get_article_content(url)
        if not article:
            print("获取文章失败！")
            return None
            
        print(f"\n成功获取文章：{article.title}")
        print(f"创建保存目录：{article.save_dir}")
        
        # 2. 保存文本内容
        self.save_content(article.save_dir, article.text)
        print("文本内容已保存")
        
        # 3. 下载并保存图片
        saved_images = self.save_images(article.save_dir, article.images)
        print(f"共保存 {len(saved_images)} 张图片")
        
        return article

def main():
    url = input("请输入微信公众号文章URL：")
    crawler = WeixinCrawler()
    article = crawler.process_url(url)
    
    if article:
        print("\n处理完成！")
        print(f"文章已保存到：{article.save_dir}")
    else:
        print("\n处理失败！")

if __name__ == "__main__":
    main() 