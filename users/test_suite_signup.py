import unittest
import time
import os
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

URL_LOGIN = "https://whippet-exotic-specially.ngrok-free.app/QlyShopTheThao/src/view/login.php"

# Email này BẮT BUỘC phải đang tồn tại trong DB của bạn để test case trùng lặp chạy đúng
EXISTING_EMAIL = "wearingarmor12345@gmail.com" 

class SignUpComplexTest(unittest.TestCase):

    def setUp(self):
        """Setup: Mở Chrome, Bypass Ngrok"""
        driver_path = os.path.join(os.getcwd(), 'driver', 'chromedriver.exe')
        service = Service(driver_path)
        options = webdriver.ChromeOptions()
        # options.add_experimental_option("detach", True) # Bỏ comment nếu muốn giữ trình duyệt
        self.driver = webdriver.Chrome(service=service, options=options)
        self.driver.maximize_window()
        self.driver.get(URL_LOGIN)
        
        # Bypass Ngrok
        try:
            visit_btn = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Visit Site')]"))
            )
            visit_btn.click()
            time.sleep(2)
        except:
            pass

    def tearDown(self):
        self.driver.quit()

    # --- HÀM HỖ TRỢ ---
    def switch_to_signup_mode(self):
        """Chuyển sang tab Sign Up"""
        WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((By.ID, "signUp"))).click()
        WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.ID, "b1_signup")))
        time.sleep(1)

    def perform_signup_flow(self, email, password):
        """Điền form -> Click Sign Up -> Xử lý Captcha"""
        driver = self.driver
        
        # Điền thông tin
        WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.ID, "email"))).send_keys(email)
        driver.find_element(By.ID, "password").send_keys(password)
        driver.find_element(By.ID, "b1_signup").click()
        print(f"📝 Đã submit: {email}")

        # Xử lý Modal Captcha
        try:
            print("⏳ Đang check Captcha...")
            # Chờ modal to hiện
            WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.ID, "recaptchaSignUpModal")))
            
            # Switch vào iframe bên trong modal
            iframe_xpath = "//div[@id='recaptchaSignUpModal']//iframe[contains(@src, 'google.com/recaptcha')]"
            iframe = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, iframe_xpath)))
            
            driver.switch_to.frame(iframe)
            WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.ID, "recaptcha-anchor"))).click()
            driver.switch_to.default_content()
            
            print("✅ Đã tick Captcha.")
            time.sleep(3) # Chờ server xử lý redirect
            return True
        except Exception as e:
            print("ℹ️ Không thấy Captcha (hoặc lỗi validate).")
            try: driver.switch_to.default_content()
            except: pass
            return False

    # --- CÁC TEST CASE MỚI ---

    def test_01_duplicate_email(self):
        """TC: Đăng ký trùng Email -> Chuyển hướng trang lỗi SQL/Thông báo"""
        print("\n--- Running: Test Duplicate Email ---")
        self.switch_to_signup_mode()
        
        # Dùng email đã tồn tại
        self.perform_signup_flow(EXISTING_EMAIL, "123456")
        
        # Kiểm tra URL chuyển hướng sang controller xulyDangKi.php
        current_url = self.driver.current_url
        print(f"URL hiện tại: {current_url}")
        self.assertIn("xulyDangKi.php", current_url)
        
        # Kiểm tra nội dung text trên trang lỗi (Raw text)
        page_content = self.driver.find_element(By.TAG_NAME, "body").text
        print(f"Nội dung trang lỗi: {page_content[:100]}...") # In 100 ký tự đầu
        
        # Kiểm tra xem có chứa từ khóa lỗi không
        # Bạn cung cấp: "SQLSTATE[23000]... Email đã tồn tại"
        is_sql_error = "SQLSTATE[23000]" in page_content
        is_text_error = "Email đã tồn tại" in page_content
        
        self.assertTrue(is_sql_error or is_text_error, "Lỗi: Không thấy thông báo trùng email!")

    def test_02_signup_success_ui(self):
        """TC: Đăng ký mới -> Chuyển hướng trang success_reset_log.php"""
        print("\n--- Running: Test Signup Success UI ---")
        self.switch_to_signup_mode()
        
        # Tạo email mới
        rand = random.randint(10000, 99999)
        new_email = f"auto_tester_{rand}@gmail.com"
        
        self.perform_signup_flow(new_email, "123456")
        
        # Kiểm tra URL
        WebDriverWait(self.driver, 10).until(EC.url_contains("success_reset_log.php"))
        print(f"✅ Đã chuyển hướng đến: {self.driver.current_url}")
        
        # Kiểm tra nội dung trang Success
        # Tìm thẻ h1: "✅ Đăng ký đã được khởi tạo!"
        h1_text = self.driver.find_element(By.TAG_NAME, "h1").text
        self.assertIn("Đăng ký đã được khởi tạo", h1_text)
        
        # Kiểm tra xem email vừa đăng ký có hiện trong thẻ <strong> không
        body_text = self.driver.find_element(By.CLASS_NAME, "auth-message-container").text
        self.assertIn(new_email, body_text)

    def test_03_login_unverified_account(self):
        """TC: Đăng ký -> Không xác thực -> Đăng nhập -> Báo lỗi chưa xác thực"""
        print("\n--- Running: Test Unverified Login ---")
        self.switch_to_signup_mode()
        
        # 1. Đăng ký tài khoản mới
        rand = random.randint(10000, 99999)
        unverified_email = f"no_verify_{rand}@gmail.com"
        pass_test = "123456"
        
        print(f"📧 Đăng ký tài khoản (sẽ không xác thực): {unverified_email}")
        self.perform_signup_flow(unverified_email, pass_test)
        
        # Chờ chuyển hướng xong
        WebDriverWait(self.driver, 10).until(EC.url_contains("success_reset_log.php"))
        
        # 2. Quay lại trang Login (Click link "Quay lại trang đăng nhập" hoặc get URL lại)
        print("🔙 Quay lại trang Login...")
        self.driver.get(URL_LOGIN)
        
        # Bypass ngrok lại nếu cần (thường session còn lưu thì ko cần, nhưng cứ check cho chắc)
        try:
             WebDriverWait(self.driver, 2).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Visit Site')]"))).click()
        except: pass

        # 3. Thử Đăng nhập với tài khoản vừa tạo (nhưng chưa click mail)
        print("🔑 Đang thử đăng nhập...")
        WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.ID, "email_signin"))).send_keys(unverified_email)
        self.driver.find_element(By.ID, "password_signin").send_keys(pass_test)
        self.driver.find_element(By.ID, "b1").click()
        
        # Xử lý Captcha Đăng nhập
        try:
            iframe = WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, "iframe[src*='google.com/recaptcha']")))
            self.driver.switch_to.frame(iframe)
            WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((By.ID, "recaptcha-anchor"))).click()
            self.driver.switch_to.default_content()
            time.sleep(3)
        except:
            print("Không thấy captcha login")

        # 4. Kiểm tra lỗi "Tài khoản chưa xác thực"
        # Theo mô tả: Chuyển hướng sang xulyDangNhap.php và hiện text raw
        current_url = self.driver.current_url
        print(f"URL sau khi login: {current_url}")
        
        # Bạn nói là nó hiện raw text như ảnh chụp
        page_source = self.driver.find_element(By.TAG_NAME, "body").text
        print(f"Thông báo nhận được: {page_source}")
        
        target_msg = "Tài khoản chưa xác thực"
        self.assertIn(target_msg, page_source, "Lỗi: Không hiện thông báo tài khoản chưa xác thực!")

if __name__ == "__main__":
    unittest.main()