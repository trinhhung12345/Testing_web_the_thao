import unittest
import time
import os
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

URL_MAIN = "https://whippet-exotic-specially.ngrok-free.app/QlyShopTheThao/src/view/login.php"

class SignUpTest(unittest.TestCase):

    def setUp(self):
        """Setup: Mở Chrome, Bypass Ngrok"""
        driver_path = os.path.join(os.getcwd(), 'driver', 'chromedriver.exe')
        service = Service(driver_path)
        options = webdriver.ChromeOptions()
        options.add_experimental_option("detach", True)
        self.driver = webdriver.Chrome(service=service, options=options)
        self.driver.maximize_window()
        
        self.driver.get(URL_MAIN)
        
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
        driver = self.driver
        # Click nút Ghost "Sign Up"
        WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.ID, "signUp"))).click()
        # Chờ nút submit Sign Up hiện ra
        WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.ID, "b1_signup")))
        time.sleep(1) # Chờ animation slide xong

    def perform_signup_flow(self, email, password):
        """
        Điền form -> Click Sign Up -> Xử lý Modal Captcha (nếu hiện)
        Trả về: True nếu tick captcha thành công, False nếu không hiện captcha (do lỗi form)
        """
        driver = self.driver
        
        # 1. Điền thông tin
        WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.ID, "email"))).send_keys(email)
        driver.find_element(By.ID, "password").send_keys(password)
        
        # 2. Click nút Sign Up (b1_signup)
        driver.find_element(By.ID, "b1_signup").click()
        print(f"📝 Đã submit form đăng ký với Email: {email}")

        # 3. Xử lý Modal Captcha Sign Up
        # Modal ID: recaptchaSignUpModal
        try:
            print("⏳ Đang đợi Modal Captcha Sign Up hiện lên...")
            
            # Chờ cái Modal to bao bên ngoài hiện lên trước
            modal = WebDriverWait(driver, 5).until(
                EC.visibility_of_element_located((By.ID, "recaptchaSignUpModal"))
            )
            
            # Tìm iframe captacha NẰM BÊN TRONG modal đó
            # XPath: Tìm div id='recaptchaSignUpModal' -> tìm iframe con cháu của nó
            iframe_xpath = "//div[@id='recaptchaSignUpModal']//iframe[contains(@src, 'google.com/recaptcha')]"
            
            iframe = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, iframe_xpath))
            )
            
            # Switch vào iframe
            driver.switch_to.frame(iframe)
            
            # Click checkbox
            checkbox = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.ID, "recaptcha-anchor")))
            checkbox.click()
            print("✅ Đã tick Captcha Đăng Ký.")
            
            # Switch ra ngoài
            driver.switch_to.default_content()
            
            # Chờ server xử lý đăng ký xong
            time.sleep(3)
            return True

        except Exception as e:
            print(f"ℹ️ Không tick được Captcha (Có thể do form lỗi validate nên modal không hiện).")
            # Nếu đang ở trong iframe thì phải chui ra
            try:
                driver.switch_to.default_content()
            except:
                pass
            return False

    # --- CÁC TEST CASE ---

    def test_01_signup_success(self):
        """TC01: Đăng ký thành công -> Check Captcha -> Chuyển hướng"""
        print("\n--- TC01: Sign Up Success ---")
        self.switch_to_signup_mode()
        
        # Random Email
        rand = random.randint(10000, 99999)
        email = f"auto_test_{rand}@gmail.com"
        password = "password123"
        
        is_captcha_ticked = self.perform_signup_flow(email, password)
        
        self.assertTrue(is_captcha_ticked, "Lỗi: Captcha Modal không xuất hiện dù điền đúng thông tin!")
        
        # Assert kết quả (Ví dụ: URL thay đổi, hoặc hiện thông báo Success)
        # current_url = self.driver.current_url
        # self.assertNotIn("login.php", current_url, "Vẫn ở trang login sau khi đăng ký thành công!")

    def test_02_invalid_email(self):
        """TC02: Email sai format -> Không hiện Modal Captcha -> Hiện lỗi"""
        print("\n--- TC02: Invalid Email ---")
        self.switch_to_signup_mode()
        
        # Nhập sai email -> Hàm sẽ trả về False vì không thấy Captcha
        result = self.perform_signup_flow("email_sai_format", "123456")
        
        # 1. Kiểm tra Captcha KHÔNG được hiện
        self.assertFalse(result, "Lỗi: Captcha vẫn hiện dù email sai định dạng!")
        
        # 2. Kiểm tra thông báo lỗi
        xpath_invalid = "//input[@id='email']/ancestor::div[contains(@class, 'invalid')]"
        try:
            msg_elm = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.XPATH, xpath_invalid + "//span[@class='form-message']"))
            )
            print(f"Thông báo lỗi: {msg_elm.text}")
            self.assertEqual(msg_elm.text, "Trường này phải là email")
        except:
            self.fail("Không tìm thấy thông báo lỗi validate email.")

    def test_03_short_password(self):
        """TC03: Password ngắn -> Không hiện Modal Captcha -> Hiện lỗi"""
        print("\n--- TC03: Short Password ---")
        self.switch_to_signup_mode()
        
        result = self.perform_signup_flow("valid@test.com", "123")
        
        self.assertFalse(result, "Lỗi: Captcha vẫn hiện dù password quá ngắn!")
        
        xpath_invalid = "//input[@id='password']/ancestor::div[contains(@class, 'invalid')]"
        try:
            msg_elm = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.XPATH, xpath_invalid + "//span[@class='form-message']"))
            )
            print(f"Thông báo lỗi: {msg_elm.text}")
            self.assertEqual(msg_elm.text, "Vui lòng nhập tối thiểu 5 kí tự")
        except:
            self.fail("Không tìm thấy thông báo lỗi validate password.")

if __name__ == "__main__":
    unittest.main()