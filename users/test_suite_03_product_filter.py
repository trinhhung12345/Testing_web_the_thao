import unittest
import time
import os
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select # Cần import cái này để xử lý Dropdown

# URL danh sách sản phẩm
URL_PRODUCTS = "https://whippet-exotic-specially.ngrok-free.app/QlyShopTheThao/src/view/viewUser/index.php?module=sanpham"

class ProductFilterTest(unittest.TestCase):

    def setUp(self):
        """Setup: Mở Chrome & Bypass Ngrok"""
        driver_path = os.path.join(os.getcwd(), 'driver', 'chromedriver.exe')
        service = Service(driver_path)
        options = webdriver.ChromeOptions()
        # options.add_argument("--headless") 
        self.driver = webdriver.Chrome(service=service, options=options)
        self.driver.maximize_window()
        self.driver.get(URL_PRODUCTS)
        self.bypass_ngrok()

    def tearDown(self):
        self.driver.quit()

    def bypass_ngrok(self):
        try:
            btn = WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Visit Site')]")))
            btn.click()
            time.sleep(2)
        except: pass

    # --- HÀM HỖ TRỢ (HELPER) ---
    def click_filter_button(self):
        """Tìm và click nút Lọc"""
        # HTML: <button type="submit" class="btn ..."><i class="fa fa-filter"></i> Lọc</button>
        # XPath: Tìm nút có type=submit và chứa chữ "Lọc"
        btn = self.driver.find_element(By.XPATH, "//button[@type='submit' and contains(., 'Lọc')]")
        
        # Scroll tới nút để tránh bị che
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
        time.sleep(0.5)
        btn.click()
        time.sleep(2) # Chờ trang reload kết quả

    def get_all_prices(self):
        """Lấy danh sách giá của tất cả sản phẩm đang hiển thị (dạng số nguyên)"""
        # HTML: <p style="color: orangered">Giá bán: 159,000₫</p>
        # XPath: Tìm thẻ <p> có chứa chữ "Giá bán:"
        price_elements = self.driver.find_elements(By.XPATH, "//p[contains(text(), 'Giá bán:')]")
        prices = []
        for elm in price_elements:
            text = elm.text # "Giá bán: 159,000₫"
            # Dùng Regex để chỉ lấy số: xóa hết chữ cái, dấu phẩy, ký tự lạ
            number_str = re.sub(r'\D', '', text) 
            if number_str:
                prices.append(int(number_str))
        return prices

    # --- CÁC TEST CASE ---

    def test_01_search_by_name(self):
        """TC01: Tìm kiếm sản phẩm (Input ID: search)"""
        print("\n--- Running: Test Search Product ---")
        keyword = "Aolikes"
        
        # 1. Nhập từ khóa
        search_input = self.driver.find_element(By.ID, "search")
        search_input.clear()
        search_input.send_keys(keyword)
        
        # 2. Click nút Lọc
        self.click_filter_button()
        
        # 3. CẬP NHẬT: Tìm tiêu đề chính xác hơn
        # Chỉ lấy thẻ h3 nằm trong div có class='product-item'
        xpath_titles = "//div[contains(@class, 'product-item')]//h3[contains(@class, 'h3-title')]"
        titles = self.driver.find_elements(By.XPATH, xpath_titles)
        
        if not titles:
            self.fail(f"Không tìm thấy sản phẩm nào với từ khóa '{keyword}'")

        print(f"Tìm thấy {len(titles)} sản phẩm.")
        
        for title in titles:
            # Lấy text và loại bỏ khoảng trắng thừa
            product_name = title.text.strip()
            print(f" - {product_name}")
            
            # Nếu tên rỗng (do lỗi load) thì bỏ qua
            if not product_name: 
                continue
                
            # Assert: Kiểm tra xem tên sản phẩm có chứa từ khóa không
            self.assertIn(keyword.lower(), product_name.lower(), 
                          f"Lỗi: Sản phẩm '{product_name}' không chứa từ khóa '{keyword}'")

    def test_02_filter_by_price_range(self):
        """TC02: Lọc theo khoảng giá (Input name: price_min, price_max)"""
        print("\n--- Running: Test Price Filter ---")
        min_price = 50000
        max_price = 200000
        
        # 1. Nhập khoảng giá
        self.driver.find_element(By.NAME, "price_min").send_keys(str(min_price))
        self.driver.find_element(By.NAME, "price_max").send_keys(str(max_price))
        
        # 2. Click nút Lọc
        self.click_filter_button()
        
        # 3. Kiểm tra giá các sản phẩm hiển thị
        prices = self.get_all_prices()
        
        if not prices:
            self.fail("Không có sản phẩm nào trong khoảng giá này (hoặc lỗi locator).")
            
        print(f"Giá các sản phẩm tìm thấy: {prices}")
        
        for price in prices:
            # Kiểm tra từng giá phải nằm trong khoảng Min-Max
            self.assertTrue(min_price <= price <= max_price, 
                            f"Lỗi: Giá {price} nằm ngoài khoảng {min_price}-{max_price}")

    def test_03_sort_price_ascending(self):
        """TC03: Sắp xếp giá Tăng dần (Select ID: sort, value: asc)"""
        print("\n--- Running: Test Sort Ascending ---")
        
        # 1. Chọn Dropdown
        sort_dropdown = Select(self.driver.find_element(By.ID, "sort"))
        sort_dropdown.select_by_value("asc") # value="asc" trong HTML
        
        # 2. Click nút Lọc (Vì form HTML thường yêu cầu submit mới sort)
        self.click_filter_button()
        
        # 3. Lấy danh sách giá
        prices = self.get_all_prices()
        print(f"Danh sách giá sau khi sort Tăng dần: {prices}")
        
        # 4. Logic kiểm tra: Giá sau phải lớn hơn hoặc bằng giá trước
        # Cách nhanh nhất: So sánh list hiện tại với list đã được sort bằng code Python
        sorted_prices = sorted(prices)
        self.assertEqual(prices, sorted_prices, "Lỗi: Danh sách chưa được sắp xếp tăng dần!")

    def test_04_sort_price_descending(self):
        """TC04: Sắp xếp giá Giảm dần (Select ID: sort, value: desc)"""
        print("\n--- Running: Test Sort Descending ---")
        
        # 1. Chọn Dropdown
        sort_dropdown = Select(self.driver.find_element(By.ID, "sort"))
        sort_dropdown.select_by_value("desc") # value="desc"
        
        # 2. Click nút Lọc
        self.click_filter_button()
        
        # 3. Lấy danh sách giá
        prices = self.get_all_prices()
        print(f"Danh sách giá sau khi sort Giảm dần: {prices}")
        
        # 4. Logic kiểm tra: List hiện tại phải bằng List sort ngược
        sorted_prices_desc = sorted(prices, reverse=True)
        self.assertEqual(prices, sorted_prices_desc, "Lỗi: Danh sách chưa được sắp xếp giảm dần!")

if __name__ == "__main__":
    unittest.main()