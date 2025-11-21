import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 1. Setup Driver
driver_path = os.path.join(os.getcwd(), 'driver', 'chromedriver.exe')
service = Service(driver_path)
options = webdriver.ChromeOptions()
options.add_experimental_option("detach", True)

driver = webdriver.Chrome(service=service, options=options)

try:
    # 2. Truy cập trang web
    url = "https://whippet-exotic-specially.ngrok-free.app/QlyShopTheThao/src/view/login.php"
    driver.get(url)
    print(f"Đang mở URL: {url}")

    # 3. Xử lý màn hình ngrok (Nếu có)
    try:
        # Tìm nút "Visit Site" và click
        visit_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Visit Site')]"))
        )
        visit_button.click()
        print("✅ Đã click bypass trang ngrok.")
        
        # Chờ một chút để trang chính load lại sau khi click
        time.sleep(2)
    except:
        print("ℹ️ Không thấy màn hình ngrok, vào thẳng trang web.")

    # 4. Code kiểm thử tiếp theo của bạn...
    print("Tiêu đề trang hiện tại:", driver.title)
    
    # Ví dụ login (nếu cần test luôn)
    # driver.find_element(By.NAME, "email").send_keys("user@example.com")

except Exception as e:
    print("❌ Có lỗi xảy ra:", e)

# finally:
#     driver.quit()