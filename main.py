import os
import time
import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

# 获取你在后台设置的账号密码
EMAIL = os.environ.get("DOG_EMAIL")
PASSWORD = os.environ.get("DOG_PASSWORD")

def run_task():
    # --- 浏览器配置 ---
    chrome_options = Options()
    chrome_options.add_argument("--headless") # 无头模式，不显示界面
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    # 模拟真实浏览器，防止被拦截
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36")
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.implicitly_wait(15) # 找不到元素时多等一会

    # 设置最长运行时间 (5小时50分钟，配合GitHub的6小时限制)
    start_time = time.time()
    max_duration = 21000 

    try:
        # === 1. 登录部分 ===
        print(">>> [1/3] 正在打开登录页...")
        driver.get("https://www.freedogdog.com/auth/login")
        time.sleep(5)

        print(">>> [2/3] 输入账号密码...")
        # 自动寻找邮箱和密码输入框
        driver.find_element(By.XPATH, "//input[@type='email']").send_keys(EMAIL)
        driver.find_element(By.XPATH, "//input[@type='password']").send_keys(PASSWORD)
        
        # 模拟按回车键登录
        driver.find_element(By.XPATH, "//input[@type='password']").send_keys(Keys.ENTER)
        
        print(">>> [3/3] 正在登录，等待跳转...")
        time.sleep(10) # 给足时间等待跳转到用户中心

        # === 2. 循环购买部分 ===
        buy_url = "https://www.freedogdog.com/user/plan2?id=1"
        
        print(">>> 登录成功，开始执行循环购买任务...")

        while True:
            # 检查是否超时
            if time.time() - start_time > max_duration:
                print(">>> 运行时间已到，准备重启...")
                break

            current_time = datetime.datetime.now().strftime("%H:%M:%S")
            try:
                # 访问购买链接
                driver.get(buy_url)
                
                # 【核心逻辑】尝试寻找确认按钮
                # 这种网站通常点进去后，下面会有一个“下单”、“结账”或者“Confirm”的按钮
                # 下面的 XPath 会寻找包含这些文字的按钮
                
                # 1. 尝试寻找主要的提交按钮
                buttons = driver.find_elements(By.XPATH, "//*[contains(text(),'下单') or contains(text(),'结账') or contains(text(),'下一步') or contains(text(),'Subscribe')]")
                
                if len(buttons) > 0:
                    # 如果找到了，点击第一个
                    buttons[0].click()
                    print(f"[{current_time}] ✅ 成功点击了下单按钮！")
                    
                    # (可选) 如果点击下单后还有弹窗确认，这里再点一次
                    time.sleep(2)
                    # driver.find_element(By.XPATH, "//*[text()='确定']").click()
                else:
                    # 有时候可能直接跳转了，或者按钮叫别的名字
                    print(f"[{current_time}] ⚠️ 页面打开了，但没找到明显的'下单'按钮，可能需要人工检查一下页面结构。")
                    # 打印一下标题看看对不对
                    print(f"当前页面标题: {driver.title}")

            except Exception as e:
                print(f"[{current_time}] ❌ 发生错误: {str(e)[:50]}")

            # 等待 60 秒再试
            time.sleep(60)

    except Exception as e:
        print(f"致命错误: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    run_task()
