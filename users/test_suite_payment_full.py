import unittest
import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- CẤU HÌNH URL ---
BASE_URL = "https://whippet-exotic-specially.ngrok-free.app/QlyShopTheThao/src/view/viewUser/index.php"
URL_CART = BASE_URL + "?module=cart"
URL_LOGIN = "https://whippet-exotic-specially.ngrok-free.app/QlyShopTheThao/src/view/login.php"
URL_PRODUCTS = BASE_URL + "?module=sanpham"
URL_HISTORY = BASE_URL + "?module=orderhistory"

TEST_ACC = {"email": "trinhhuuhung92@gmail.com", "pass": "hung12345"}

class PaymentFullTest(unittest.TestCase):

    def setUp(self):
        """Setup: Mở Chrome, Login, Bypass Ngrok"""
        driver_path = os.path.join(os.getcwd(), 'driver', 'chromedriver.exe')
        service = Service(driver_path)
        options = webdriver.ChromeOptions()
        self.driver = webdriver.Chrome(service=service, options=options)
        self.driver.maximize_window()
        
        self.driver.get(URL_LOGIN)
        self.bypass_ngrok()
        self.perform_login()

    def tearDown(self):
        self.driver.quit()

    def bypass_ngrok(self):
        try:
            btn = WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Visit Site')]")))
            btn.click()
            time.sleep(2)
        except: pass

    def perform_login(self):
        driver = self.driver
        if "login.php" not in driver.current_url:
            driver.get(URL_LOGIN)
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "email_signin"))).send_keys(TEST_ACC['email'])
        driver.find_element(By.ID, "password_signin").send_keys(TEST_ACC['pass'])
        driver.find_element(By.ID, "b1").click()
        try:
            iframe = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, "iframe[src*='google.com/recaptcha']")))
            driver.switch_to.frame(iframe)
            WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.ID, "recaptcha-anchor"))).click()
            driver.switch_to.default_content()
            time.sleep(3)
        except: pass

    def ensure_cart_has_item(self):
        self.driver.get(URL_CART)
        if "Giỏ hàng trống" in self.driver.find_element(By.TAG_NAME, "body").text:
            self.driver.get(URL_PRODUCTS)
            try:
                xpath = "(//a[contains(@href, 'module=cart') and contains(@href, 'act=add')])[1]"
                add_btn = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, xpath)))
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", add_btn)
                time.sleep(1)
                self.driver.execute_script("arguments[0].click();", add_btn)
                time.sleep(2)
                try: self.driver.switch_to.alert.accept() 
                except: pass
            except: pass

    def prepare_checkout(self):
        self.ensure_cart_has_item()
        self.driver.get(URL_CART)
        try:
            cb = WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.NAME, "select_item[]")))
            if not cb.is_selected():
                self.driver.execute_script("arguments[0].click();", cb)
        except: pass
        self.driver.execute_script("arguments[0].click();", self.driver.find_element(By.CLASS_NAME, "button"))
        WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.ID, "hoten"))).send_keys("Tester Auto")
        self.driver.find_element(By.ID, "dienthoai").send_keys("0912345678")
        self.driver.find_element(By.ID, "diachi").send_keys("123 Test Street")

    # --- HÀM MỚI: CHECK SUCCESS -> CLICK VỀ TRANG CHỦ ---
    def process_success_page_and_return_home(self):
        """
        1. Chờ giao diện Success hiện ra (bất kể URL là Success.php hay success.php)
        2. Click nút 'Về trang chủ'
        3. Chờ trang chủ load xong
        """
        print("🎉 Đang kiểm tra trang Success...")
        try:
            # THAY ĐỔI QUAN TRỌNG:
            # Không chờ URL nữa, mà chờ cái hộp thông báo (success-container) hiện lên.
            # Cách này chạy đúng cho cả COD (success.php) và Stripe (Success.php).
            container = WebDriverWait(self.driver, 20).until(
                EC.visibility_of_element_located((By.CLASS_NAME, "success-container"))
            )
            
            # Check nội dung text
            success_text = container.text
            print(f"Nội dung Success: {success_text}")
            self.assertIn("Đặt hàng thành công", success_text)
            
            # Tìm và Click nút 'Về trang chủ'
            print("🖱️ Đang click nút 'Về trang chủ'...")
            btn_home = self.driver.find_element(By.CLASS_NAME, "btn-home")
            self.driver.execute_script("arguments[0].click();", btn_home)
            
            # Chờ quay về trang chủ
            print("⏳ Đang chờ quay về Trang chủ...")
            # Chỉ cần chờ URL chứa "Index.php" hoặc "module=home" là đủ
            WebDriverWait(self.driver, 15).until(
                lambda d: "Index.php" in d.current_url or "module=home" in d.current_url
            )
            print("✅ Đã về trang chủ.")
            
        except Exception as e:
            self.fail(f"Lỗi xử lý trang Success: {e}")

    def check_latest_order_status(self, expected_status_text):
        """Vào lịch sử -> Check status đơn mới nhất"""
        print(f"🔍 Vào Lịch sử đơn hàng check status: '{expected_status_text}'")
        self.driver.get(URL_HISTORY)
        try:
            # Lấy trạng thái dòng đầu tiên
            status_badge = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//table/tbody/tr[1]//span[contains(@class, 'order-status-badge')]"))
            )
            actual_status = status_badge.text.strip().lower()
            print(f"📝 Trạng thái thực tế: {actual_status}")
            self.assertIn(expected_status_text.lower(), actual_status)
            print("✅ Status khớp.")
        except Exception as e:
            self.fail(f"Lỗi check status: {e}")

    # --- TEST CASES ---

    def test_01_cod_order_status(self):
        """TC01: COD -> Success -> Click Home -> History 'Đang xử lý'"""
        print("\n--- TC01: COD Flow ---")
        self.prepare_checkout()
        
        self.driver.execute_script("arguments[0].click();", self.driver.find_element(By.ID, "cod"))
        self.driver.find_element(By.ID, "dathang").click()
        
        # 1. Check Success Page VÀ Click về trang chủ
        self.process_success_page_and_return_home()
        
        # 2. Vào lịch sử check
        self.check_latest_order_status("Đang xử lý")

    def test_02_stripe_success_status(self):
        """TC02: Stripe Pay -> Success -> Click Home -> History 'Đã thanh toán'"""
        print("\n--- TC02: Stripe Success Flow ---")
        self.prepare_checkout()
        
        self.driver.execute_script("arguments[0].click();", self.driver.find_element(By.ID, "stripe"))
        self.driver.find_element(By.ID, "dathang").click()
        
        print("⏳ Sang Stripe...")
        try:
            email_input = WebDriverWait(self.driver, 40).until(EC.visibility_of_element_located((By.ID, "email")))
            if not email_input.get_attribute("value"):
                email_input.send_keys("test_stripe@gmail.com")

            card_input = self.driver.find_element(By.ID, "cardNumber")
            card_input.clear()
            for digit in "4242424242424242":
                card_input.send_keys(digit)
                time.sleep(0.05)
            
            self.driver.find_element(By.ID, "cardExpiry").send_keys("1230")
            self.driver.find_element(By.ID, "cardCvc").send_keys("123")
            self.driver.find_element(By.ID, "billingName").send_keys("Tester")
            
            self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
            
            print("⏳ Đang xử lý thanh toán (5s)...")
            time.sleep(5) 
            
            # 1. Check Success Page VÀ Click về trang chủ
            self.process_success_page_and_return_home()
            
            # 2. Vào lịch sử check
            self.check_latest_order_status("Đã thanh toán")
            
        except Exception as e:
            self.fail(f"Lỗi Stripe Flow: {e}")

    def test_03_stripe_cancel_status(self):
        """TC03: Stripe -> Click nút Back trên trang Stripe -> Check History 'Hủy'"""
        print("\n--- TC03: Stripe Cancel Flow ---")
        self.prepare_checkout()
        
        # Chọn Stripe và Đặt hàng
        self.driver.execute_script("arguments[0].click();", self.driver.find_element(By.ID, "stripe"))
        self.driver.find_element(By.ID, "dathang").click()
        
        print("⏳ Đang chuyển hướng sang Stripe...")
        try:
            # 1. Chờ trang Stripe load xong (xuất hiện ô Email)
            WebDriverWait(self.driver, 40).until(EC.visibility_of_element_located((By.ID, "email")))
            print("✅ Đã vào giao diện Stripe.")
            
            # 2. Tìm nút Back trên giao diện Stripe
            # Sử dụng data-testid="business-link" như bạn cung cấp
            print("🔙 Đang tìm nút mũi tên Back...")
            back_link = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "a[data-testid='business-link']"))
            )
            
            # Click nút Back
            back_link.click()
            print("🖱️ Đã click nút Back trên trang Stripe.")
            
            # 3. Chờ quay về website (URL Payment.php)
            print("⏳ Đang quay lại website...")
            WebDriverWait(self.driver, 30).until(EC.url_contains("Payment.php"))
            print("✅ Đã quay về trang Payment.")
            
            # Chờ server cập nhật trạng thái hủy vào DB (quan trọng)
            time.sleep(5)
            
            # 4. Vào lịch sử check trạng thái "Hủy"
            self.check_latest_order_status("hủy")
            
        except Exception as e:
            self.fail(f"Lỗi Stripe Cancel Flow: {e}")

if __name__ == "__main__":
    unittest.main()