import os
import json
import time
from typing import List, Optional, Dict
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from dataclasses import dataclass

@dataclass
class PublishResult:
    success: bool
    message: str
    post_url: Optional[str] = None

class XHSPublisher:
    def __init__(self, cookie_path: str = '.cookies.json'):
        """初始化发布器
        cookie_path: 保存小红书登录cookie的文件路径
        """
        self.cookie_path = cookie_path
        self.driver = None
        
    def init_driver(self):
        """初始化浏览器"""
        options = webdriver.ChromeOptions()
        options.add_argument('--start-maximized')
        # options.add_argument('--headless')  # 无头模式，取消注释后将不显示浏览器窗口
        
        self.driver = webdriver.Chrome(options=options)
        
    def load_cookies(self) -> bool:
        """加载保存的cookie"""
        try:
            if not os.path.exists(self.cookie_path):
                return False
                
            with open(self.cookie_path, 'r') as f:
                cookies = json.load(f)
                
            # 访问小红书首页
            self.driver.get('https://www.xiaohongshu.com')
            
            # 添加cookie
            for cookie in cookies:
                self.driver.add_cookie(cookie)
                
            return True
            
        except Exception as e:
            print(f"加载cookie失败: {str(e)}")
            return False
            
    def save_cookies(self):
        """保存当前的cookie"""
        try:
            cookies = self.driver.get_cookies()
            with open(self.cookie_path, 'w') as f:
                json.dump(cookies, f)
        except Exception as e:
            print(f"保存cookie失败: {str(e)}")
            
    def check_login(self) -> bool:
        """检查是否已登录"""
        try:
            self.driver.get('https://www.xiaohongshu.com')
            time.sleep(3)  # 等待页面加载
            
            # 检查是否存在登录按钮
            login_buttons = self.driver.find_elements(By.XPATH, "//div[contains(text(), '登录')]")
            return len(login_buttons) == 0
            
        except Exception as e:
            print(f"检查登录状态失败: {str(e)}")
            return False
            
    def manual_login(self) -> bool:
        """等待用户手动登录"""
        print("请在打开的浏览器窗口中手动登录小红书...")
        print("登录成功后程序将自动继续")
        
        # 等待登录成功
        max_wait = 300  # 最多等待5分钟
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            if self.check_login():
                self.save_cookies()
                return True
            time.sleep(3)
            
        return False
        
    def publish_content(self, title: str, content: str, image_paths: List[str]) -> PublishResult:
        """发布内容到小红书"""
        try:
            if not self.driver:
                self.init_driver()
                
            # 尝试使用已保存的cookie登录
            if not self.load_cookies() or not self.check_login():
                # 需要手动登录
                if not self.manual_login():
                    return PublishResult(False, "登录失败")
                    
            # 打开发布页面
            self.driver.get('https://www.xiaohongshu.com/publish')
            time.sleep(3)
            
            # 上传图片
            file_input = self.driver.find_element(By.CSS_SELECTOR, 'input[type="file"]')
            for image_path in image_paths:
                file_input.send_keys(os.path.abspath(image_path))
                time.sleep(1)
                
            # 输入标题
            title_input = self.driver.find_element(By.CSS_SELECTOR, '[placeholder="标题，添加标题会获得更多赞"]')
            title_input.send_keys(title)
            
            # 输入正文
            content_input = self.driver.find_element(By.CSS_SELECTOR, '[placeholder="请输入正文"]')
            content_input.send_keys(content)
            
            # 点击发布按钮
            publish_button = self.driver.find_element(By.XPATH, "//button[contains(text(), '发布')]")
            publish_button.click()
            
            # 等待发布成功
            time.sleep(5)
            
            # TODO: 获取发布后的笔记链接
            post_url = None
            
            return PublishResult(True, "发布成功", post_url)
            
        except Exception as e:
            return PublishResult(False, f"发布失败: {str(e)}")
            
        finally:
            if self.driver:
                self.driver.quit()
                self.driver = None
                
    def publish_from_files(self, content_file: str, image_dir: str) -> PublishResult:
        """从文件发布内容"""
        try:
            # 读取内容
            with open(content_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # 获取标题（假设第一行是标题）
            title = content.split('\n')[0].strip()
            
            # 获取图片文件列表
            image_files = []
            for file in os.listdir(image_dir):
                if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                    image_files.append(os.path.join(image_dir, file))
                    
            # 发布内容
            return self.publish_content(title, content, image_files)
            
        except Exception as e:
            return PublishResult(False, f"发布失败: {str(e)}")

def main():
    # 测试代码
    from weixin_crawler import WeixinCrawler
    from xhs_converter import XHSConverter
    
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
    
    if not xhs_content:
        print("转换失败！")
        return
        
    # 3. 发布到小红书
    publisher = XHSPublisher()
    result = publisher.publish_from_files(
        xhs_content.save_path,
        os.path.join(article.save_dir, 'images')
    )
    
    if result.success:
        print("\n发布成功！")
        if result.post_url:
            print(f"笔记链接：{result.post_url}")
    else:
        print(f"\n发布失败：{result.message}")

if __name__ == "__main__":
    main() 