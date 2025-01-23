import os
import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

def test_login():
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
        
        print("正在访问小红书...")
        driver.get('https://www.xiaohongshu.com')
        
        # 等待用户手动登录
        print("\n请在打开的浏览器窗口中手动登录小红书")
        print("登录成功后，按回车键继续...")
        input()
        
        # 保存cookie
        print("正在保存登录状态...")
        cookies = driver.get_cookies()
        with open('.cookies.json', 'w') as f:
            json.dump(cookies, f)
        print("Cookie已保存到.cookies.json")
        
        # 让用户选择是否关闭浏览器
        print("\n是否关闭浏览器？(y/n)")
        choice = input().lower()
        if choice == 'y':
            print("正在关闭浏览器...")
            driver.quit()
        else:
            print("浏览器将保持打开状态，请手动关闭。")
            # 分离driver，让浏览器保持打开
            driver.service.process = None
            driver.quit()
        
    except Exception as e:
        print(f"测试过程中出现错误: {str(e)}")
        if 'driver' in locals():
            driver.quit()
        
if __name__ == "__main__":
    test_login() 