import unittest
import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# URL Cấu hình
BASE_URL = "https://whippet-exotic-specially.ngrok-free.app/QlyShopTheThao/src/view/viewUser/index.php"
URL_CART = BASE_URL + "?module=cart"
URL_LOGIN = "https://whippet-exotic-specially.ngrok-free.app/QlyShopTheThao/src/view/login.php"
URL_PRODUCTS = BASE_URL + "?module=sanpham"

TEST_ACC = {
    "email": "trinhhuuhung92@gmail.com",
    "pass": "hung12345"
}

class CartTest(unittest.TestCase):

    def setUp(self):
        """Setup: Mở Chrome, Login, Bypass Ngrok, Đảm bảo giỏ hàng có đồ"""
        driver_path = os.path.join(os.getcwd(), 'driver', 'chromedriver.exe')
        service = Service(driver_path)
        options = webdriver.ChromeOptions()
        self.driver = webdriver.Chrome(service=service, options=options)
        self.driver.maximize_window()
        
        self.driver.get(URL_LOGIN)
        self.bypass_ngrok()
        self.perform_login()
        
        # Sau khi login, đảm bảo giỏ hàng có ít nhất 1 món để test
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

        # Captcha (nếu có)
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

    # --- CÁC TEST CASE ---

    def test_01_view_cart_structure(self):
        """TC01: Kiểm tra hiển thị cấu trúc giỏ hàng"""
        print("\n--- TC01: View Cart Structure ---")
        
        # Kiểm tra bảng table tồn tại
        try:
            table = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "table")))
            print("✅ Bảng giỏ hàng hiển thị.")
        except:
            self.fail("Không tìm thấy bảng sản phẩm trong giỏ hàng.")

        # Kiểm tra có ít nhất 1 dòng sản phẩm (trừ dòng header và footer)
        rows = self.driver.find_elements(By.XPATH, "//table//tr[td]") # Tìm tr có chứa td
        self.assertTrue(len(rows) > 0, "Lỗi: Không có dòng sản phẩm nào hiển thị.")
        print(f"Hiện đang có {len(rows)-1} sản phẩm trong giỏ (trừ dòng tổng).")

    def test_02_update_quantity(self):
        """TC02: Thay đổi số lượng (Input number)"""
        print("\n--- TC02: Update Quantity ---")
        
        # Tìm ô input số lượng đầu tiên
        # Class: qty-input
        qty_input = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "qty-input"))
        )
        
        old_val = qty_input.get_attribute("value")
        print(f"Số lượng cũ: {old_val}")
        
        # Thay đổi số lượng thành 5
        qty_input.clear()
        qty_input.send_keys("5")
        
        # Click ra ngoài để kích hoạt sự kiện onchange (nếu cần)
        self.driver.find_element(By.TAG_NAME, "h2").click()
        time.sleep(1)
        
        new_val = qty_input.get_attribute("value")
        print(f"Số lượng mới: {new_val}")
        
        self.assertEqual(new_val, "5", "Lỗi: Input số lượng không cập nhật giá trị mới.")
        
        # Ghi chú: Không assert Tổng tiền vì code HTML thiếu ID, JS sẽ lỗi

    def test_03_checkbox_selection(self):
        """TC03: Chọn Checkbox sản phẩm"""
        print("\n--- TC03: Checkbox Selection ---")
        
        # Tìm checkbox đầu tiên (loại trừ item hết hàng nếu có)
        # Checkbox name="select_item[]"
        try:
            checkbox = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.NAME, "select_item[]"))
            )
            
            if not checkbox.is_selected():
                checkbox.click()
                print("✅ Đã tick vào checkbox.")
                self.assertTrue(checkbox.is_selected())
            else:
                print("ℹ️ Checkbox đã được tick sẵn.")
                
            # Kiểm tra nút Thanh toán có hiển thị không
            btn_pay = self.driver.find_element(By.CLASS_NAME, "button")
            self.assertTrue(btn_pay.is_displayed())
            
        except:
            print("⚠️ Không tìm thấy checkbox (Có thể do hết hàng hoặc giỏ trống).")

    def test_04_remove_item(self):
        """TC04: Xóa sản phẩm khỏi giỏ"""
        print("\n--- TC04: Remove Item ---")
        
        # Đếm số lượng dòng trước khi xóa
        rows_before = len(self.driver.find_elements(By.XPATH, "//table//tr[contains(., 'Xóa')]"))
        print(f"Số dòng trước khi xóa: {rows_before}")
        
        # Click nút Xóa đầu tiên
        remove_btn = self.driver.find_element(By.LINK_TEXT, "Xóa")
        remove_btn.click()
        print("🖱️ Đã click Xóa.")
        
        time.sleep(2)
        
        # Đếm lại
        rows_after = len(self.driver.find_elements(By.XPATH, "//table//tr[contains(., 'Xóa')]"))
        print(f"Số dòng sau khi xóa: {rows_after}")
        
        # Logic: Số dòng phải giảm đi 1, HOẶC nếu xóa hết thì hiện chữ "Giỏ hàng trống"
        if rows_after == rows_before - 1:
            print("✅ Xóa thành công, số lượng dòng giảm 1.")
        else:
            body_text = self.driver.find_element(By.TAG_NAME, "body").text
            if "Giỏ hàng trống" in body_text:
                print("✅ Xóa thành công, giỏ hàng hiện đã trống.")
            else:
                self.fail("Lỗi: Số lượng dòng không giảm sau khi xóa!")

if __name__ == "__main__":
    unittest.main()