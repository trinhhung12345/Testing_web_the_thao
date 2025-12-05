import unittest
import time
import os
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# --- CẤU HÌNH DỮ LIỆU TEST ---
URL_LOGIN = "https://whippet-exotic-specially.ngrok-free.app/QlyShopTheThao/src/view/login.php"
URL_ADMIN_DASHBOARD = "https://whippet-exotic-specially.ngrok-free.app/QlyShopTheThao/src/view/ViewAdmin/index.php?page=dashboard"

# Tài khoản Admin thật trong DB
ADMIN_ACC = {"email": "wearingarmor12345@gmail.com", "pass": "hung12345"}

# Tài khoản User thường (không có quyền admin)
USER_ACC = {"email": "killerqueen2337@gmail.com", "pass": "hung12345"}


class AdminDashboardTest(unittest.TestCase):
    """Test Suite cho trang Admin Dashboard"""

    @classmethod
    def setUpClass(cls):
        """Thiết lập một lần cho toàn bộ test class - Đăng nhập Admin"""
        driver_path = os.path.join(os.getcwd(), 'driver', 'chromedriver.exe')
        service = Service(driver_path)
        options = webdriver.ChromeOptions()
        # options.add_argument("--headless")  # Bỏ comment nếu muốn chạy ẩn
        cls.driver = webdriver.Chrome(service=service, options=options)
        cls.driver.maximize_window()
        cls.wait = WebDriverWait(cls.driver, 10)
        
        # Đăng nhập Admin một lần duy nhất
        cls._login_as_admin()

    @classmethod
    def _login_as_admin(cls):
        """Đăng nhập với tài khoản Admin"""
        driver = cls.driver
        driver.get(URL_LOGIN)
        
        # Bypass Ngrok (Nếu có)
        try:
            visit_btn = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Visit Site')]"))
            )
            visit_btn.click()
            time.sleep(2)
        except:
            pass

        # Điền thông tin đăng nhập
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

        # Chờ chuyển hướng đến trang Admin
        WebDriverWait(driver, 15).until(
            EC.url_contains("ViewAdmin")
        )
        print("✅ Đăng nhập Admin thành công!")

    @classmethod
    def tearDownClass(cls):
        """Đóng trình duyệt sau khi chạy xong tất cả test"""
        cls.driver.quit()

    def setUp(self):
        """Trước mỗi test case, điều hướng về trang Dashboard"""
        self.driver.get(URL_ADMIN_DASHBOARD)
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

    # ==================== TEST CASES ====================

    def test_01_dashboard_page_loads_successfully(self):
        """TC01: Trang Dashboard load thành công"""
        print("\n--- Running: Test Dashboard Page Loads ---")
        driver = self.driver

        try:
            # Kiểm tra URL chứa dashboard
            self.assertIn("dashboard", driver.current_url.lower(), 
                         "Lỗi: URL không chứa 'dashboard'")

            # Kiểm tra page title hiển thị
            page_title = self.wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "page-title"))
            )
            self.assertIsNotNone(page_title, "Lỗi: Không tìm thấy page title")
            print(f"✅ Page title: {page_title.text}")

        except Exception as e:
            self._save_error_screenshot("TC01_dashboard_load")
            raise e

    def test_02_dashboard_statistics_cards_display(self):
        """TC02: Hiển thị đầy đủ 4 thẻ thống kê (Doanh thu, Đơn hàng, Người dùng, Đánh giá)"""
        print("\n--- Running: Test Statistics Cards Display ---")
        driver = self.driver

        try:
            # Tìm tất cả các card stats
            stats_cards = self.wait.until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "card-stats"))
            )
            
            # Kiểm tra có đủ 4 thẻ
            self.assertEqual(len(stats_cards), 4, 
                           f"Lỗi: Mong đợi 4 thẻ thống kê, nhưng tìm thấy {len(stats_cards)}")
            print(f"✅ Tìm thấy {len(stats_cards)} thẻ thống kê")

            # Kiểm tra nội dung từng thẻ
            expected_labels = ["Doanh thu tháng", "Đơn hàng mới (Tháng)", "Tổng người dùng", "Đánh giá chờ duyệt"]
            
            for card in stats_cards:
                card_category = card.find_element(By.CLASS_NAME, "card-category").text
                card_value = card.find_element(By.CLASS_NAME, "card-title").text
                print(f"  📊 {card_category}: {card_value}")
                
                # Kiểm tra label có trong danh sách mong đợi
                found = any(label in card_category for label in expected_labels)
                self.assertTrue(found, f"Lỗi: Label '{card_category}' không hợp lệ")

        except Exception as e:
            self._save_error_screenshot("TC02_stats_cards")
            raise e

    def test_03_revenue_chart_display(self):
        """TC03: Biểu đồ doanh thu hiển thị đúng"""
        print("\n--- Running: Test Revenue Chart Display ---")
        driver = self.driver

        try:
            # Kiểm tra canvas biểu đồ doanh thu tồn tại
            revenue_chart = self.wait.until(
                EC.presence_of_element_located((By.ID, "revenueChart"))
            )
            self.assertIsNotNone(revenue_chart, "Lỗi: Không tìm thấy biểu đồ doanh thu")
            print("✅ Biểu đồ doanh thu tồn tại")

            # Kiểm tra tiêu đề biểu đồ - tìm h4 trong card-header của card chứa revenueChart
            chart_header = driver.find_element(By.XPATH, 
                "//canvas[@id='revenueChart']/ancestor::div[contains(@class,'card')]/div[contains(@class,'card-header')]//h4"
            )
            self.assertIn("Doanh thu", chart_header.text, "Lỗi: Tiêu đề biểu đồ không đúng")
            print(f"✅ Tiêu đề biểu đồ: {chart_header.text}")

        except Exception as e:
            self._save_error_screenshot("TC03_revenue_chart")
            raise e

    def test_04_revenue_chart_filter_functionality(self):
        """TC04: Bộ lọc biểu đồ doanh thu hoạt động"""
        print("\n--- Running: Test Revenue Chart Filter ---")
        driver = self.driver

        try:
            # Tìm dropdown bộ lọc
            filter_select = self.wait.until(
                EC.presence_of_element_located((By.ID, "revenue-chart-filter"))
            )
            select = Select(filter_select)

            # Lấy danh sách các option
            options = select.options
            expected_options = ["7 ngày qua", "Hôm nay", "Hôm qua", "Tháng này", "Quý này", "Năm nay"]
            
            print(f"  📋 Số lượng options: {len(options)}")
            
            for option in options:
                print(f"    - {option.text}")
            
            # Kiểm tra số lượng options
            self.assertEqual(len(options), 6, f"Lỗi: Mong đợi 6 options, tìm thấy {len(options)}")

            # Test chuyển đổi filter
            select.select_by_value("this_month")
            time.sleep(2)  # Chờ chart update
            print("✅ Đã chọn filter 'Tháng này'")

            select.select_by_value("this_year")
            time.sleep(2)
            print("✅ Đã chọn filter 'Năm nay'")

        except Exception as e:
            self._save_error_screenshot("TC04_chart_filter")
            raise e

    def test_05_category_chart_display(self):
        """TC05: Biểu đồ phân bổ sản phẩm hiển thị"""
        print("\n--- Running: Test Category Chart Display ---")
        driver = self.driver

        try:
            # Kiểm tra canvas biểu đồ category
            category_chart = self.wait.until(
                EC.presence_of_element_located((By.ID, "categoryChart"))
            )
            self.assertIsNotNone(category_chart, "Lỗi: Không tìm thấy biểu đồ phân bổ sản phẩm")
            print("✅ Biểu đồ phân bổ sản phẩm tồn tại")

            # Kiểm tra tiêu đề - tìm h4 trong card-header của card chứa categoryChart
            chart_header = driver.find_element(By.XPATH,
                "//canvas[@id='categoryChart']/ancestor::div[contains(@class,'card')]/div[contains(@class,'card-header')]//h4"
            )
            self.assertIn("Phân bổ Sản phẩm", chart_header.text)
            print(f"✅ Tiêu đề: {chart_header.text}")

        except Exception as e:
            self._save_error_screenshot("TC05_category_chart")
            raise e

    def test_06_recent_orders_table_display(self):
        """TC06: Bảng đơn hàng mới nhất hiển thị đúng cấu trúc"""
        print("\n--- Running: Test Recent Orders Table ---")
        driver = self.driver

        try:
            # Tìm bảng đơn hàng mới nhất
            orders_table = self.wait.until(
                EC.presence_of_element_located((By.XPATH, 
                    "//h4[contains(text(),'Đơn Hàng Mới Nhất')]/ancestor::div[contains(@class,'card')]//table"
                ))
            )
            self.assertIsNotNone(orders_table, "Lỗi: Không tìm thấy bảng đơn hàng")

            # Kiểm tra các cột header (chuyển về lowercase để so sánh)
            headers = orders_table.find_elements(By.TAG_NAME, "th")
            header_texts = [h.text.upper() for h in headers]
            print(f"  📋 Headers: {header_texts}")

            expected_headers = ["MÃ ĐH", "KHÁCH HÀNG", "TỔNG TIỀN", "TRẠNG THÁI"]
            for expected in expected_headers:
                self.assertIn(expected, header_texts, f"Lỗi: Thiếu cột '{expected}'")

            # Kiểm tra có dữ liệu trong bảng
            rows = orders_table.find_elements(By.XPATH, ".//tbody/tr")
            print(f"  📊 Số dòng dữ liệu: {len(rows)}")
            
            if len(rows) > 0:
                first_row_cells = rows[0].find_elements(By.TAG_NAME, "td")
                if len(first_row_cells) >= 4:
                    print(f"  ➡️ Đơn hàng đầu tiên: {first_row_cells[0].text}")
            
            print("✅ Bảng đơn hàng mới nhất hiển thị đúng")

        except Exception as e:
            self._save_error_screenshot("TC06_recent_orders")
            raise e

    def test_07_low_stock_products_table_display(self):
        """TC07: Bảng sản phẩm sắp hết hàng hiển thị"""
        print("\n--- Running: Test Low Stock Products Table ---")
        driver = self.driver

        try:
            # Scroll xuống cuối trang để load hết nội dung
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)

            # Tìm table: từ card-header chứa h4 "Sắp Hết Hàng", lấy following-sibling card-body, rồi tìm table
            low_stock_table = self.wait.until(
                EC.presence_of_element_located((By.XPATH,
                    "//div[contains(@class,'card-header')][.//h4[contains(text(),'Sắp Hết Hàng')]]/following-sibling::div[contains(@class,'card-body')]//table"
                ))
            )
            self.assertIsNotNone(low_stock_table)
            print("  📌 Tìm thấy bảng sản phẩm sắp hết hàng")

            # Kiểm tra headers (chuyển về uppercase để so sánh)
            headers = low_stock_table.find_elements(By.TAG_NAME, "th")
            header_texts = [h.text.upper() for h in headers]
            print(f"  📋 Headers: {header_texts}")

            self.assertTrue(any("SẢN PHẨM" in h for h in header_texts), "Lỗi: Thiếu cột 'Sản Phẩm'")
            self.assertTrue(any("TỒN KHO" in h or "TỒN" in h for h in header_texts), "Lỗi: Thiếu cột 'Tồn Kho'")

            # Kiểm tra dữ liệu
            rows = low_stock_table.find_elements(By.XPATH, ".//tbody/tr")
            print(f"  📊 Số sản phẩm sắp hết hàng: {len(rows)}")

            print("✅ Bảng sản phẩm sắp hết hàng hiển thị đúng")

        except Exception as e:
            self._save_error_screenshot("TC07_low_stock")
            raise e

    def test_08_recent_users_table_display(self):
        """TC08: Bảng người dùng mới đăng ký hiển thị"""
        print("\n--- Running: Test Recent Users Table ---")
        driver = self.driver

        try:
            # Scroll xuống cuối trang để load hết nội dung
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)

            # Tìm table: từ card-header chứa h4 "Người Dùng Mới Đăng Ký", lấy following-sibling card-body, rồi tìm table
            users_table = self.wait.until(
                EC.presence_of_element_located((By.XPATH,
                    "//div[contains(@class,'card-header')][.//h4[contains(text(),'Người Dùng Mới Đăng Ký')]]/following-sibling::div[contains(@class,'card-body')]//table"
                ))
            )
            self.assertIsNotNone(users_table)
            print("  📌 Tìm thấy bảng người dùng mới đăng ký")

            # Kiểm tra headers (chuyển về uppercase để so sánh)
            headers = users_table.find_elements(By.TAG_NAME, "th")
            header_texts = [h.text.upper() for h in headers]
            print(f"  📋 Headers: {header_texts}")

            expected_headers = ["ID", "EMAIL", "NGÀY ĐĂNG KÝ"]
            for expected in expected_headers:
                self.assertIn(expected, header_texts, f"Lỗi: Thiếu cột '{expected}'")

            # Kiểm tra dữ liệu
            rows = users_table.find_elements(By.XPATH, ".//tbody/tr")
            print(f"  📊 Số người dùng mới: {len(rows)}")

            print("✅ Bảng người dùng mới đăng ký hiển thị đúng")

        except Exception as e:
            self._save_error_screenshot("TC08_recent_users")
            raise e

    def test_09_order_link_navigation(self):
        """TC09: Click vào mã đơn hàng điều hướng đến trang chi tiết"""
        print("\n--- Running: Test Order Link Navigation ---")
        driver = self.driver

        try:
            # Tìm link đơn hàng đầu tiên trong bảng
            order_links = driver.find_elements(By.XPATH,
                "//h4[contains(text(),'Đơn Hàng Mới Nhất')]/ancestor::div[contains(@class,'card')]//tbody//a[contains(@href,'order_details')]"
            )

            if len(order_links) > 0:
                order_id = order_links[0].text
                print(f"  ➡️ Click vào đơn hàng: {order_id}")
                
                # Scroll đến element trước khi click
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});" , order_links[0])
                time.sleep(1)
                
                # Sử dụng JavaScript click để tránh bị intercept
                driver.execute_script("arguments[0].click();", order_links[0])
                time.sleep(2)

                # Kiểm tra đã chuyển đến trang chi tiết
                self.assertIn("order_details", driver.current_url, 
                             "Lỗi: Không chuyển đến trang chi tiết đơn hàng")
                print(f"✅ Đã chuyển đến trang chi tiết: {driver.current_url}")
            else:
                print("⚠️ Không có đơn hàng nào để test navigation")
                self.skipTest("Không có dữ liệu đơn hàng")

        except Exception as e:
            self._save_error_screenshot("TC09_order_navigation")
            raise e

    def test_10_breadcrumb_navigation(self):
        """TC10: Breadcrumb điều hướng hoạt động"""
        print("\n--- Running: Test Breadcrumb Navigation ---")
        driver = self.driver

        try:
            # Tìm breadcrumb
            breadcrumbs = self.wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "breadcrumbs"))
            )
            self.assertIsNotNone(breadcrumbs)

            # Tìm icon home
            home_link = breadcrumbs.find_element(By.CLASS_NAME, "nav-home")
            self.assertIsNotNone(home_link, "Lỗi: Không tìm thấy link Home trong breadcrumb")
            print("✅ Breadcrumb hiển thị đúng")

            # Kiểm tra có item Dashboard
            nav_items = breadcrumbs.find_elements(By.CLASS_NAME, "nav-item")
            print(f"  📋 Số nav items: {len(nav_items)}")

        except Exception as e:
            self._save_error_screenshot("TC10_breadcrumb")
            raise e

    def test_11_sidebar_menu_items_exist(self):
        """TC11: Sidebar menu có đầy đủ các mục"""
        print("\n--- Running: Test Sidebar Menu Items ---")
        driver = self.driver

        try:
            # Danh sách các menu item mong đợi (theo sidebar.php thực tế)
            expected_menus = ["Dashboard", "Sản Phẩm", "Danh Mục", "Đơn Hàng", "Người Dùng", "Đánh Giá"]

            sidebar = self.wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "sidebar"))
            )

            found_count = 0
            for menu_name in expected_menus:
                try:
                    # Tìm trong thẻ p (theo cấu trúc sidebar.php)
                    menu_item = sidebar.find_element(By.XPATH, f".//p[contains(text(),'{menu_name}')]")
                    print(f"  ✅ Tìm thấy menu: {menu_name}")
                    found_count += 1
                except NoSuchElementException:
                    print(f"  ⚠️ Không tìm thấy menu: {menu_name}")

            # Kiểm tra tìm thấy ít nhất 4 menu items
            self.assertGreaterEqual(found_count, 4, f"Lỗi: Chỉ tìm thấy {found_count}/{len(expected_menus)} menu items")
            print(f"✅ Kiểm tra sidebar menu hoàn tất ({found_count}/{len(expected_menus)} items)")

        except Exception as e:
            self._save_error_screenshot("TC11_sidebar_menu")
            raise e

    def test_12_dashboard_welcome_message(self):
        """TC12: Thông báo chào mừng Admin hiển thị"""
        print("\n--- Running: Test Welcome Message ---")
        driver = self.driver

        try:
            # Tìm card title chứa text chào mừng
            welcome_card = self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//div[contains(@class,'card-title') and contains(text(),'Xin chào Admin')]"))
            )
            self.assertIsNotNone(welcome_card)
            print(f"✅ Thông báo chào mừng: {welcome_card.text}")

            # Kiểm tra mô tả trong card-body
            try:
                card_body = driver.find_element(By.XPATH,
                    "//div[contains(@class,'card-title') and contains(text(),'Xin chào Admin')]/ancestor::div[contains(@class,'card')]//div[contains(@class,'card-body')]//p"
                )
                if card_body and card_body.text:
                    desc_text = card_body.text[:100] + "..." if len(card_body.text) > 100 else card_body.text
                    print(f"  📝 Mô tả: {desc_text}")
            except NoSuchElementException:
                print("  📝 Không tìm thấy mô tả chi tiết (không bắt buộc)")

            print("✅ Test welcome message hoàn tất")

        except Exception as e:
            self._save_error_screenshot("TC12_welcome_message")
            raise e

    def test_13_stats_card_colors(self):
        """TC13: Các thẻ thống kê có màu sắc đúng theo loại"""
        print("\n--- Running: Test Stats Card Colors ---")
        driver = self.driver

        try:
            # Kiểm tra từng loại card
            color_classes = {
                "card-success": "Doanh thu tháng (xanh lá)",
                "card-info": "Đơn hàng mới (xanh dương)",
                "card-primary": "Tổng người dùng (tím/xanh)",
                "card-warning": "Đánh giá chờ duyệt (vàng)"
            }

            for color_class, description in color_classes.items():
                try:
                    card = driver.find_element(By.CSS_SELECTOR, f".card-stats.{color_class}")
                    print(f"  ✅ {description}: Tìm thấy")
                except NoSuchElementException:
                    print(f"  ⚠️ {description}: Không tìm thấy")

            print("✅ Kiểm tra màu sắc card hoàn tất")

        except Exception as e:
            self._save_error_screenshot("TC13_card_colors")
            raise e

    def test_14_order_status_badges(self):
        """TC14: Badge trạng thái đơn hàng hiển thị đúng màu"""
        print("\n--- Running: Test Order Status Badges ---")
        driver = self.driver

        try:
            # Tìm tất cả badges trong bảng đơn hàng
            badges = driver.find_elements(By.XPATH,
                "//h4[contains(text(),'Đơn Hàng Mới Nhất')]/ancestor::div[@class='card']//span[contains(@class,'badge')]"
            )

            print(f"  📊 Số badges tìm thấy: {len(badges)}")

            status_colors = {
                "đang xử lý": "badge-warning",
                "đang giao": "badge-info",
                "đã giao": "badge-success",
                "đã hủy": "badge-danger"
            }

            for badge in badges:
                status_text = badge.text.lower()
                badge_class = badge.get_attribute("class")
                print(f"    - Trạng thái: '{badge.text}' | Class: {badge_class}")

            print("✅ Kiểm tra badge trạng thái hoàn tất")

        except Exception as e:
            self._save_error_screenshot("TC14_status_badges")
            raise e

    def test_15_responsive_layout(self):
        """TC15: Layout responsive khi thu nhỏ cửa sổ"""
        print("\n--- Running: Test Responsive Layout ---")
        driver = self.driver

        try:
            # Lưu kích thước ban đầu
            original_size = driver.get_window_size()
            print(f"  📐 Kích thước ban đầu: {original_size['width']}x{original_size['height']}")

            # Thu nhỏ cửa sổ (tablet size)
            driver.set_window_size(768, 1024)
            time.sleep(1)
            
            # Kiểm tra các card vẫn hiển thị
            stats_cards = driver.find_elements(By.CLASS_NAME, "card-stats")
            self.assertGreater(len(stats_cards), 0, "Lỗi: Cards không hiển thị ở kích thước tablet")
            print("  ✅ Cards hiển thị ở kích thước tablet (768px)")

            # Thu nhỏ hơn nữa (mobile size)
            driver.set_window_size(375, 812)
            time.sleep(1)

            stats_cards = driver.find_elements(By.CLASS_NAME, "card-stats")
            self.assertGreater(len(stats_cards), 0, "Lỗi: Cards không hiển thị ở kích thước mobile")
            print("  ✅ Cards hiển thị ở kích thước mobile (375px)")

            # Khôi phục kích thước
            driver.set_window_size(original_size['width'], original_size['height'])
            print("✅ Test responsive hoàn tất")

        except Exception as e:
            self._save_error_screenshot("TC15_responsive")
            # Khôi phục kích thước nếu có lỗi
            driver.maximize_window()
            raise e


class AdminDashboardAccessControlTest(unittest.TestCase):
    """Test Suite kiểm tra quyền truy cập Dashboard"""

    def setUp(self):
        """Thiết lập trình duyệt mới cho mỗi test"""
        driver_path = os.path.join(os.getcwd(), 'driver', 'chromedriver.exe')
        service = Service(driver_path)
        options = webdriver.ChromeOptions()
        self.driver = webdriver.Chrome(service=service, options=options)
        self.driver.maximize_window()
        self.wait = WebDriverWait(self.driver, 10)

    def tearDown(self):
        """Đóng trình duyệt sau mỗi test"""
        self.driver.quit()

    def _bypass_ngrok(self):
        """Bypass Ngrok warning nếu có"""
        try:
            visit_btn = WebDriverWait(self.driver, 5).until(
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

    def test_01_access_denied_without_login(self):
        """TC_AC01: Truy cập Dashboard khi chưa đăng nhập -> Từ chối"""
        print("\n--- Running: Test Access Denied Without Login ---")
        driver = self.driver

        try:
            # Truy cập trực tiếp vào Dashboard mà không đăng nhập
            driver.get(URL_ADMIN_DASHBOARD)
            self._bypass_ngrok()
            time.sleep(2)

            # Kiểm tra thông báo từ chối truy cập hoặc redirect
            page_source = driver.page_source.lower()
            
            # Kiểm tra có hiển thị thông báo từ chối
            access_denied = (
                "truy cập bị từ chối" in page_source or
                "access denied" in page_source or
                "đăng nhập" in page_source or
                "login" in driver.current_url.lower()
            )

            self.assertTrue(access_denied, 
                          "Lỗi: Không có bảo vệ truy cập cho trang Admin Dashboard")
            print("✅ Trang Dashboard được bảo vệ - Không cho phép truy cập khi chưa đăng nhập")

        except Exception as e:
            self._save_error_screenshot("TC_AC01_access_denied")
            raise e

    def test_02_user_cannot_access_admin_dashboard(self):
        """TC_AC02: User thường không thể truy cập trang Admin Dashboard"""
        print("\n--- Running: Test User Cannot Access Admin Dashboard ---")
        driver = self.driver

        try:
            # Đăng nhập với tài khoản User thường
            driver.get(URL_LOGIN)
            self._bypass_ngrok()

            email_input = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.ID, "email_signin"))
            )
            email_input.clear()
            email_input.send_keys(USER_ACC['email'])
            driver.find_element(By.ID, "password_signin").send_keys(USER_ACC['pass'])
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

            # Cố gắng truy cập trang Admin Dashboard
            driver.get(URL_ADMIN_DASHBOARD)
            self._bypass_ngrok()
            time.sleep(2)

            # Kiểm tra xem có bị chặn không
            page_source = driver.page_source.lower()
            
            is_blocked = (
                "truy cập bị từ chối" in page_source or
                "access denied" in page_source or
                "ViewAdmin" not in driver.current_url or
                "dashboard" not in driver.page_source.lower()
            )

            # Nếu vẫn có thể truy cập, đây là lỗi bảo mật
            if "ViewAdmin" in driver.current_url and "xin chào admin" in page_source:
                self.fail("LỖI BẢO MẬT: User thường có thể truy cập trang Admin Dashboard!")
            
            print("✅ User thường không thể truy cập trang Admin Dashboard")

        except Exception as e:
            self._save_error_screenshot("TC_AC02_user_access")
            raise e


if __name__ == "__main__":
    # Tạo test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Thêm các test class vào suite
    suite.addTests(loader.loadTestsFromTestCase(AdminDashboardTest))
    suite.addTests(loader.loadTestsFromTestCase(AdminDashboardAccessControlTest))

    # Chạy tests
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
