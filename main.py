import os
import time
import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 获取账号密码
EMAIL = os.environ.get("DOG_EMAIL")
PASSWORD = os.environ.get("DOG_PASSWORD")

def run_task():
    # --- 1. 升级版浏览器伪装配置 ---
    chrome_options = Options()
    chrome_options.add_argument("--headless") 
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    # 关键：禁用自动化控制特征，防止被检测为机器人
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # 模拟最新的 Windows Chrome
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
    chrome_options.add_argument("--window-size=1920,1080")
    
    driver = webdriver.Chrome(options=chrome_options)
    # 修改 WebDriver 属性，防止被 JS 检测
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    start_time = time.time()
    max_duration = 21000 

    try:
        print(">>> [1/4] 正在打开登录页 (https://www.freedogdog.com/auth/login)...")
        driver.get("https://www.freedogdog.com/auth/login")
        
        # --- 2. 智能等待与诊断 ---
        print(">>> 等待页面加载...")
        try:
            # 最多等 20 秒，直到邮箱输入框出现
            # 我们尝试用 name="email" 来找，这比 type="email" 更通用
            email_input = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.NAME, "email"))
            )
            print("✅ 成功找到邮箱输入框！")
            
        except Exception as e:
            # 如果等了20秒还没找到，说明出大事了
            print("\n❌ 严重错误：找不到登录框！")
            print(f"当前页面标题是: 【{driver.title}】")
            print("可能原因：")
            print("1. 遇到了 Cloudflare 五秒盾 (Just a moment...)")
            print("2. 网站改版了")
            
            # 打印网页源码的前500个字，看看是啥
            print(f"网页源码片段: {driver.page_source[:500]}")
            
            # 直接结束程序
            driver.quit()
            return

        # --- 3. 执行登录 ---
        print(">>> [2/4] 输入账号密码...")
        email_input.clear()
        email_input.send_keys(EMAIL)
        
        # 找密码框
        pass_input = driver.find_element(By.CSS_SELECTOR, "input[type='password']")
        pass_input.clear()
        pass_input.send_keys(PASSWORD)
        
        # 登录
        print(">>> 提交登录...")
        pass_input.send_keys(Keys.ENTER)
        
        time.sleep(10) # 等待跳转
        print(f"登录后标题: {driver.title}")

        # --- 4. 循环购买 ---
        buy_url = "https://www.freedogdog.com/user/plan2?id=1"
        print(">>> [3/4] 开始循环任务...")
        
        while True:
            if time.time() - start_time > max_duration:
                break

            current_time = datetime.datetime.now().strftime("%H:%M:%S")
            try:
                driver.get(buy_url)
                # 等待 5 秒让 JS 加载
                time.sleep(5)
                
                # 尝试点击任何看起来像下单的按钮
                # 这里使用了 CSS 选择器，查找包含 specific class 的按钮
                # 同时也保留 XPath 文本查找
                
                found = False
                
                # 策略 A: 找文字
                try:
                    targets = driver.find_elements(By.XPATH, "//*[contains(text(),'下单') or contains(text(),'结账') or contains(text(),'¥') or contains(text(),'Submit')]")
                    for t in targets:
                        # 排除掉不可见的元素
                        if t.is_displayed():
                            print(f"[{current_time}] 尝试点击文本按钮: {t.text}")
                            driver.execute_script("arguments[0].click();", t)
                            found = True
                            break
                except:
                    pass
                
                # 策略 B: 找 V2Board 常见的 Checkout 按钮 class
                if not found:
                    try:
                        btn = driver.find_element(By.CSS_SELECTOR, ".btn-primary")
                        print(f"[{current_time}] 尝试点击主按钮 (.btn-primary)")
                        driver.execute_script("arguments[0].click();", btn)
                        found = True
                    except:
                        pass

                if found:
                    print(f"[{current_time}] ✅ 点击动作已发送")
                else:
                    print(f"[{current_time}] ⚠️ 未找到按钮。当前标题: {driver.title}")

            except Exception as e:
                print(f"[{current_time}] 出错: {e}")

            time.sleep(60)

    except Exception as e:
        print(f"致命错误: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    run_task()
