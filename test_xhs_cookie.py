import os
import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def test_cookie():
    try:
        print("正在初始化Chrome浏览器...")
        
        # 配置Chrome选项
        chrome_options = Options()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--ignore-certificate-errors')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-software-rasterizer')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--start-maximized')
        
        # 使用本地Chrome浏览器
        chrome_options.add_experimental_option('detach', True)
        
        print("正在创建WebDriver...")
        driver = webdriver.Chrome(options=chrome_options)
        
        # 首先访问小红书主页
        print("正在访问小红书...")
        driver.get('https://www.xiaohongshu.com')
        time.sleep(2)  # 等待页面加载
        
        # 加载保存的cookie
        if os.path.exists('.cookies.json'):
            print("正在加载已保存的Cookie...")
            with open('.cookies.json', 'r') as f:
                cookies = json.load(f)
            for cookie in cookies:
                driver.add_cookie(cookie)
            
            # 刷新页面以应用cookie
            print("正在刷新页面...")
            driver.refresh()
            time.sleep(3)  # 等待页面加载
            
            # 检查是否已登录（可以通过检查页面上的某些元素来判断）
            print("正在检查登录状态...")
            try:
                # 等待页面加载完成，检查是否存在登录按钮
                login_buttons = driver.find_elements(By.XPATH, "//div[contains(text(), '登录')]")
                if len(login_buttons) == 0:
                    print("Cookie验证成功！已成功登录小红书")
                else:
                    print("Cookie可能已过期，需要重新登录")
            except Exception as e:
                print(f"检查登录状态时出错: {str(e)}")
        else:
            print("未找到保存的Cookie文件")
        
        # 让用户选择是否关闭浏览器
        print("\n是否关闭浏览器？(y/n)")
        choice = input().lower()
        if choice == 'y':
            print("正在关闭浏览器...")
            driver.quit()
        else:
            print("浏览器将保持打开状态，请手动关闭。")
            driver.service.process = None
            driver.quit()
            
    except Exception as e:
        print(f"测试过程中出现错误: {str(e)}")
        if 'driver' in locals():
            driver.quit()

if __name__ == "__main__":
    test_cookie() 