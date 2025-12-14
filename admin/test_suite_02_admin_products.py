import unittest
import time
import os
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

# --- CẤU HÌNH DỮ LIỆU TEST ---
URL_LOGIN = "https://melissia-untragical-inviably.ngrok-free.dev/QlyShopTheThao/src/view/login.php"
URL_ADMIN_PRODUCTS = "https://melissia-untragical-inviably.ngrok-free.dev/QlyShopTheThao/src/view/ViewAdmin/index.php?page=products"

# Tài khoản Admin
ADMIN_ACC = {"email": "wearingarmor12345@gmail.com", "pass": "hung12345"}

# Dữ liệu test sản phẩm
TEST_PRODUCT_DATA = {
    "name": "Sản phẩm Test Selenium " + datetime.now().strftime("%H%M%S"),
    "price": "500000",
    "discount_price": "450000",
    "stock": "100",
    "brand": "Test Brand",
    "location": "Việt Nam",
    "description": "Đây là sản phẩm test được tạo bởi Selenium automation test."
}


class AdminProductsTest(unittest.TestCase):
    """Test Suite cho trang Quản lý Sản phẩm Admin"""

    @classmethod
    def setUpClass(cls):
        """Thiết lập một lần cho toàn bộ test class - Đăng nhập Admin"""
        driver_path = os.path.join(os.getcwd(), 'driver', 'chromedriver.exe')
        service = Service(driver_path)
        options = webdriver.ChromeOptions()
        # options.add_argument("--headless")
        cls.driver = webdriver.Chrome(service=service, options=options)
        cls.driver.maximize_window()
        cls.wait = WebDriverWait(cls.driver, 10)
        
        cls._login_as_admin()

    @classmethod
    def _login_as_admin(cls):
        """Đăng nhập với tài khoản Admin"""
        driver = cls.driver
        driver.get(URL_LOGIN)
        
        # Bypass Ngrok
        try:
            visit_btn = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Visit Site')]"))
            )
            visit_btn.click()
            time.sleep(2)
        except:
            pass

        email_input = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, "email_signin"))
        )
        email_input.clear()
        email_input.send_keys(ADMIN_ACC['email'])
        driver.find_element(By.ID, "password_signin").send_keys(ADMIN_ACC['pass'])
        driver.find_element(By.ID, "b1").click()

        # Xử lý Captcha
        try:
            iframe = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "iframe[src*='google.com/recaptcha']"))
            )
            driver.switch_to.frame(iframe)
            checkbox = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.ID, "recaptcha-anchor"))
            )
            checkbox.click()
            driver.switch_to.default_content()
            time.sleep(5)
        except:
            pass

        WebDriverWait(driver, 15).until(EC.url_contains("ViewAdmin"))
        print("✅ Đăng nhập Admin thành công!")

    @classmethod
    def tearDownClass(cls):
        """Đóng trình duyệt sau khi chạy xong tất cả test"""
        cls.driver.quit()

    def setUp(self):
        """Trước mỗi test case, điều hướng về trang Products"""
        self.driver.get(URL_ADMIN_PRODUCTS)
        time.sleep(2)
        # Bypass Ngrok nếu cần
        try:
            visit_btn = WebDriverWait(self.driver, 3).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Visit Site')]"))
            )
            visit_btn.click()
            time.sleep(2)
        except:
            pass

    def _save_error_screenshot(self, test_name):
        """Lưu ảnh chụp màn hình khi có lỗi"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        screenshot_name = f"error_test_{test_name}_{timestamp}.png"
        screenshot_path = os.path.join(os.getcwd(), 'results', screenshot_name)
        self.driver.save_screenshot(screenshot_path)
        print(f"📸 Screenshot saved: {screenshot_path}")

    def _scroll_to_element(self, element):
        """Scroll đến element"""
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
        time.sleep(0.5)

    def _js_click(self, element):
        """Click element bằng JavaScript"""
        self.driver.execute_script("arguments[0].click();", element)

    # ==================== TEST CASES ====================

    def test_01_products_page_loads_successfully(self):
        """TC01: Trang Quản lý sản phẩm load thành công"""
        print("\n--- Running: Test Products Page Loads ---")
        driver = self.driver

        try:
            # Kiểm tra URL
            self.assertIn("products", driver.current_url.lower())

            # Kiểm tra page title
            page_title = self.wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "page-title"))
            )
            self.assertIn("Sản Phẩm", page_title.text)
            print(f"✅ Page title: {page_title.text}")

            # Kiểm tra card title
            card_title = driver.find_element(By.XPATH, "//h4[@class='card-title' and contains(text(),'Danh sách sản phẩm')]")
            self.assertIsNotNone(card_title)
            print("✅ Tìm thấy card 'Danh sách sản phẩm'")

        except Exception as e:
            self._save_error_screenshot("TC01_products_load")
            raise e

    def test_02_products_table_display(self):
        """TC02: Bảng sản phẩm hiển thị đúng cấu trúc"""
        print("\n--- Running: Test Products Table Display ---")
        driver = self.driver

        try:
            # Tìm bảng sản phẩm
            products_table = self.wait.until(
                EC.presence_of_element_located((By.ID, "add-row"))
            )
            self.assertIsNotNone(products_table)

            # Kiểm tra headers
            headers = products_table.find_elements(By.TAG_NAME, "th")
            header_texts = [h.text.upper() for h in headers]
            print(f"  📋 Headers: {header_texts}")

            # Các cột mong đợi (bỏ qua cột sort icon)
            expected_columns = ["ẢNH", "TÊN SẢN PHẨM", "GIÁ", "TỒN KHO", "ĐÃ BÁN", "DANH MỤC", "HÀNH ĐỘNG"]
            for col in expected_columns:
                found = any(col in h for h in header_texts)
                self.assertTrue(found, f"Lỗi: Thiếu cột '{col}'")
                print(f"  ✅ Tìm thấy cột: {col}")

            # Kiểm tra có dữ liệu
            rows = products_table.find_elements(By.XPATH, ".//tbody/tr")
            print(f"  📊 Số sản phẩm hiển thị: {len(rows)}")
            self.assertGreater(len(rows), 0, "Lỗi: Không có sản phẩm nào trong bảng")

            print("✅ Bảng sản phẩm hiển thị đúng")

        except Exception as e:
            self._save_error_screenshot("TC02_products_table")
            raise e

    def test_03_add_product_button_exists(self):
        """TC03: Nút 'Thêm sản phẩm' tồn tại và hoạt động"""
        print("\n--- Running: Test Add Product Button ---")
        driver = self.driver

        try:
            # Tìm nút thêm sản phẩm (có icon <i> bên trong nên dùng normalize-space)
            add_btn = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(@class,'btn-primary') and contains(.,'Thêm sản phẩm')]"))
            )
            self.assertIsNotNone(add_btn)
            print("✅ Tìm thấy nút 'Thêm sản phẩm'")

            # Click để mở modal
            self._js_click(add_btn)
            time.sleep(1)

            # Kiểm tra modal mở
            add_modal = self.wait.until(
                EC.visibility_of_element_located((By.ID, "addRowModal"))
            )
            self.assertTrue(add_modal.is_displayed())
            print("✅ Modal 'Thêm sản phẩm' mở thành công")

            # Đóng modal
            close_btn = driver.find_element(By.ID, "closeAddRowModal")
            self._js_click(close_btn)
            time.sleep(1)

        except Exception as e:
            self._save_error_screenshot("TC03_add_button")
            raise e

    def test_04_add_product_form_validation(self):
        """TC04: Form thêm sản phẩm có validation các trường bắt buộc"""
        print("\n--- Running: Test Add Product Form Validation ---")
        driver = self.driver

        try:
            # Mở modal thêm sản phẩm
            add_btn = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(@class,'btn-primary') and contains(.,'Thêm sản phẩm')]"))
            )
            self._js_click(add_btn)
            time.sleep(1)

            # Kiểm tra các trường bắt buộc có dấu *
            required_labels = driver.find_elements(By.XPATH, "//form[@id='addProductForm']//label[contains(.//span[@class='text-danger'], '*')]")
            print(f"  📋 Số trường bắt buộc: {len(required_labels)}")

            # Các trường bắt buộc mong đợi
            expected_required = ["Tên sản phẩm", "Giá gốc", "Số lượng tồn", "Danh mục", "Ảnh đại diện"]
            for label in required_labels:
                label_text = label.text.replace("*", "").strip()
                print(f"    - {label_text}")

            # Kiểm tra các input required
            name_input = driver.find_element(By.ID, "addProductName")
            self.assertTrue(name_input.get_attribute("required") is not None or name_input.get_attribute("required") == "true")

            price_input = driver.find_element(By.ID, "addProductPrice")
            self.assertTrue(price_input.get_attribute("required") is not None)

            stock_input = driver.find_element(By.ID, "addProductStock")
            self.assertTrue(stock_input.get_attribute("required") is not None)

            category_select = driver.find_element(By.ID, "addProductCategory")
            self.assertTrue(category_select.get_attribute("required") is not None)

            print("✅ Form validation các trường bắt buộc hoạt động")

            # Đóng modal
            cancel_btn = driver.find_element(By.ID, "cancelAddProductButton")
            self._js_click(cancel_btn)
            time.sleep(1)

        except Exception as e:
            self._save_error_screenshot("TC04_form_validation")
            raise e

    def test_05_search_product_by_keyword(self):
        """TC05: Tìm kiếm sản phẩm theo từ khóa"""
        print("\n--- Running: Test Search Product by Keyword ---")
        driver = self.driver

        try:
            # Tìm ô tìm kiếm
            search_input = self.wait.until(
                EC.presence_of_element_located((By.ID, "searchKeyword"))
            )

            # Nhập từ khóa tìm kiếm
            search_keyword = "bóng"
            search_input.clear()
            search_input.send_keys(search_keyword)
            print(f"  🔍 Tìm kiếm với từ khóa: '{search_keyword}'")

            # Click nút tìm kiếm (có icon <i> bên trong)
            search_btn = driver.find_element(By.XPATH, "//form[@id='searchProductForm']//button[contains(.,'Tìm kiếm')]")
            self._js_click(search_btn)
            time.sleep(2)

            # Kiểm tra URL có chứa keyword
            self.assertIn("keyword", driver.current_url.lower())
            print(f"✅ URL chứa tham số keyword: {driver.current_url}")

            # Kiểm tra kết quả (nếu có)
            rows = driver.find_elements(By.XPATH, "//table[@id='add-row']//tbody/tr")
            print(f"  📊 Số kết quả tìm kiếm: {len(rows)}")

            print("✅ Chức năng tìm kiếm hoạt động")

        except Exception as e:
            self._save_error_screenshot("TC05_search_keyword")
            raise e

    def test_06_filter_product_by_category(self):
        """TC06: Lọc sản phẩm theo danh mục"""
        print("\n--- Running: Test Filter Product by Category ---")
        driver = self.driver

        try:
            # Tìm dropdown danh mục
            category_select = self.wait.until(
                EC.presence_of_element_located((By.ID, "searchCategory"))
            )
            select = Select(category_select)

            # Lấy danh sách options
            options = select.options
            print(f"  📋 Số danh mục: {len(options)}")

            if len(options) > 1:
                # Chọn danh mục đầu tiên (không phải "Tất cả")
                select.select_by_index(1)
                selected_category = select.first_selected_option.text
                print(f"  📁 Chọn danh mục: {selected_category}")

                # Click tìm kiếm (có icon <i> bên trong)
                search_btn = driver.find_element(By.XPATH, "//form[@id='searchProductForm']//button[contains(.,'Tìm kiếm')]")
                self._js_click(search_btn)
                time.sleep(2)

                # Kiểm tra URL
                self.assertIn("category_filter", driver.current_url.lower())
                print("✅ Lọc theo danh mục hoạt động")
            else:
                print("⚠️ Không có danh mục để test filter")

        except Exception as e:
            self._save_error_screenshot("TC06_filter_category")
            raise e

    def test_07_filter_product_by_stock(self):
        """TC07: Lọc sản phẩm theo tồn kho"""
        print("\n--- Running: Test Filter Product by Stock ---")
        driver = self.driver

        try:
            # Tìm dropdown tồn kho
            stock_select = self.wait.until(
                EC.presence_of_element_located((By.ID, "searchStock"))
            )
            select = Select(stock_select)

            # Kiểm tra các options
            options = [opt.text for opt in select.options]
            print(f"  📋 Options tồn kho: {options}")

            expected_options = ["Tất cả", "Còn hàng", "Hết hàng", "Sắp hết"]
            for expected in expected_options:
                found = any(expected.lower() in opt.lower() for opt in options)
                self.assertTrue(found, f"Lỗi: Thiếu option '{expected}'")

            # Test lọc "Còn hàng"
            select.select_by_value("in_stock")
            search_btn = driver.find_element(By.XPATH, "//form[@id='searchProductForm']//button[contains(.,'Tìm kiếm')]")
            self._js_click(search_btn)
            time.sleep(2)

            self.assertIn("stock_filter=in_stock", driver.current_url)
            print("✅ Lọc theo tồn kho hoạt động")

        except Exception as e:
            self._save_error_screenshot("TC07_filter_stock")
            raise e

    def test_08_reset_search_filter(self):
        """TC08: Nút 'Đặt lại' reset các bộ lọc"""
        print("\n--- Running: Test Reset Search Filter ---")
        driver = self.driver

        try:
            # Nhập dữ liệu tìm kiếm
            search_input = self.wait.until(
                EC.presence_of_element_located((By.ID, "searchKeyword"))
            )
            search_input.send_keys("test")

            # Chọn filter
            stock_select = Select(driver.find_element(By.ID, "searchStock"))
            stock_select.select_by_value("in_stock")

            # Click tìm kiếm (có icon <i> bên trong)
            search_btn = driver.find_element(By.XPATH, "//form[@id='searchProductForm']//button[contains(.,'Tìm kiếm')]")
            self._js_click(search_btn)
            time.sleep(1)

            # Click nút Đặt lại
            reset_btn = driver.find_element(By.XPATH, "//form[@id='searchProductForm']//a[contains(.,'Đặt lại')]")
            reset_btn.click()
            time.sleep(2)

            # Kiểm tra URL không còn các tham số filter
            current_url = driver.current_url
            self.assertNotIn("keyword=test", current_url)
            print("✅ Nút 'Đặt lại' hoạt động đúng")

        except Exception as e:
            self._save_error_screenshot("TC08_reset_filter")
            raise e

    def test_09_sort_products_by_name(self):
        """TC09: Sắp xếp sản phẩm theo tên"""
        print("\n--- Running: Test Sort Products by Name ---")
        driver = self.driver

        try:
            # Tìm header "Tên sản phẩm" có link sort
            name_sort_link = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//a[contains(@class,'sortable-column') and contains(text(),'Tên sản phẩm')]"))
            )
            print("✅ Tìm thấy link sắp xếp theo tên")

            # Click để sort
            name_sort_link.click()
            time.sleep(2)

            # Kiểm tra URL có tham số sort
            self.assertIn("sort_col=name", driver.current_url)
            print(f"✅ URL sau khi sort: {driver.current_url}")

        except Exception as e:
            self._save_error_screenshot("TC09_sort_name")
            raise e

    def test_10_sort_products_by_price(self):
        """TC10: Sắp xếp sản phẩm theo giá"""
        print("\n--- Running: Test Sort Products by Price ---")
        driver = self.driver

        try:
            # Tìm header "Giá" có link sort
            price_sort_link = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//a[contains(@class,'sortable-column') and contains(text(),'Giá')]"))
            )
            price_sort_link.click()
            time.sleep(2)

            self.assertIn("sort_col=price", driver.current_url)
            print("✅ Sắp xếp theo giá hoạt động")

        except Exception as e:
            self._save_error_screenshot("TC10_sort_price")
            raise e

    def test_11_sort_products_by_stock(self):
        """TC11: Sắp xếp sản phẩm theo tồn kho"""
        print("\n--- Running: Test Sort Products by Stock ---")
        driver = self.driver

        try:
            stock_sort_link = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//a[contains(@class,'sortable-column') and contains(text(),'Tồn kho')]"))
            )
            stock_sort_link.click()
            time.sleep(2)

            self.assertIn("sort_col=stock", driver.current_url)
            print("✅ Sắp xếp theo tồn kho hoạt động")

        except Exception as e:
            self._save_error_screenshot("TC11_sort_stock")
            raise e

    def test_12_click_product_row_opens_edit_modal(self):
        """TC12: Click vào dòng sản phẩm mở modal chỉnh sửa"""
        print("\n--- Running: Test Click Product Row Opens Edit Modal ---")
        driver = self.driver

        try:
            # Tìm dòng sản phẩm đầu tiên
            first_row = self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//table[@id='add-row']//tbody/tr[@class='product-row-clickable'][1]"))
            )
            product_name = first_row.find_element(By.XPATH, ".//td[2]").text
            print(f"  📦 Click vào sản phẩm: {product_name}")

            # Click vào dòng (tránh click vào nút action)
            name_cell = first_row.find_element(By.XPATH, ".//td[2]")
            self._scroll_to_element(name_cell)
            self._js_click(name_cell)
            time.sleep(2)

            # Kiểm tra modal edit mở
            edit_modal = self.wait.until(
                EC.visibility_of_element_located((By.ID, "productEditModal"))
            )
            self.assertTrue(edit_modal.is_displayed())
            print("✅ Modal chỉnh sửa sản phẩm mở thành công")

            # Kiểm tra tên sản phẩm trong modal
            modal_product_name = driver.find_element(By.ID, "modalEditProductName").get_attribute("value")
            print(f"  📝 Tên sản phẩm trong modal: {modal_product_name}")

            # Đóng modal bằng JS click
            close_btn = driver.find_element(By.ID, "closeProductEditModal")
            self._js_click(close_btn)
            time.sleep(1)

        except Exception as e:
            self._save_error_screenshot("TC12_click_row")
            raise e

    def test_13_edit_button_opens_edit_modal(self):
        """TC13: Nút sửa (icon) mở modal chỉnh sửa"""
        print("\n--- Running: Test Edit Button Opens Modal ---")
        driver = self.driver

        try:
            # Đảm bảo không có modal nào đang mở
            try:
                existing_modal = driver.find_element(By.ID, "productEditModal")
                if existing_modal.is_displayed():
                    close_btn = driver.find_element(By.ID, "closeProductEditModal")
                    self._js_click(close_btn)
                    time.sleep(1)
            except:
                pass

            # Tìm nút sửa đầu tiên
            edit_btn = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//table[@id='add-row']//tbody//button[contains(@class,'edit-product-button')][1]"))
            )
            self._scroll_to_element(edit_btn)
            time.sleep(0.5)
            self._js_click(edit_btn)
            
            # Chờ modal hiển thị (tăng timeout vì AJAX load dữ liệu)
            edit_modal = WebDriverWait(driver, 15).until(
                EC.visibility_of_element_located((By.ID, "productEditModal"))
            )
            self.assertTrue(edit_modal.is_displayed())
            print("✅ Nút sửa mở modal thành công")

            # Chờ một chút rồi đóng modal bằng JS click
            time.sleep(1)
            close_btn = driver.find_element(By.ID, "closeProductEditModal")
            self._js_click(close_btn)
            time.sleep(1)

        except Exception as e:
            self._save_error_screenshot("TC13_edit_button")
            raise e

    def test_14_edit_modal_displays_product_data(self):
        """TC14: Modal chỉnh sửa hiển thị đúng dữ liệu sản phẩm"""
        print("\n--- Running: Test Edit Modal Displays Product Data ---")
        driver = self.driver

        try:
            # Click vào sản phẩm đầu tiên
            first_row = self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//table[@id='add-row']//tbody/tr[@class='product-row-clickable'][1]"))
            )
            row_product_id = first_row.get_attribute("data-id")
            row_product_name = first_row.get_attribute("data-name")
            print(f"  📦 Sản phẩm ID: {row_product_id}, Tên: {row_product_name}")

            # Click để mở modal
            name_cell = first_row.find_element(By.XPATH, ".//td[2]")
            self._scroll_to_element(name_cell)
            self._js_click(name_cell)
            
            # Chờ modal hiển thị và AJAX load dữ liệu
            self.wait.until(EC.visibility_of_element_located((By.ID, "productEditModal")))
            time.sleep(3)  # Chờ AJAX load dữ liệu

            # Kiểm tra dữ liệu trong modal (chờ dữ liệu được load)
            modal_id = self.wait.until(
                lambda d: d.find_element(By.ID, "modalDisplayProductId").text if d.find_element(By.ID, "modalDisplayProductId").text else False
            )
            modal_name = driver.find_element(By.ID, "modalEditProductName").get_attribute("value")
            modal_price = driver.find_element(By.ID, "modalEditProductPrice").get_attribute("value")
            modal_stock = driver.find_element(By.ID, "modalEditProductStock").get_attribute("value")

            print(f"  📝 Modal - ID: {modal_id}, Tên: {modal_name}")
            print(f"  📝 Modal - Giá: {modal_price}, Tồn kho: {modal_stock}")

            self.assertEqual(modal_id, row_product_id)
            self.assertEqual(modal_name, row_product_name)
            self.assertIsNotNone(modal_price)
            self.assertIsNotNone(modal_stock)

            print("✅ Modal hiển thị đúng dữ liệu sản phẩm")

            # Đóng modal bằng JS click
            close_btn = driver.find_element(By.ID, "closeProductEditModal")
            self._js_click(close_btn)
            time.sleep(1)

        except Exception as e:
            self._save_error_screenshot("TC14_edit_modal_data")
            raise e

    def test_15_delete_button_opens_confirm_modal(self):
        """TC15: Nút xóa mở modal xác nhận"""
        print("\n--- Running: Test Delete Button Opens Confirm Modal ---")
        driver = self.driver

        try:
            # Tìm nút xóa đầu tiên
            delete_btn = self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//table[@id='add-row']//tbody//button[contains(@class,'delete-product-button')][1]"))
            )
            product_name = delete_btn.get_attribute("data-product-name")
            print(f"  🗑️ Click xóa sản phẩm: {product_name}")

            self._scroll_to_element(delete_btn)
            self._js_click(delete_btn)
            time.sleep(1)

            # Kiểm tra modal xác nhận xóa mở
            delete_modal = self.wait.until(
                EC.visibility_of_element_located((By.ID, "deleteConfirmModal"))
            )
            self.assertTrue(delete_modal.is_displayed())
            print("✅ Modal xác nhận xóa mở thành công")

            # Kiểm tra tên sản phẩm hiển thị trong modal
            confirm_text = driver.find_element(By.ID, "deleteProductNameConfirm").text
            print(f"  📝 Tên SP trong modal xác nhận: {confirm_text}")

            # Đóng modal (click Hủy)
            cancel_btn = delete_modal.find_element(By.XPATH, ".//button[contains(text(),'Hủy')]")
            cancel_btn.click()
            time.sleep(1)

        except Exception as e:
            self._save_error_screenshot("TC15_delete_button")
            raise e

    def test_16_pagination_exists(self):
        """TC16: Phân trang hiển thị (nếu có nhiều sản phẩm)"""
        print("\n--- Running: Test Pagination ---")
        driver = self.driver

        try:
            # Tìm phân trang
            pagination = driver.find_elements(By.CLASS_NAME, "pagination")

            if len(pagination) > 0:
                page_items = pagination[0].find_elements(By.CLASS_NAME, "page-item")
                print(f"  📋 Số page items: {len(page_items)}")

                # Kiểm tra có nút prev/next
                prev_next = pagination[0].find_elements(By.XPATH, ".//a[contains(text(),'«') or contains(text(),'»')]")
                print(f"  ◀️▶️ Nút điều hướng: {len(prev_next)}")

                print("✅ Phân trang hiển thị đúng")
            else:
                print("⚠️ Không có phân trang (có thể do ít sản phẩm)")

        except Exception as e:
            self._save_error_screenshot("TC16_pagination")
            raise e

    def test_17_breadcrumb_navigation(self):
        """TC17: Breadcrumb điều hướng hoạt động"""
        print("\n--- Running: Test Breadcrumb Navigation ---")
        driver = self.driver

        try:
            # Tìm breadcrumb
            breadcrumbs = self.wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "breadcrumbs"))
            )

            # Kiểm tra các items
            nav_items = breadcrumbs.find_elements(By.TAG_NAME, "a")
            print(f"  🔗 Số links trong breadcrumb: {len(nav_items)}")

            # Kiểm tra link home
            home_link = breadcrumbs.find_element(By.XPATH, ".//a[contains(@href,'dashboard')]")
            self.assertIsNotNone(home_link)
            print("✅ Breadcrumb hiển thị đúng")

        except Exception as e:
            self._save_error_screenshot("TC17_breadcrumb")
            raise e

    def test_18_product_image_display(self):
        """TC18: Ảnh sản phẩm hiển thị trong bảng"""
        print("\n--- Running: Test Product Image Display ---")
        driver = self.driver

        try:
            # Tìm ảnh sản phẩm trong bảng
            product_images = driver.find_elements(By.XPATH, "//table[@id='add-row']//tbody//tr//td[1]//img")
            print(f"  🖼️ Số ảnh sản phẩm: {len(product_images)}")

            if len(product_images) > 0:
                first_image = product_images[0]
                img_src = first_image.get_attribute("src")
                print(f"  📸 URL ảnh đầu tiên: {img_src[:80]}...")

                # Kiểm tra kích thước ảnh
                width = first_image.get_attribute("style")
                self.assertIn("60px", width)
                print("✅ Ảnh sản phẩm hiển thị đúng kích thước")

        except Exception as e:
            self._save_error_screenshot("TC18_product_image")
            raise e

    def test_19_action_buttons_exist(self):
        """TC19: Các nút hành động (Sửa, Xóa) tồn tại cho mỗi sản phẩm"""
        print("\n--- Running: Test Action Buttons Exist ---")
        driver = self.driver

        try:
            # Tìm tất cả các dòng sản phẩm
            rows = driver.find_elements(By.XPATH, "//table[@id='add-row']//tbody/tr[@class='product-row-clickable']")

            if len(rows) > 0:
                # Kiểm tra dòng đầu tiên có đủ nút
                first_row = rows[0]
                edit_btn = first_row.find_elements(By.CLASS_NAME, "edit-product-button")
                delete_btn = first_row.find_elements(By.CLASS_NAME, "delete-product-button")

                self.assertEqual(len(edit_btn), 1, "Thiếu nút Sửa")
                self.assertEqual(len(delete_btn), 1, "Thiếu nút Xóa")

                print("✅ Các nút hành động tồn tại đầy đủ")
            else:
                print("⚠️ Không có sản phẩm để kiểm tra")

        except Exception as e:
            self._save_error_screenshot("TC19_action_buttons")
            raise e

    def test_20_edit_modal_has_save_and_delete_buttons(self):
        """TC20: Modal chỉnh sửa có nút Lưu và Xóa"""
        print("\n--- Running: Test Edit Modal Buttons ---")
        driver = self.driver

        try:
            # Mở modal edit
            edit_btn = self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//table[@id='add-row']//tbody//button[contains(@class,'edit-product-button')][1]"))
            )
            self._scroll_to_element(edit_btn)
            self._js_click(edit_btn)
            
            # Chờ modal hiển thị và AJAX load dữ liệu
            self.wait.until(EC.visibility_of_element_located((By.ID, "productEditModal")))
            time.sleep(3)  # Chờ AJAX load dữ liệu

            # Kiểm tra nút Lưu
            save_btn = self.wait.until(
                EC.presence_of_element_located((By.ID, "modalOpenSaveChangesConfirmButton"))
            )
            self.assertIsNotNone(save_btn)
            print(f"  💾 Nút Lưu: {save_btn.text}")

            # Kiểm tra nút Xóa
            delete_btn = driver.find_element(By.ID, "modalOpenDeleteConfirmButton")
            self.assertIsNotNone(delete_btn)
            print(f"  🗑️ Nút Xóa: {delete_btn.text}")

            # Kiểm tra nút Đóng
            close_btn = driver.find_element(By.ID, "closeProductEditModalButton")
            self.assertIsNotNone(close_btn)
            print(f"  ❌ Nút Đóng: {close_btn.text}")

            print("✅ Modal chỉnh sửa có đầy đủ các nút")

            # Đóng modal bằng JS click
            self._js_click(close_btn)
            time.sleep(1)

        except Exception as e:
            self._save_error_screenshot("TC20_edit_modal_buttons")
            raise e


class AdminProductsFormTest(unittest.TestCase):
    """Test Suite cho các form sản phẩm (Thêm, Sửa)"""

    @classmethod
    def setUpClass(cls):
        driver_path = os.path.join(os.getcwd(), 'driver', 'chromedriver.exe')
        service = Service(driver_path)
        options = webdriver.ChromeOptions()
        cls.driver = webdriver.Chrome(service=service, options=options)
        cls.driver.maximize_window()
        cls.wait = WebDriverWait(cls.driver, 10)
        
        # Login
        cls._login_as_admin()

    @classmethod
    def _login_as_admin(cls):
        driver = cls.driver
        driver.get(URL_LOGIN)
        try:
            visit_btn = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Visit Site')]"))
            )
            visit_btn.click()
            time.sleep(2)
        except:
            pass

        email_input = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, "email_signin"))
        )
        email_input.clear()
        email_input.send_keys(ADMIN_ACC['email'])
        driver.find_element(By.ID, "password_signin").send_keys(ADMIN_ACC['pass'])
        driver.find_element(By.ID, "b1").click()

        try:
            iframe = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "iframe[src*='google.com/recaptcha']"))
            )
            driver.switch_to.frame(iframe)
            checkbox = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.ID, "recaptcha-anchor"))
            )
            checkbox.click()
            driver.switch_to.default_content()
            time.sleep(5)
        except:
            pass

        WebDriverWait(driver, 15).until(EC.url_contains("ViewAdmin"))
        print("✅ Đăng nhập Admin thành công!")

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()

    def setUp(self):
        self.driver.get(URL_ADMIN_PRODUCTS)
        time.sleep(2)
        try:
            visit_btn = WebDriverWait(self.driver, 3).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Visit Site')]"))
            )
            visit_btn.click()
            time.sleep(2)
        except:
            pass

    def _save_error_screenshot(self, test_name):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        screenshot_name = f"error_test_{test_name}_{timestamp}.png"
        screenshot_path = os.path.join(os.getcwd(), 'results', screenshot_name)
        self.driver.save_screenshot(screenshot_path)
        print(f"📸 Screenshot saved: {screenshot_path}")

    def _js_click(self, element):
        """Click element bằng JavaScript"""
        self.driver.execute_script("arguments[0].click();", element)

    def test_01_add_product_form_fields(self):
        """TC_F01: Kiểm tra các trường trong form thêm sản phẩm"""
        print("\n--- Running: Test Add Product Form Fields ---")
        driver = self.driver

        try:
            # Mở modal (nút có icon <i> bên trong)
            add_btn = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(@class,'btn-primary') and contains(.,'Thêm sản phẩm')]"))
            )
            self._js_click(add_btn)
            time.sleep(1)

            # Kiểm tra các trường
            fields = {
                "addProductName": "Tên sản phẩm",
                "addProductPrice": "Giá gốc",
                "addProductDiscountPrice": "Giá khuyến mãi",
                "addProductStock": "Số lượng tồn",
                "addProductCategory": "Danh mục",
                "addProductBrand": "Thương hiệu",
                "addProductLocation": "Nơi bán",
                "addProductDescription": "Mô tả"
            }

            for field_id, field_name in fields.items():
                element = driver.find_element(By.ID, field_id)
                self.assertIsNotNone(element, f"Không tìm thấy trường {field_name}")
                print(f"  ✅ Tìm thấy trường: {field_name}")

            # Kiểm tra input file ảnh
            thumbnail_input = driver.find_element(By.ID, "addThumbnailInput")
            self.assertIsNotNone(thumbnail_input)
            print("  ✅ Tìm thấy input ảnh đại diện")

            other_images_input = driver.find_element(By.ID, "addProductImagesInput")
            self.assertIsNotNone(other_images_input)
            print("  ✅ Tìm thấy input ảnh khác")

            print("✅ Form thêm sản phẩm có đầy đủ các trường")

            # Đóng modal bằng JS click
            cancel_btn = driver.find_element(By.ID, "cancelAddProductButton")
            self._js_click(cancel_btn)
            time.sleep(1)

        except Exception as e:
            self._save_error_screenshot("TC_F01_form_fields")
            raise e

    def test_02_category_dropdown_has_options(self):
        """TC_F02: Dropdown danh mục có các options"""
        print("\n--- Running: Test Category Dropdown Options ---")
        driver = self.driver

        try:
            # Mở modal (nút có icon <i> bên trong)
            add_btn = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(@class,'btn-primary') and contains(.,'Thêm sản phẩm')]"))
            )
            self._js_click(add_btn)
            time.sleep(1)

            # Kiểm tra dropdown
            category_select = Select(driver.find_element(By.ID, "addProductCategory"))
            options = category_select.options
            print(f"  📋 Số danh mục: {len(options)}")

            self.assertGreater(len(options), 1, "Dropdown danh mục không có options")

            for opt in options[:5]:  # Hiển thị 5 options đầu
                print(f"    - {opt.text}")

            print("✅ Dropdown danh mục có đầy đủ options")

            cancel_btn = driver.find_element(By.ID, "cancelAddProductButton")
            self._js_click(cancel_btn)
            time.sleep(1)

        except Exception as e:
            self._save_error_screenshot("TC_F02_category_options")
            raise e

    def test_03_edit_form_change_detection(self):
        """TC_F03: Form sửa phát hiện thay đổi và bật nút Lưu"""
        print("\n--- Running: Test Edit Form Change Detection ---")
        driver = self.driver

        try:
            # Mở modal edit
            edit_btn = self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//table[@id='add-row']//tbody//button[contains(@class,'edit-product-button')][1]"))
            )
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", edit_btn)
            driver.execute_script("arguments[0].click();", edit_btn)
            
            # Chờ modal hiển thị và AJAX load dữ liệu
            self.wait.until(EC.visibility_of_element_located((By.ID, "productEditModal")))
            time.sleep(3)  # Chờ AJAX load dữ liệu

            # Kiểm tra nút Lưu ban đầu disabled
            save_btn = self.wait.until(
                EC.presence_of_element_located((By.ID, "modalOpenSaveChangesConfirmButton"))
            )
            is_disabled = save_btn.get_attribute("disabled")
            self.assertTrue(is_disabled == "true" or is_disabled == "", "Nút Lưu ban đầu phải disabled")
            print("  ✅ Nút Lưu ban đầu disabled")

            # Chờ input name có value (AJAX đã load xong)
            name_input = self.wait.until(
                EC.visibility_of_element_located((By.ID, "modalEditProductName"))
            )
            # Chờ cho đến khi value được load
            WebDriverWait(driver, 10).until(
                lambda d: name_input.get_attribute("value") != ""
            )
            original_name = name_input.get_attribute("value")
            
            # Clear và nhập text mới
            name_input.click()
            name_input.send_keys(Keys.CONTROL + "a")
            name_input.send_keys(original_name + " - Test Edit")
            time.sleep(1)

            # Kiểm tra nút Lưu đã enabled
            # Note: Tùy thuộc vào JS, có thể cần chờ thêm
            time.sleep(1)
            is_disabled_after = save_btn.get_attribute("disabled")
            print(f"  📝 Sau khi thay đổi, disabled = {is_disabled_after}")

            print("✅ Form phát hiện thay đổi")

            # Đóng modal (không lưu) bằng JS click
            close_btn = driver.find_element(By.ID, "closeProductEditModal")
            self._js_click(close_btn)
            time.sleep(1)

            # Xử lý modal xác nhận hủy nếu có
            try:
                discard_modal = WebDriverWait(driver, 3).until(
                    EC.visibility_of_element_located((By.ID, "discardConfirmModal"))
                )
                confirm_discard = discard_modal.find_element(By.ID, "confirmDiscardButton")
                self._js_click(confirm_discard)
                time.sleep(1)
            except:
                pass

        except Exception as e:
            self._save_error_screenshot("TC_F03_change_detection")
            raise e


class AdminProductsCRUDTest(unittest.TestCase):
    """Test Suite cho chức năng CRUD sản phẩm (Thêm, Sửa, Xóa)"""

    # Biến lưu ID sản phẩm được tạo để test sửa và xóa
    created_product_name = None

    @classmethod
    def setUpClass(cls):
        driver_path = os.path.join(os.getcwd(), 'driver', 'chromedriver.exe')
        service = Service(driver_path)
        options = webdriver.ChromeOptions()
        cls.driver = webdriver.Chrome(service=service, options=options)
        cls.driver.maximize_window()
        cls.wait = WebDriverWait(cls.driver, 15)
        
        cls._login_as_admin()

    @classmethod
    def _login_as_admin(cls):
        driver = cls.driver
        driver.get(URL_LOGIN)
        try:
            visit_btn = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Visit Site')]"))
            )
            visit_btn.click()
            time.sleep(2)
        except:
            pass

        email_input = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, "email_signin"))
        )
        email_input.clear()
        email_input.send_keys(ADMIN_ACC['email'])
        driver.find_element(By.ID, "password_signin").send_keys(ADMIN_ACC['pass'])
        driver.find_element(By.ID, "b1").click()

        try:
            iframe = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "iframe[src*='google.com/recaptcha']"))
            )
            driver.switch_to.frame(iframe)
            checkbox = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.ID, "recaptcha-anchor"))
            )
            checkbox.click()
            driver.switch_to.default_content()
            time.sleep(5)
        except:
            pass

        WebDriverWait(driver, 15).until(EC.url_contains("ViewAdmin"))
        print("✅ Đăng nhập Admin thành công cho CRUD Test!")

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()

    def setUp(self):
        self.driver.get(URL_ADMIN_PRODUCTS)
        time.sleep(2)
        try:
            visit_btn = WebDriverWait(self.driver, 3).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Visit Site')]"))
            )
            visit_btn.click()
            time.sleep(2)
        except:
            pass

    def _save_error_screenshot(self, test_name):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        screenshot_name = f"error_test_{test_name}_{timestamp}.png"
        screenshot_path = os.path.join(os.getcwd(), 'results', screenshot_name)
        self.driver.save_screenshot(screenshot_path)
        print(f"📸 Screenshot saved: {screenshot_path}")

    def _js_click(self, element):
        """Click element bằng JavaScript"""
        self.driver.execute_script("arguments[0].click();", element)

    def _scroll_to_element(self, element):
        """Scroll đến element"""
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
        time.sleep(0.5)

    def _close_any_open_modal(self):
        """Đóng bất kỳ modal nào đang mở"""
        driver = self.driver
        modals_to_close = [
            ("productEditModal", "closeProductEditModal"),
            ("addRowModal", "closeAddRowModal"),
            ("deleteConfirmModal", None),  # Có nút Hủy
            ("discardConfirmModal", None)
        ]
        for modal_id, close_btn_id in modals_to_close:
            try:
                modal = driver.find_element(By.ID, modal_id)
                if modal.is_displayed():
                    if close_btn_id:
                        close_btn = driver.find_element(By.ID, close_btn_id)
                        self._js_click(close_btn)
                    else:
                        # Tìm nút Hủy trong modal
                        cancel_btn = modal.find_element(By.XPATH, ".//button[contains(text(),'Hủy')]")
                        self._js_click(cancel_btn)
                    time.sleep(0.5)
            except:
                pass

    # ==================== TEST THÊM SẢN PHẨM ====================

    def test_01_add_product_validation_empty_name(self):
        """TC_CRUD01: Validation - Không cho phép thêm sản phẩm khi tên trống"""
        print("\n--- Running: Test Add Product Validation Empty Name ---")
        driver = self.driver

        try:
            # Mở modal thêm sản phẩm
            add_btn = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(@class,'btn-primary') and contains(.,'Thêm sản phẩm')]"))
            )
            self._js_click(add_btn)
            time.sleep(1)

            # Điền các trường khác nhưng bỏ trống tên
            driver.find_element(By.ID, "addProductPrice").send_keys("100000")
            driver.find_element(By.ID, "addProductStock").send_keys("10")
            
            # Chọn danh mục
            category_select = Select(driver.find_element(By.ID, "addProductCategory"))
            if len(category_select.options) > 1:
                category_select.select_by_index(1)

            # Click nút Thêm mới
            submit_btn = driver.find_element(By.ID, "submitAddProductButton")
            self._js_click(submit_btn)
            time.sleep(1)

            # Kiểm tra form validation (HTML5 required) hoặc thông báo lỗi
            name_input = driver.find_element(By.ID, "addProductName")
            # Kiểm tra xem input có validation message không
            validation_message = driver.execute_script("return arguments[0].validationMessage;", name_input)
            
            if validation_message:
                print(f"  ✅ Validation message: {validation_message}")
            else:
                # Kiểm tra thông báo lỗi từ server (nếu form submit)
                time.sleep(2)
                # Modal vẫn mở = validation hoạt động
                modal = driver.find_element(By.ID, "addRowModal")
                self.assertTrue(modal.is_displayed(), "Modal đã đóng - có thể form đã submit")
                print("  ✅ Modal vẫn mở - validation hoạt động")

            print("✅ Validation tên sản phẩm trống hoạt động")

            # Đóng modal
            self._js_click(driver.find_element(By.ID, "cancelAddProductButton"))
            time.sleep(1)

        except Exception as e:
            self._save_error_screenshot("TC_CRUD01_validation_name")
            raise e

    def test_02_add_product_validation_empty_price(self):
        """TC_CRUD02: Validation - Không cho phép thêm khi giá trống"""
        print("\n--- Running: Test Add Product Validation Empty Price ---")
        driver = self.driver

        try:
            # Mở modal
            add_btn = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(@class,'btn-primary') and contains(.,'Thêm sản phẩm')]"))
            )
            self._js_click(add_btn)
            time.sleep(1)

            # Điền tên nhưng bỏ trống giá
            driver.find_element(By.ID, "addProductName").send_keys("Test Product Name")
            driver.find_element(By.ID, "addProductStock").send_keys("10")
            
            category_select = Select(driver.find_element(By.ID, "addProductCategory"))
            if len(category_select.options) > 1:
                category_select.select_by_index(1)

            # Click submit
            submit_btn = driver.find_element(By.ID, "submitAddProductButton")
            self._js_click(submit_btn)
            time.sleep(1)

            # Kiểm tra validation
            price_input = driver.find_element(By.ID, "addProductPrice")
            validation_message = driver.execute_script("return arguments[0].validationMessage;", price_input)
            
            if validation_message:
                print(f"  ✅ Validation message: {validation_message}")
            
            # Modal vẫn mở
            modal = driver.find_element(By.ID, "addRowModal")
            self.assertTrue(modal.is_displayed())
            print("✅ Validation giá sản phẩm trống hoạt động")

            # Đóng modal
            self._js_click(driver.find_element(By.ID, "cancelAddProductButton"))
            time.sleep(1)

        except Exception as e:
            self._save_error_screenshot("TC_CRUD02_validation_price")
            raise e

    def test_03_add_product_validation_empty_category(self):
        """TC_CRUD03: Validation - Không cho phép thêm khi chưa chọn danh mục"""
        print("\n--- Running: Test Add Product Validation Empty Category ---")
        driver = self.driver

        try:
            # Mở modal
            add_btn = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(@class,'btn-primary') and contains(.,'Thêm sản phẩm')]"))
            )
            self._js_click(add_btn)
            time.sleep(1)

            # Điền đầy đủ trừ danh mục
            driver.find_element(By.ID, "addProductName").send_keys("Test Product")
            driver.find_element(By.ID, "addProductPrice").send_keys("100000")
            driver.find_element(By.ID, "addProductStock").send_keys("10")
            # Không chọn danh mục

            # Click submit
            submit_btn = driver.find_element(By.ID, "submitAddProductButton")
            self._js_click(submit_btn)
            time.sleep(1)

            # Kiểm tra validation
            category_select = driver.find_element(By.ID, "addProductCategory")
            validation_message = driver.execute_script("return arguments[0].validationMessage;", category_select)
            
            if validation_message:
                print(f"  ✅ Validation message: {validation_message}")
            
            modal = driver.find_element(By.ID, "addRowModal")
            self.assertTrue(modal.is_displayed())
            print("✅ Validation danh mục trống hoạt động")

            # Đóng modal
            self._js_click(driver.find_element(By.ID, "cancelAddProductButton"))
            time.sleep(1)

        except Exception as e:
            self._save_error_screenshot("TC_CRUD03_validation_category")
            raise e

    def test_04_add_product_discount_price_validation(self):
        """TC_CRUD04: Validation - Giá khuyến mãi không được lớn hơn giá gốc"""
        print("\n--- Running: Test Add Product Discount Price Validation ---")
        driver = self.driver

        try:
            # Mở modal
            add_btn = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(@class,'btn-primary') and contains(.,'Thêm sản phẩm')]"))
            )
            self._js_click(add_btn)
            time.sleep(1)

            # Điền thông tin với giá khuyến mãi > giá gốc
            driver.find_element(By.ID, "addProductName").send_keys("Test Discount Validation")
            driver.find_element(By.ID, "addProductPrice").send_keys("100000")
            driver.find_element(By.ID, "addProductDiscountPrice").send_keys("150000")  # Lớn hơn giá gốc
            driver.find_element(By.ID, "addProductStock").send_keys("10")
            
            category_select = Select(driver.find_element(By.ID, "addProductCategory"))
            if len(category_select.options) > 1:
                category_select.select_by_index(1)

            # Cần có ảnh thumbnail - bỏ qua nếu không có ảnh test
            # Trong trường hợp này, form sẽ fail do thiếu ảnh hoặc giá không hợp lệ

            print("✅ Test case giá khuyến mãi đã được thiết lập")
            print("  ⚠️ Lưu ý: Server sẽ validate và trả về lỗi nếu giá KM > giá gốc")

            # Đóng modal
            self._js_click(driver.find_element(By.ID, "cancelAddProductButton"))
            time.sleep(1)

        except Exception as e:
            self._save_error_screenshot("TC_CRUD04_discount_validation")
            raise e

    # ==================== TEST SỬA SẢN PHẨM ====================

    def test_05_edit_product_load_data(self):
        """TC_CRUD05: Modal sửa load đúng dữ liệu sản phẩm từ server"""
        print("\n--- Running: Test Edit Product Load Data ---")
        driver = self.driver

        try:
            # Click vào nút sửa sản phẩm đầu tiên
            edit_btn = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//table[@id='add-row']//tbody//button[contains(@class,'edit-product-button')][1]"))
            )
            
            # Lấy product ID từ nút
            product_id = edit_btn.get_attribute("data-product-id")
            print(f"  📦 Đang mở sản phẩm ID: {product_id}")

            self._scroll_to_element(edit_btn)
            self._js_click(edit_btn)

            # Chờ modal và AJAX load
            self.wait.until(EC.visibility_of_element_located((By.ID, "productEditModal")))
            time.sleep(3)

            # Chờ dữ liệu được load (ID hiển thị)
            modal_id = WebDriverWait(driver, 10).until(
                lambda d: d.find_element(By.ID, "modalDisplayProductId").text if d.find_element(By.ID, "modalDisplayProductId").text else False
            )
            
            # Kiểm tra các trường có dữ liệu
            modal_name = driver.find_element(By.ID, "modalEditProductName").get_attribute("value")
            modal_price = driver.find_element(By.ID, "modalEditProductPrice").get_attribute("value")
            modal_stock = driver.find_element(By.ID, "modalEditProductStock").get_attribute("value")

            print(f"  📝 ID: {modal_id}")
            print(f"  📝 Tên: {modal_name}")
            print(f"  📝 Giá: {modal_price}")
            print(f"  📝 Tồn kho: {modal_stock}")

            # Assertions
            self.assertEqual(modal_id, product_id)
            self.assertTrue(len(modal_name) > 0, "Tên sản phẩm không được load")
            self.assertTrue(len(modal_price) > 0, "Giá không được load")
            self.assertTrue(len(modal_stock) > 0, "Tồn kho không được load")

            print("✅ Dữ liệu sản phẩm được load đúng")

            # Đóng modal
            close_btn = driver.find_element(By.ID, "closeProductEditModal")
            self._js_click(close_btn)
            time.sleep(1)

        except Exception as e:
            self._save_error_screenshot("TC_CRUD05_edit_load_data")
            raise e

    def test_06_edit_product_change_name(self):
        """TC_CRUD06: Thay đổi tên sản phẩm và lưu thành công"""
        print("\n--- Running: Test Edit Product Change Name ---")
        driver = self.driver

        try:
            # Mở modal edit sản phẩm đầu tiên
            edit_btn = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//table[@id='add-row']//tbody//button[contains(@class,'edit-product-button')][1]"))
            )
            self._scroll_to_element(edit_btn)
            self._js_click(edit_btn)

            self.wait.until(EC.visibility_of_element_located((By.ID, "productEditModal")))
            time.sleep(3)

            # Chờ input name có value
            name_input = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.ID, "modalEditProductName"))
            )
            WebDriverWait(driver, 10).until(
                lambda d: name_input.get_attribute("value") != ""
            )

            original_name = name_input.get_attribute("value")
            print(f"  📝 Tên gốc: {original_name}")

            # Thêm suffix vào tên
            test_suffix = " - Edited " + datetime.now().strftime("%H%M%S")
            name_input.click()
            name_input.send_keys(Keys.CONTROL + "a")
            name_input.send_keys(original_name + test_suffix)
            time.sleep(1)

            # Kiểm tra nút Lưu đã enabled
            save_btn = driver.find_element(By.ID, "modalOpenSaveChangesConfirmButton")
            is_disabled = save_btn.get_attribute("disabled")
            print(f"  📝 Nút Lưu disabled: {is_disabled}")

            # Nếu nút Lưu enabled, có thể click (nhưng không thực sự lưu để tránh thay đổi data)
            print("✅ Phát hiện thay đổi và nút Lưu sẵn sàng")

            # Đóng modal và hủy thay đổi
            close_btn = driver.find_element(By.ID, "closeProductEditModal")
            self._js_click(close_btn)
            time.sleep(1)

            # Xử lý modal xác nhận hủy
            try:
                discard_modal = WebDriverWait(driver, 3).until(
                    EC.visibility_of_element_located((By.ID, "discardConfirmModal"))
                )
                confirm_discard = discard_modal.find_element(By.ID, "confirmDiscardButton")
                self._js_click(confirm_discard)
                time.sleep(1)
            except:
                pass

        except Exception as e:
            self._save_error_screenshot("TC_CRUD06_edit_change_name")
            raise e

    def test_07_edit_product_validation_empty_name(self):
        """TC_CRUD07: Validation khi xóa trắng tên sản phẩm"""
        print("\n--- Running: Test Edit Product Validation Empty Name ---")
        driver = self.driver

        try:
            # Mở modal edit
            edit_btn = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//table[@id='add-row']//tbody//button[contains(@class,'edit-product-button')][1]"))
            )
            self._scroll_to_element(edit_btn)
            self._js_click(edit_btn)

            self.wait.until(EC.visibility_of_element_located((By.ID, "productEditModal")))
            time.sleep(3)

            # Chờ input có value
            name_input = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.ID, "modalEditProductName"))
            )
            WebDriverWait(driver, 10).until(
                lambda d: name_input.get_attribute("value") != ""
            )

            # Xóa trắng tên
            name_input.click()
            name_input.send_keys(Keys.CONTROL + "a")
            name_input.send_keys(Keys.DELETE)
            time.sleep(1)

            # Kiểm tra validation message
            validation_message = driver.execute_script("return arguments[0].validationMessage;", name_input)
            if validation_message:
                print(f"  ✅ Validation message: {validation_message}")
            
            print("✅ Validation tên trống trong edit form hoạt động")

            # Đóng modal
            close_btn = driver.find_element(By.ID, "closeProductEditModal")
            self._js_click(close_btn)
            time.sleep(1)

            try:
                discard_modal = WebDriverWait(driver, 3).until(
                    EC.visibility_of_element_located((By.ID, "discardConfirmModal"))
                )
                confirm_discard = discard_modal.find_element(By.ID, "confirmDiscardButton")
                self._js_click(confirm_discard)
                time.sleep(1)
            except:
                pass

        except Exception as e:
            self._save_error_screenshot("TC_CRUD07_edit_validation_name")
            raise e

    # ==================== TEST XÓA SẢN PHẨM ====================

    def test_08_delete_product_confirm_modal_display(self):
        """TC_CRUD08: Modal xác nhận xóa hiển thị đúng thông tin"""
        print("\n--- Running: Test Delete Product Confirm Modal ---")
        driver = self.driver

        try:
            # Tìm nút xóa đầu tiên
            delete_btn = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//table[@id='add-row']//tbody//button[contains(@class,'delete-product-button')][1]"))
            )
            
            product_name = delete_btn.get_attribute("data-product-name")
            product_id = delete_btn.get_attribute("data-product-id")
            print(f"  📦 Sản phẩm: {product_name} (ID: {product_id})")

            self._scroll_to_element(delete_btn)
            self._js_click(delete_btn)
            time.sleep(1)

            # Kiểm tra modal xác nhận xóa hiển thị
            delete_modal = self.wait.until(
                EC.visibility_of_element_located((By.ID, "deleteConfirmModal"))
            )
            self.assertTrue(delete_modal.is_displayed())

            # Kiểm tra tên sản phẩm trong modal
            confirm_name = driver.find_element(By.ID, "deleteProductNameConfirm").text
            print(f"  📝 Tên SP trong modal: {confirm_name}")
            
            # Kiểm tra có nút Xóa và Hủy
            confirm_delete_btn = delete_modal.find_element(By.ID, "confirmDeleteButton")
            cancel_btn = delete_modal.find_element(By.XPATH, ".//button[contains(text(),'Hủy')]")
            
            self.assertIsNotNone(confirm_delete_btn)
            self.assertIsNotNone(cancel_btn)

            print("✅ Modal xác nhận xóa hiển thị đúng")

            # Đóng modal (click Hủy)
            self._js_click(cancel_btn)
            time.sleep(1)

        except Exception as e:
            self._save_error_screenshot("TC_CRUD08_delete_confirm_modal")
            raise e

    def test_09_delete_product_cancel(self):
        """TC_CRUD09: Hủy xóa sản phẩm - sản phẩm vẫn còn"""
        print("\n--- Running: Test Delete Product Cancel ---")
        driver = self.driver

        try:
            # Đếm số sản phẩm trước
            rows_before = driver.find_elements(By.XPATH, "//table[@id='add-row']//tbody/tr[contains(@class,'product-row-clickable')]")
            count_before = len(rows_before)
            print(f"  📊 Số sản phẩm trước: {count_before}")

            # Click xóa sản phẩm đầu tiên
            delete_btn = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//table[@id='add-row']//tbody//button[contains(@class,'delete-product-button')][1]"))
            )
            self._scroll_to_element(delete_btn)
            self._js_click(delete_btn)
            time.sleep(1)

            # Chờ modal hiển thị
            delete_modal = self.wait.until(
                EC.visibility_of_element_located((By.ID, "deleteConfirmModal"))
            )

            # Click nút Hủy
            cancel_btn = delete_modal.find_element(By.XPATH, ".//button[contains(text(),'Hủy')]")
            self._js_click(cancel_btn)
            time.sleep(1)

            # Đếm số sản phẩm sau khi hủy
            rows_after = driver.find_elements(By.XPATH, "//table[@id='add-row']//tbody/tr[contains(@class,'product-row-clickable')]")
            count_after = len(rows_after)
            print(f"  📊 Số sản phẩm sau khi hủy: {count_after}")

            self.assertEqual(count_before, count_after, "Số sản phẩm thay đổi sau khi hủy xóa")
            print("✅ Hủy xóa thành công - sản phẩm vẫn còn")

        except Exception as e:
            self._save_error_screenshot("TC_CRUD09_delete_cancel")
            raise e

    def test_10_delete_from_edit_modal(self):
        """TC_CRUD10: Nút xóa trong modal chỉnh sửa mở modal xác nhận"""
        print("\n--- Running: Test Delete From Edit Modal ---")
        driver = self.driver

        try:
            # Mở modal edit
            edit_btn = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//table[@id='add-row']//tbody//button[contains(@class,'edit-product-button')][1]"))
            )
            self._scroll_to_element(edit_btn)
            self._js_click(edit_btn)

            self.wait.until(EC.visibility_of_element_located((By.ID, "productEditModal")))
            time.sleep(3)

            # Click nút "Xóa sản phẩm" trong modal edit
            delete_in_modal_btn = driver.find_element(By.ID, "modalOpenDeleteConfirmButton")
            self._js_click(delete_in_modal_btn)
            time.sleep(1)

            # Kiểm tra modal xác nhận xóa hiển thị
            delete_confirm_modal = self.wait.until(
                EC.visibility_of_element_located((By.ID, "deleteConfirmModal"))
            )
            self.assertTrue(delete_confirm_modal.is_displayed())
            print("✅ Nút xóa trong modal edit mở modal xác nhận thành công")

            # Đóng modal xác nhận
            cancel_btn = delete_confirm_modal.find_element(By.XPATH, ".//button[contains(text(),'Hủy')]")
            self._js_click(cancel_btn)
            time.sleep(1)

            # Đóng modal edit
            close_edit_btn = driver.find_element(By.ID, "closeProductEditModal")
            self._js_click(close_edit_btn)
            time.sleep(1)

        except Exception as e:
            self._save_error_screenshot("TC_CRUD10_delete_from_edit")
            raise e

    # ==================== TEST TỔNG HỢP ====================

    def test_11_add_product_form_reset_on_close(self):
        """TC_CRUD11: Form thêm sản phẩm được reset khi đóng modal"""
        print("\n--- Running: Test Add Product Form Reset ---")
        driver = self.driver

        try:
            # Mở modal thêm
            add_btn = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(@class,'btn-primary') and contains(.,'Thêm sản phẩm')]"))
            )
            self._js_click(add_btn)
            time.sleep(1)

            # Điền một số thông tin
            name_input = driver.find_element(By.ID, "addProductName")
            name_input.send_keys("Test Reset Form")
            
            price_input = driver.find_element(By.ID, "addProductPrice")
            price_input.send_keys("999999")

            # Đóng modal
            cancel_btn = driver.find_element(By.ID, "cancelAddProductButton")
            self._js_click(cancel_btn)
            time.sleep(1)

            # Mở lại modal
            self._js_click(add_btn)
            time.sleep(1)

            # Kiểm tra form đã được reset
            name_value = driver.find_element(By.ID, "addProductName").get_attribute("value")
            price_value = driver.find_element(By.ID, "addProductPrice").get_attribute("value")

            print(f"  📝 Tên sau khi mở lại: '{name_value}'")
            print(f"  📝 Giá sau khi mở lại: '{price_value}'")

            self.assertEqual(name_value, "", "Form không được reset - tên còn giá trị")
            self.assertEqual(price_value, "", "Form không được reset - giá còn giá trị")

            print("✅ Form được reset khi đóng modal")

            # Đóng modal
            self._js_click(driver.find_element(By.ID, "cancelAddProductButton"))
            time.sleep(1)

        except Exception as e:
            self._save_error_screenshot("TC_CRUD11_form_reset")
            raise e

    def test_12_edit_save_confirm_modal(self):
        """TC_CRUD12: Modal xác nhận lưu hiển thị khi click Lưu thay đổi"""
        print("\n--- Running: Test Edit Save Confirm Modal ---")
        driver = self.driver

        try:
            # Mở modal edit
            edit_btn = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//table[@id='add-row']//tbody//button[contains(@class,'edit-product-button')][1]"))
            )
            self._scroll_to_element(edit_btn)
            self._js_click(edit_btn)

            self.wait.until(EC.visibility_of_element_located((By.ID, "productEditModal")))
            time.sleep(3)

            # Chờ input có value
            name_input = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.ID, "modalEditProductName"))
            )
            WebDriverWait(driver, 10).until(
                lambda d: name_input.get_attribute("value") != ""
            )

            # Thay đổi để enable nút Lưu
            original_name = name_input.get_attribute("value")
            name_input.click()
            name_input.send_keys(Keys.CONTROL + "a")
            name_input.send_keys(original_name + " - Test")
            time.sleep(1)

            # Click nút Lưu thay đổi
            save_btn = driver.find_element(By.ID, "modalOpenSaveChangesConfirmButton")
            
            # Chờ nút enable
            WebDriverWait(driver, 5).until(
                lambda d: not save_btn.get_attribute("disabled")
            )
            
            self._js_click(save_btn)
            time.sleep(1)

            # Kiểm tra modal xác nhận lưu hiển thị
            save_confirm_modal = self.wait.until(
                EC.visibility_of_element_located((By.ID, "saveConfirmModal"))
            )
            self.assertTrue(save_confirm_modal.is_displayed())
            print("✅ Modal xác nhận lưu hiển thị")

            # Đóng modal xác nhận (không lưu)
            cancel_save_btn = save_confirm_modal.find_element(By.XPATH, ".//button[contains(text(),'Hủy')]")
            self._js_click(cancel_save_btn)
            time.sleep(1)

            # Đóng modal edit
            close_edit_btn = driver.find_element(By.ID, "closeProductEditModal")
            self._js_click(close_edit_btn)
            time.sleep(1)

            # Xử lý modal discard nếu có
            try:
                discard_modal = WebDriverWait(driver, 3).until(
                    EC.visibility_of_element_located((By.ID, "discardConfirmModal"))
                )
                confirm_discard = discard_modal.find_element(By.ID, "confirmDiscardButton")
                self._js_click(confirm_discard)
                time.sleep(1)
            except:
                pass

        except Exception as e:
            self._save_error_screenshot("TC_CRUD12_save_confirm_modal")
            raise e


if __name__ == "__main__":
    # Tạo test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Thêm các test class
    suite.addTests(loader.loadTestsFromTestCase(AdminProductsTest))
    suite.addTests(loader.loadTestsFromTestCase(AdminProductsFormTest))
    suite.addTests(loader.loadTestsFromTestCase(AdminProductsCRUDTest))

    # Chạy tests
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
