import os
import time
import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

EMAIL = os.environ.get("DOG_EMAIL")
PASSWORD = os.environ.get("DOG_PASSWORD")

def run_task():
    print(">>> 初始化浏览器 (配合 WARP 网络)...")
    
    chrome_options = Options()
    # 必须的无头配置
    chrome_options.add_argument("--headless=new") # 使用新版无头模式，特征更少
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    # 伪装配置
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    # 忽略证书错误（代理模式下常见）
    chrome_options.add_argument("--ignore-certificate-errors")

    driver = webdriver.Chrome(options=chrome_options)
    
    # 移除 webdriver 特征
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    try:
        # === 1. 验证网络 ===
        print(">>> [0/4] 检查当前网络连通性...")
        try:
            driver.get("https://www.google.com")
            print(f"Google 访问标题: {driver.title}")
        except:
            print("无法访问 Google，WARP 可能连接不稳定，但继续尝试目标网站...")

        # === 2. 打开登录页 ===
        target_login = "https://www.freedogdog.com/auth/login"
        print(f">>> [1/4] 正在打开: {target_login}")
        
        driver.get(target_login)
        time.sleep(5)
        
        # 截图页面源码的一小部分，确认是否还是 Not Found
        print(f"当前页面标题: 【{driver.title}】")
        if "Not Found" in driver.page_source or driver.title == "":
            print("❌ 依然被拦截！WARP IP 也被墙了，或者网站有极高级别的风控。")
            print(driver.page_source[:200])
            return

        # === 3. 输入账号密码 ===
        print(">>> [2/4] 输入账号密码...")
        # 显式等待输入框
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='email']"))
        ).send_keys(EMAIL)
        
        driver.find_element(By.CSS_SELECTOR, "input[type='password']").send_keys(PASSWORD)
        time.sleep(1)
        
        # 提交
        print(">>> 提交登录...")
        driver.find_element(By.CSS_SELECTOR, "input[type='password']").send_keys(Keys.ENTER)
        
        # 等待跳转
        time.sleep(10)
        print(f"登录后标题: {driver.title}")

        # === 4. 循环购买 ===
        buy_url = "https://www.freedogdog.com/user/plan2?id=1"
        start_time = time.time()
        
        print(">>> [3/4] 进入抢购循环...")
        while True:
            if time.time() - start_time > 21000: # 接近6小时
                break
                
            try:
                driver.get(buy_url)
                time.sleep(5)
                
                # 暴力查找所有可能的按钮
                # 针对 V2Board 的结构，寻找 checkout / order 类的按钮
                print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] 扫描按钮...")
                
                # 方案A: 文本匹配
                xpath = "//*[contains(text(),'下单') or contains(text(),'结账') or contains(text(),'Submit') or contains(text(),'Checkout')]"
                btns = driver.find_elements(By.XPATH, xpath)
                
                if btns:
                    for btn in btns:
                        if btn.is_displayed():
                            print(f"👉 点击文本按钮: {btn.text}")
                            driver.execute_script("arguments[0].click();", btn)
                            print("✅ 点击指令已发送")
                            break
                else:
                    # 方案B: CSS 类匹配 (常见于 V2Board)
                    try:
                        btn = driver.find_element(By.CSS_SELECTOR, ".btn-primary")
                        print("👉 点击 .btn-primary 按钮")
                        driver.execute_script("arguments[0].click();", btn)
                        print("✅ 点击指令已发送")
                    except:
                        print(f"⚠️ 没找到按钮。当前标题: {driver.title}")

            except Exception as e:
                print(f"出错: {str(e)[:100]}")
                
            time.sleep(60)

    except Exception as e:
        print(f"致命错误: {e}")
        # 打印源码方便排查
        try:
            print("最后的页面源码片段:")
            print(driver.page_source[:500])
        except:
            pass
    finally:
        driver.quit()

if __name__ == "__main__":
    run_task()
