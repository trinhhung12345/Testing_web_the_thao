import unittest
import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- CẤU HÌNH DỮ LIỆU TEST ---
URL_LOGIN = "https://whippet-exotic-specially.ngrok-free.app/QlyShopTheThao/src/view/login.php"

# Tài khoản Admin thật trong DB
ADMIN_ACC = {"email": "wearingarmor12345@gmail.com", "pass": "hung12345"} 

# Tài khoản User thường thật trong DB (Bạn tự điền thêm vào nhé)
USER_ACC = {"email": "killerqueen2337@gmail.com", "pass": "hung12345"} 

class LoginTest(unittest.TestCase):

    def setUp(self):
        """Hàm chạy TRƯỚC mỗi test case: Mở trình duyệt + Bypass Ngrok"""
        driver_path = os.path.join(os.getcwd(), 'driver', 'chromedriver.exe')
        service = Service(driver_path)
        options = webdriver.ChromeOptions()
        # options.add_argument("--headless") # Bỏ comment nếu muốn chạy ẩn
        self.driver = webdriver.Chrome(service=service, options=options)
        self.driver.maximize_window()
        
        # 1. Mở trang web
        self.driver.get(URL_LOGIN)
        
        # 2. Bypass Ngrok (Nếu có)
        try:
            visit_btn = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Visit Site')]"))
            )
            visit_btn.click()
            time.sleep(2)
        except:
            pass # Không có ngrok warning thì bỏ qua

    def tearDown(self):
        """Hàm chạy SAU mỗi test case: Đóng trình duyệt"""
        self.driver.quit()

    # --- HÀM HỖ TRỢ (HELPER) ---
    def perform_login(self, email, password):
        """Điền form -> Click Submit -> Xử lý Captcha"""
        driver = self.driver
        
        # Điền Email
        email_input = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "email_signin")))
        email_input.clear()
        email_input.send_keys(email)
        
        # Điền Pass
        driver.find_element(By.ID, "password_signin").send_keys(password)
        
        # Click Sign In (ID: b1)
        driver.find_element(By.ID, "b1").click()
        
        # Xử lý Captcha (Chỉ khi form valid thì modal mới hiện)
        try:
            iframe = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "iframe[src*='google.com/recaptcha']"))
            )
            driver.switch_to.frame(iframe)
            checkbox = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.ID, "recaptcha-anchor")))
            checkbox.click()
            driver.switch_to.default_content()
            
            # Chờ server xử lý đăng nhập (Wait for URL change or reload)
            time.sleep(5) 
            return True
        except:
            # Nếu không hiện captcha (do lỗi validate form), trả về False
            return False

    # --- CÁC TEST CASE CHÍNH ---

    def test_01_login_admin_success(self):
        """TC01: Đăng nhập Admin thành công -> Vào trang Admin"""
        print("\n--- Running: Test Admin Login ---")
        self.perform_login(ADMIN_ACC['email'], ADMIN_ACC['pass'])
        
        # Kiểm tra URL hiện tại có chứa từ khóa của trang admin không
        current_url = self.driver.current_url
        print(f"URL sau khi login: {current_url}")
        
        # Assert: Mong đợi URL chứa 'ViewAdmin'
        self.assertIn("ViewAdmin/index.php", current_url, "Lỗi: Không chuyển hướng vào trang Admin!")

    def test_02_login_user_success(self):
        """TC02: Đăng nhập User thường thành công -> Vào trang Shop"""
        print("\n--- Running: Test User Login ---")
        self.perform_login(USER_ACC['email'], USER_ACC['pass'])
        
        current_url = self.driver.current_url
        print(f"URL sau khi login: {current_url}")
        
        # Assert: Mong đợi URL chứa 'ViewUser'
        self.assertIn("ViewUser/Index.php", current_url, "Lỗi: Không chuyển hướng vào trang User!")

    def test_03_invalid_email_format(self):
        """TC03: Email sai định dạng -> Kiểm tra class 'invalid' được kích hoạt"""
        print("\n--- Running: Test Invalid Email Format ---")
        
        driver = self.driver

        # 1. Tự thực hiện thao tác (Không dùng perform_login để kiểm soát kỹ hơn)
        print("Nhập email sai...")
        email_input = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "email_signin")))
        email_input.clear()
        email_input.send_keys("admin_khong_co_a_cong") # Sai format
        
        driver.find_element(By.ID, "password_signin").send_keys("123456")
        
        # Click Sign in để kích hoạt validation
        driver.find_element(By.ID, "b1").click()
        print("Đã click Sign in.")

        # 2. QUAN TRỌNG: Chờ thẻ DIV cha xuất hiện class "invalid"
        # Logic: Khi lỗi, div cha sẽ biến thành <div class="form-group invalid">
        try:
            # CSS Selector này nghĩa là: Tìm thẻ div có CẢ 2 class là 'form-group' và 'invalid'
            # Và nó phải chứa input có id là 'email_signin' bên trong
            parent_xpath = "//input[@id='email_signin']/ancestor::div[contains(@class, 'invalid')]"
            
            print("Đang chờ class 'invalid' xuất hiện...")
            
            # Chờ tối đa 5s để JS xử lý và thêm class vào
            invalid_div = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, parent_xpath))
            )
            print("✅ Phát hiện class 'invalid' -> Validation đã hoạt động!")

            # 3. (Tùy chọn) Bây giờ mới lấy text ra để kiểm tra
            # Vì div cha đã invalid, chắc chắn span con sẽ hiện ra
            msg_element = invalid_div.find_element(By.CLASS_NAME, "form-message")
            actual_msg = msg_element.text
            print(f"Nội dung thông báo: '{actual_msg}'")
            
            self.assertEqual(actual_msg, "Trường này phải là email")

        except Exception as e:
            # Nếu lỗi, in ra HTML của thẻ cha để debug xem class thực sự của nó là gì
            print("❌ Test Failed.")
            try:
                parent = driver.find_element(By.XPATH, "//input[@id='email_signin']/ancestor::div")
                print(f"HTML của thẻ cha hiện tại: {parent.get_attribute('outerHTML')}")
            except:
                pass
            self.fail("Không tìm thấy class 'invalid' trên form-group. Có thể JS validation chưa chạy.")

    def test_04_show_password_feature(self):
        """TC06: Chức năng hiện mật khẩu"""
        print("\n--- Running: Test Show Password ---")
        driver = self.driver
        
        pass_input = driver.find_element(By.ID, "password_signin")
        pass_input.send_keys("secret123")
        
        # Kiểm tra type ban đầu là password
        self.assertEqual(pass_input.get_attribute("type"), "password")
        
        # Click checkbox Show Password
        driver.find_element(By.ID, "showPassword").click()
        
        # Kiểm tra type đã đổi thành text chưa
        self.assertEqual(pass_input.get_attribute("type"), "text", "Lỗi: Mật khẩu không hiển thị khi check Show Password")

if __name__ == "__main__":
    unittest.main()