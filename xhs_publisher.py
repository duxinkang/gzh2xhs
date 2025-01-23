import os
import json
import time
from typing import List, Optional, Dict
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from dataclasses import dataclass

@dataclass
class PublishResult:
    success: bool
    message: str
    post_url: Optional[str] = None

class XHSPublisher:
    def __init__(self, cookie_path: str = '.cookies.json'):
        """初始化发布器"""
        self.cookie_path = cookie_path
        
        # 配置Chrome选项
        options = Options()
        options.add_argument('--no-sandbox')
        options.add_argument('--start-maximized')
        options.add_experimental_option('detach', True)
        
        # 初始化浏览器
        self.driver = webdriver.Chrome(options=options)
        
    def login(self) -> bool:
        """登录小红书，如果有cookie则使用cookie登录"""
        try:
            print("正在访问小红书...")
            self.driver.get('https://www.xiaohongshu.com')
            time.sleep(2)
            
            if os.path.exists(self.cookie_path):
                print("正在使用已保存的Cookie登录...")
                with open(self.cookie_path, 'r') as f:
                    cookies = json.load(f)
                for cookie in cookies:
                    self.driver.add_cookie(cookie)
                
                # 刷新页面应用cookie
                self.driver.refresh()
                time.sleep(3)
                
                # 检查是否登录成功
                login_buttons = self.driver.find_elements(By.XPATH, "//div[contains(text(), '登录')]")
                if len(login_buttons) == 0:
                    print("自动登录成功！")
                    return True
                else:
                    print("Cookie已过期，需要重新登录")
            
            # 如果没有cookie或cookie失效，等待手动登录
            print("\n请在浏览器中手动登录小红书")
            print("登录成功后，按回车键继续...")
            input()
            
            # 保存新的cookie
            print("正在保存登录状态...")
            cookies = self.driver.get_cookies()
            with open(self.cookie_path, 'w') as f:
                json.dump(cookies, f)
            print("Cookie已保存")
            
            return True
            
        except Exception as e:
            print(f"登录过程中出现错误: {str(e)}")
            return False
            
    def publish_note(self, title: str, content: str, image_paths: List[str]) -> PublishResult:
        """发布笔记"""
        try:
            if not self.login():
                return PublishResult(success=False, message="登录失败")
            
            print("正在打开发布页面...")
            self.driver.get('https://www.xiaohongshu.com/publish')
            time.sleep(3)
            
            # 上传图片
            if image_paths:
                print("正在上传图片...")
                file_input = self.driver.find_element(By.CSS_SELECTOR, 'input[type="file"]')
                for image_path in image_paths:
                    file_input.send_keys(os.path.abspath(image_path))
                    time.sleep(1)
            
            # 输入标题
            print("正在输入标题...")
            title_input = self.driver.find_element(By.CSS_SELECTOR, '[placeholder="标题，添加标题会获得更多赞"]')
            title_input.send_keys(title)
            
            # 输入正文
            print("正在输入正文...")
            content_input = self.driver.find_element(By.CSS_SELECTOR, '[placeholder="请输入正文"]')
            content_input.send_keys(content)
            
            # 点击发布按钮
            print("正在发布...")
            publish_button = self.driver.find_element(By.XPATH, "//button[contains(text(), '发布')]")
            publish_button.click()
            
            # 等待发布成功
            time.sleep(5)
            
            # 获取发布后的笔记链接
            # TODO: 实现获取笔记链接的逻辑
            post_url = "发布成功，笔记链接待实现"
            
            return PublishResult(success=True, message="发布成功", post_url=post_url)
            
        except Exception as e:
            return PublishResult(success=False, message=f"发布失败: {str(e)}")
            
    def close(self):
        """关闭浏览器"""
        if self.driver:
            self.driver.quit()

def process_content(content: str) -> tuple[str, str]:
    """处理转换后的内容，提取标题和正文"""
    try:
        # 分割内容
        parts = content.split("二. 正文")
        if len(parts) != 2:
            raise ValueError("内容格式不正确")
            
        # 处理标题部分
        titles_part = parts[0].split("一. 标题")[1].strip()
        titles = [t.strip() for t in titles_part.split("\n") if t.strip()]
        
        # 选择第一个标题（通常是最好的）
        title = titles[0] if titles else "未找到标题"
        
        # 处理正文部分
        content = parts[1].strip()
        
        return title, content
    except Exception as e:
        print(f"处理内容时出错: {str(e)}")
        return "默认标题", content

def main():
    publisher = XHSPublisher()
    try:
        # 从文件读取内容
        content_dir = r"E:\fy\智企内推\data\CES 上最火的 AI 眼镜，竟然是中国美瞳一哥做的"
        
        # 读取转换后的内容
        with open(os.path.join(content_dir, "xiaohongshu.txt"), "r", encoding="utf-8") as f:
            raw_content = f.read()
        
        # 处理内容，提取标题和正文
        title, content = process_content(raw_content)
        print(f"使用标题: {title}")
        
        # 获取图片路径
        image_dir = os.path.join(content_dir, "images")
        image_paths = []
        if os.path.exists(image_dir):
            for file in os.listdir(image_dir):
                if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                    image_paths.append(os.path.join(image_dir, file))
            print(f"找到 {len(image_paths)} 张图片")
        
        # 发布笔记
        result = publisher.publish_note(
            title=title,
            content=content,
            image_paths=image_paths
        )
        print(f"发布结果: {result}")
    finally:
        publisher.close()

if __name__ == "__main__":
    main() 