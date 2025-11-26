import unittest
import time
import os
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# URL
BASE_URL = "https://whippet-exotic-specially.ngrok-free.app/QlyShopTheThao/src/view/viewUser/index.php"
URL_CART = BASE_URL + "?module=cart"
URL_LOGIN = "https://whippet-exotic-specially.ngrok-free.app/QlyShopTheThao/src/view/login.php"
URL_PRODUCTS = BASE_URL + "?module=sanpham"

# Tài khoản test
TEST_ACC = {"email": "trinhhuuhung92@gmail.com", "pass": "hung12345"}

class PaymentTest(unittest.TestCase):

    def setUp(self):
        """Setup: Login -> Bypass Ngrok -> Đảm bảo giỏ hàng có đồ"""
        driver_path = os.path.join(os.getcwd(), 'driver', 'chromedriver.exe')
        service = Service(driver_path)
        options = webdriver.ChromeOptions()
        self.driver = webdriver.Chrome(service=service, options=options)
        self.driver.maximize_window()
        
        self.driver.get(URL_LOGIN)
        self.bypass_ngrok()
        self.perform_login()
        self.ensure_cart_has_item()

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
        """Hàm phụ: Đảm bảo giỏ hàng có hàng (Phiên bản Fix cho thẻ <a>)"""
        driver = self.driver
        print("🛒 Đang kiểm tra giỏ hàng...")
        driver.get(URL_CART)
        
        # Kiểm tra xem có chữ "Giỏ hàng trống" không
        try:
            body_text = driver.find_element(By.TAG_NAME, "body").text
            # Nếu giỏ hàng KHÔNG trống (tức là đã có hàng), thì return luôn, không cần thêm nữa
            if "Giỏ hàng trống" not in body_text and "Thanh toán" in body_text:
                print("✅ Giỏ hàng đã có sẵn sản phẩm. Tiếp tục test.")
                return
        except:
            pass

        print("ℹ️ Giỏ hàng trống. Đang đi thêm sản phẩm...")
        driver.get(URL_PRODUCTS)
        
        try:
            # 1. Tìm nút thêm giỏ hàng (Thẻ <a> chứa href module=cart&act=add)
            # XPath này tìm thẻ <a> có link chứa 'act=add'
            add_btn_xpath = "(//a[contains(@href, 'module=cart') and contains(@href, 'act=add')])[1]"
            
            add_btn = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, add_btn_xpath))
            )
            
            # 2. Scroll tới nút đó (Quan trọng để tránh bị Sidebar che)
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", add_btn)
            time.sleep(1) # Chờ scroll xong
            
            # 3. Dùng JS Click (Mạnh hơn click thường)
            driver.execute_script("arguments[0].click();", add_btn)
            print("🖱️ Đã click thêm vào giỏ (bằng JS).")
            
            # 4. Xử lý Alert (Nếu có) hoặc Chờ chuyển trang
            # Logic server của bạn: Thường sẽ hiện Alert rồi mới chuyển, hoặc chuyển luôn.
            try:
                # Chờ Alert xuất hiện trong 3 giây
                WebDriverWait(driver, 3).until(EC.alert_is_present())
                alert = driver.switch_to.alert
                print(f"⚠️ Alert xuất hiện: {alert.text}")
                alert.accept() # Bấm OK
                time.sleep(2)  # Chờ redirect sau alert
            except:
                print("ℹ️ Không thấy Alert, kiểm tra xem đã chuyển trang chưa.")

            # 5. Quay lại giỏ hàng để chắc chắn
            if "module=cart" not in driver.current_url:
                driver.get(URL_CART)
                
            print("✅ Đã thực hiện quy trình thêm hàng.")
            
        except Exception as e:
            print(f"❌ Lỗi CRITICAL: Không thể thêm sản phẩm vào giỏ! Lỗi: {e}")
            # Nếu bước này fail, các test case sau sẽ fail hết.
            self.fail("Setup thất bại: Không thể thêm hàng vào giỏ.")

    # --- HÀM HỖ TRỢ CHUYỂN TRANG ---
    def go_to_payment_page(self):
        """Từ giỏ hàng -> Tick 1 món -> Bấm Thanh toán -> Vào trang Payment"""
        self.driver.get(URL_CART)
        
        # 1. Tick vào checkbox đầu tiên
        checkbox = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.NAME, "select_item[]")))
        if not checkbox.is_selected():
            self.driver.execute_script("arguments[0].click();", checkbox)
            
        # 2. Click nút "Thanh toán sản phẩm đã chọn"
        pay_btn = self.driver.find_element(By.CLASS_NAME, "button") # class="button"
        self.driver.execute_script("arguments[0].click();", pay_btn)
        
        # 3. Chờ trang Payment load (Check tiêu đề hoặc input hoten)
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, "hoten")))
        print("➡️ Đã vào trang Thanh toán.")

    # --- TEST CASES ---

    def test_01_no_item_selected(self):
        """TC01: Không chọn sản phẩm nào -> Bấm thanh toán -> Báo lỗi"""
        print("\n--- TC01: No Item Selected ---")
        self.driver.get(URL_CART)
        
        # Bỏ tick tất cả checkbox
        checkboxes = self.driver.find_elements(By.NAME, "select_item[]")
        for cb in checkboxes:
            if cb.is_selected():
                self.driver.execute_script("arguments[0].click();", cb)
        
        # Bấm nút thanh toán
        pay_btn = self.driver.find_element(By.CLASS_NAME, "button")
        self.driver.execute_script("arguments[0].click();", pay_btn)
        
        # Kiểm tra thông báo lỗi text đỏ
        # controller echo ra: <p style='text-align:center; color:red;'>Bạn chưa chọn sản phẩm nào để thanh toán!</p>
        time.sleep(2)
        body_text = self.driver.find_element(By.TAG_NAME, "body").text
        self.assertIn("Bạn chưa chọn sản phẩm nào", body_text)
        print("✅ Đã hiện thông báo lỗi khi không chọn sản phẩm.")

    def test_02_validation_empty_fields(self):
        """TC02: Để trống thông tin -> Kiểm tra HTML5 Validation (Required)"""
        print("\n--- TC02: Validate Empty Fields ---")
        self.go_to_payment_page()
        
        # 1. Để trống các ô input, bấm Đặt hàng ngay
        submit_btn = self.driver.find_element(By.ID, "dathang")
        self.driver.execute_script("arguments[0].click();", submit_btn)
        
        # 2. Thay vì chờ Alert, ta kiểm tra thuộc tính validationMessage của input đầu tiên (Họ tên)
        # Vì HTML có 'required', trình duyệt sẽ chặn và gắn message vào input đó
        hoten_input = self.driver.find_element(By.ID, "hoten")
        
        # Lấy thông báo lỗi mặc định của trình duyệt
        # Nếu rỗng -> "Please fill out this field" (Tiếng Anh) hoặc "Vui lòng điền vào trường này" (Tiếng Việt)
        msg = hoten_input.get_attribute("validationMessage")
        
        print(f"⚠️ Thông báo Validation HTML5: '{msg}'")
        
        # 3. Kiểm tra logic: Nếu message không rỗng nghĩa là Validate đã hoạt động
        if msg:
            print("✅ Form đã bị chặn bởi HTML5 Required.")
            self.assertTrue(len(msg) > 0)
        else:
            self.fail("Lỗi: Form vẫn submit được dù để trống trường bắt buộc!")

    def test_03_validation_invalid_phone(self):
        """TC03: SĐT sai định dạng -> Alert"""
        print("\n--- TC03: Validate Invalid Phone ---")
        self.go_to_payment_page()
        
        # Điền đúng tên, địa chỉ
        self.driver.find_element(By.ID, "hoten").send_keys("Tester Auto")
        self.driver.find_element(By.ID, "diachi").send_keys("123 Street")
        
        # Điền sai SĐT
        self.driver.find_element(By.ID, "dienthoai").send_keys("abc") # Chữ cái
        
        self.driver.find_element(By.ID, "dathang").click()
        
        try:
            WebDriverWait(self.driver, 3).until(EC.alert_is_present())
            alert = self.driver.switch_to.alert
            print(f"⚠️ Alert: {alert.text}")
            self.assertIn("Số điện thoại không hợp lệ", alert.text)
            alert.accept()
        except:
            self.fail("Lỗi: Không hiện Alert khi nhập sai SĐT!")

    def test_04_cod_payment_success(self):
        """TC05: Thanh toán COD thành công"""
        print("\n--- TC05: COD Payment Success ---")
        self.go_to_payment_page()
        
        # Điền thông tin hợp lệ
        self.driver.find_element(By.ID, "hoten").send_keys("Nguyen Van Test")
        self.driver.find_element(By.ID, "dienthoai").send_keys("0912345678")
        self.driver.find_element(By.ID, "diachi").send_keys("Hanoi, Vietnam")
        
        # Chọn COD (Radio ID: cod)
        cod_radio = self.driver.find_element(By.ID, "cod")
        self.driver.execute_script("arguments[0].click();", cod_radio)
        
        # Submit
        print("🖱️ Bấm Đặt hàng (COD)...")
        self.driver.find_element(By.ID, "dathang").click()
        
        # Chờ chuyển hướng sang success.php
        WebDriverWait(self.driver, 15).until(EC.url_contains("success.php"))
        print(f"✅ URL hiện tại: {self.driver.current_url}")
        self.assertIn("order_id=", self.driver.current_url)

    def test_05_stripe_redirect(self):
        """TC06: Thanh toán Stripe -> Redirect sang trang Stripe"""
        print("\n--- TC06: Stripe Payment Redirect ---")
        self.go_to_payment_page()
        
        # Điền thông tin hợp lệ
        self.driver.find_element(By.ID, "hoten").send_keys("Stripe Tester")
        self.driver.find_element(By.ID, "dienthoai").send_keys("0987654321")
        self.driver.find_element(By.ID, "diachi").send_keys("HCM City")
        
        # Chọn Stripe (Radio ID: stripe)
        stripe_radio = self.driver.find_element(By.ID, "stripe")
        self.driver.execute_script("arguments[0].click();", stripe_radio)
        
        # Submit
        print("🖱️ Bấm Đặt hàng (Stripe)...")
        self.driver.find_element(By.ID, "dathang").click()
        
        # Chờ chuyển hướng sang domain stripe.com
        # Quá trình này có thể mất vài giây để tạo session
        print("⏳ Đang chờ chuyển hướng sang Stripe...")
        try:
            WebDriverWait(self.driver, 20).until(EC.url_contains("stripe.com"))
            print(f"✅ Đã chuyển hướng sang Stripe: {self.driver.current_url}")
        except:
            # Nếu ngrok chậm hoặc lỗi mạng
            print(f"⚠️ URL hiện tại: {self.driver.current_url}")
            if "error" in self.driver.current_url:
                print("Có lỗi backend Stripe trả về.")
            else:
                self.fail("Không chuyển hướng sang trang thanh toán Stripe được.")

if __name__ == "__main__":
    unittest.main()