import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 1. SETUP DRIVER
driver_path = os.path.join(os.getcwd(), 'driver', 'chromedriver.exe')
service = Service(driver_path)
options = webdriver.ChromeOptions()
options.add_experimental_option("detach", True)
driver = webdriver.Chrome(service=service, options=options)

try:
    # ==========================================
    # BƯỚC 1: MỞ WEB & BYPASS NGROK
    # ==========================================
    url = "https://whippet-exotic-specially.ngrok-free.app/QlyShopTheThao/src/view/login.php"
    driver.get(url)
    print(f"🌐 Đang mở URL: {url}")

    try:
        visit_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Visit Site')]"))
        )
        visit_button.click()
        print("✅ Đã bypass trang ngrok.")
        time.sleep(2)
    except:
        print("ℹ️ Vào thẳng trang web (không thấy ngrok warning).")

    # ==========================================
    # BƯỚC 2: ĐIỀN FORM ĐĂNG NHẬP
    # ==========================================
    print("📝 Đang điền thông tin đăng nhập...")
    
    # --- CẤU HÌNH TÀI KHOẢN TEST Ở ĐÂY ---
    my_email = "admin@gmail.com"  # Thay email thật của bạn
    my_pass = "123456"            # Thay pass thật của bạn
    # -------------------------------------

    email_input = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, "email_signin"))
    )
    email_input.clear()
    email_input.send_keys(my_email)

    pass_input = driver.find_element(By.ID, "password_signin")
    pass_input.clear()
    pass_input.send_keys(my_pass)

    # --- CẬP NHẬT PHẦN CLICK NÚT SIGN IN ---
    # Dùng ID="b1" như bạn cung cấp
    signin_btn = driver.find_element(By.ID, "b1")
    signin_btn.click()
    print("🖱️ Đã click nút Sign in (ID: b1).")

    # ==========================================
    # BƯỚC 3: XỬ LÝ RECAPTCHA MODAL
    # ==========================================
    print("🤖 Đang đợi Modal Captcha...")

    # 1. Tìm iframe reCAPTCHA
    # (Chờ tối đa 10s để modal hiện lên sau khi click Sign In)
    captcha_iframe = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "iframe[src*='google.com/recaptcha']"))
    )

    # 2. Switch vào iframe
    driver.switch_to.frame(captcha_iframe)

    # 3. Click checkbox
    checkbox = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "recaptcha-anchor"))
    )
    checkbox.click()
    print("✅ Đã tick vào checkbox Captcha.")

    # 4. Switch ra ngoài
    driver.switch_to.default_content()

    # ==========================================
    # BƯỚC 4: KẾT THÚC
    # ==========================================
    time.sleep(5) # Chờ login xử lý xong
    print("🎉 Script chạy xong. Kiểm tra xem đã login chưa.")

except Exception as e:
    print("❌ Lỗi:", e)