import os
import time
import requests
import re
from io import BytesIO
from bs4 import BeautifulSoup
from PIL import Image, ImageEnhance
from fake_useragent import UserAgent
from dotenv import load_dotenv

class WeixinToXiaohongshu:
    def __init__(self):
        self.headers = {
            'User-Agent': UserAgent().random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        load_dotenv()
        self.xhs_cookie = os.getenv('XHS_COOKIE')
        self.base_save_path = r"E:\fy\智企内推\data"
        
    def create_save_directory(self, title):
        """创建保存目录"""
        # 清理标题中的非法字符
        safe_title = re.sub(r'[\\/:*?"<>|]', '_', title)
        save_dir = os.path.join(self.base_save_path, safe_title)
        
        # 创建目录
        os.makedirs(save_dir, exist_ok=True)
        os.makedirs(os.path.join(save_dir, 'images'), exist_ok=True)
        
        return save_dir
        
    def save_content(self, save_dir, content, styled_content):
        """保存文本内容"""
        # 保存原始内容
        with open(os.path.join(save_dir, 'original.txt'), 'w', encoding='utf-8') as f:
            f.write(content)
            
        # 保存小红书风格内容
        with open(os.path.join(save_dir, 'xiaohongshu.txt'), 'w', encoding='utf-8') as f:
            f.write(styled_content)
            
    def save_images(self, save_dir, images):
        """下载并保存图片"""
        saved_images = []
        for i, img_url in enumerate(images):
            try:
                print(f"正在下载第 {i+1}/{len(images)} 张图片...")
                response = requests.get(img_url, headers=self.headers)
                img = Image.open(BytesIO(response.content))
                
                # 如果图片是RGBA模式，转换为RGB
                if img.mode == 'RGBA':
                    # 创建白色背景
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    # 将原图复制到白色背景上
                    background.paste(img, mask=img.split()[3])  # 使用alpha通道作为mask
                    img = background
                elif img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # 处理图片
                processed_img = self.process_image(img)
                if processed_img:
                    # 保存处理后的图片
                    save_path = os.path.join(save_dir, 'images', f'image_{i+1}.jpg')
                    processed_img.save(save_path, 'JPEG', quality=95)
                    saved_images.append(save_path)
                    print(f"图片已保存: {save_path}")
                    
            except Exception as e:
                print(f"处理第 {i+1} 张图片时出错: {str(e)}")
                continue
                
        return saved_images
        
    def process_image(self, img):
        """处理图片，添加小红书风格滤镜"""
        try:
            # 增加饱和度
            enhancer = ImageEnhance.Color(img)
            img = enhancer.enhance(1.2)
            
            # 增加对比度
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(1.1)
            
            # 增加亮度
            enhancer = ImageEnhance.Brightness(img)
            img = enhancer.enhance(1.1)
            
            return img
            
        except Exception as e:
            print(f"处理图片失败: {str(e)}")
            return None
            
    def get_weixin_content(self, url):
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
                    
            return {
                'title': title,
                'text': '\n'.join(text_content),
                'images': images
            }
            
        except Exception as e:
            print(f"获取微信文章失败: {str(e)}")
            return None
            
    def convert_to_xhs_style(self, title, content):
        """将文本转换为小红书风格"""
        # 分段处理
        paragraphs = content.split('\n')
        filtered_paragraphs = []
        seen_paragraphs = set()
        
        for p in paragraphs:
            p = p.strip()
            if p and p not in seen_paragraphs:
                filtered_paragraphs.append(p)
                seen_paragraphs.add(p)
                
        # 构建小红书风格的内容
        styled_content = []
        
        # 添加标题（使用emoji装饰）
        styled_content.append(f"✨ {title} ✨")
        styled_content.append("")  # 空行
        
        # 添加开场白
        styled_content.append("大家好呀~ 今天给大家分享一篇超棒的文章 🌟")
        styled_content.append("")  # 空行
        
        # 添加正文
        for i, p in enumerate(filtered_paragraphs):
            if i < 3:  # 只保留前三段主要内容
                styled_content.append(p)
                
        # 添加总结
        styled_content.append("")
        styled_content.append("💡 重点总结：")
        styled_content.append("1️⃣ " + filtered_paragraphs[0][:100] + "...")
        if len(filtered_paragraphs) > 1:
            styled_content.append("2️⃣ " + filtered_paragraphs[1][:100] + "...")
            
        # 添加emoji
        emoji_dict = {
            "推荐": "👍",
            "分享": "🎉",
            "喜欢": "❤️",
            "建议": "💡",
            "提醒": "⚠️",
            "注意": "❗",
            "重要": "‼️",
            "游戏": "🎮",
            "直播": "📱",
            "玩家": "👥",
            "成本": "💰",
            "营销": "📢"
        }
        
        # 添加标签
        tags = [
            "#经验分享",
            "#干货分享",
            "#每日一读",
            "#文章推荐",
            "#干货必看"
        ]
        
        # 合并内容
        final_content = "\n".join(styled_content)
        
        # 添加emoji
        for key, emoji in emoji_dict.items():
            final_content = final_content.replace(key, f"{key}{emoji}")
            
        # 添加标签
        final_content += "\n\n" + " ".join(tags)
        
        return final_content
        
    def process_url(self, url):
        """处理单个URL"""
        print(f"\n开始处理URL: {url}")
        
        # 1. 获取文章内容
        content = self.get_weixin_content(url)
        if not content:
            print("获取文章失败！")
            return False
            
        print(f"\n成功获取文章：{content['title']}")
        
        # 2. 创建保存目录
        save_dir = self.create_save_directory(content['title'])
        print(f"创建保存目录：{save_dir}")
        
        # 3. 转换为小红书风格
        styled_content = self.convert_to_xhs_style(content['title'], content['text'])
        
        # 4. 保存文本内容
        self.save_content(save_dir, content['text'], styled_content)
        print("文本内容已保存")
        
        # 5. 下载并保存图片
        saved_images = self.save_images(save_dir, content['images'])
        print(f"共保存 {len(saved_images)} 张图片")
        
        return True

def main():
    url = input("请输入微信公众号文章URL：")
    converter = WeixinToXiaohongshu()
    
    if converter.process_url(url):
        print("\n处理完成！")
    else:
        print("\n处理失败！")

if __name__ == "__main__":
    main() 