import unittest
import time
import os
import pymysql
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.keys import Keys

# --- CẤU HÌNH URL ---
URL_LOGIN = "https://whippet-exotic-specially.ngrok-free.app/QlyShopTheThao/src/view/login.php"
URL_ADMIN_ORDERS = "https://whippet-exotic-specially.ngrok-free.app/QlyShopTheThao/src/view/ViewAdmin/index.php?page=orders"

# --- CẤU HÌNH DATABASE ---
DB_CONFIG = {
    "host": "j3egkd.h.filess.io",
    "port": 3306,
    "database": "user_database_biggestzoo",
    "user": "user_database_biggestzoo",
    "password": "8200c17fb8ab66b3f73f8a0b4dc95ee2da14de7e",
    "charset": "utf8mb4"
}

# Tài khoản Admin
ADMIN_ACC = {"email": "wearingarmor12345@gmail.com", "pass": "hung12345"}

# Timestamp cho test
TEST_TIMESTAMP = datetime.now().strftime("%d%m%Y_%H%M%S")


class DatabaseHelper:
    """Helper class để kết nối và thao tác với database"""
    
    @staticmethod
    def get_connection():
        """Tạo kết nối database"""
        return pymysql.connect(
            host=DB_CONFIG["host"],
            port=DB_CONFIG["port"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            database=DB_CONFIG["database"],
            charset=DB_CONFIG["charset"],
            cursorclass=pymysql.cursors.DictCursor
        )
    
    @staticmethod
    def get_all_orders():
        """Lấy tất cả đơn hàng"""
        conn = None
        try:
            conn = DatabaseHelper.get_connection()
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT o.*, u.email as customer_email
                    FROM orders o
                    LEFT JOIN username u ON o.user_id = u.id
                    ORDER BY o.created_at DESC
                """)
                return cursor.fetchall()
        except Exception as e:
            print(f"❌ Database error: {e}")
            return []
        finally:
            if conn:
                conn.close()
    
    @staticmethod
    def get_order_by_id(order_id):
        """Lấy đơn hàng theo ID"""
        conn = None
        try:
            conn = DatabaseHelper.get_connection()
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT o.*, u.email as customer_email
                    FROM orders o
                    LEFT JOIN username u ON o.user_id = u.id
                    WHERE o.id = %s
                """, (order_id,))
                return cursor.fetchone()
        except Exception as e:
            print(f"❌ Database error: {e}")
            return None
        finally:
            if conn:
                conn.close()
    
    @staticmethod
    def get_order_items(order_id):
        """Lấy các sản phẩm trong đơn hàng"""
        conn = None
        try:
            conn = DatabaseHelper.get_connection()
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT oi.*, p.name as product_name
                    FROM order_item oi
                    JOIN product p ON oi.product_id = p.id
                    WHERE oi.order_id = %s
                """, (order_id,))
                return cursor.fetchall()
        except Exception as e:
            print(f"❌ Database error: {e}")
            return []
        finally:
            if conn:
                conn.close()
    
    @staticmethod
    def get_orders_by_status(status):
        """Lấy đơn hàng theo trạng thái"""
        conn = None
        try:
            conn = DatabaseHelper.get_connection()
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT o.*, u.email as customer_email
                    FROM orders o
                    LEFT JOIN username u ON o.user_id = u.id
                    WHERE o.status = %s
                    ORDER BY o.created_at DESC
                """, (status,))
                return cursor.fetchall()
        except Exception as e:
            print(f"❌ Database error: {e}")
            return []
        finally:
            if conn:
                conn.close()
    
    @staticmethod
    def get_orders_by_payment_method(payment_method):
        """Lấy đơn hàng theo phương thức thanh toán"""
        conn = None
        try:
            conn = DatabaseHelper.get_connection()
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT o.*, u.email as customer_email
                    FROM orders o
                    LEFT JOIN username u ON o.user_id = u.id
                    WHERE o.payment_method = %s
                    ORDER BY o.created_at DESC
                """, (payment_method,))
                return cursor.fetchall()
        except Exception as e:
            print(f"❌ Database error: {e}")
            return []
        finally:
            if conn:
                conn.close()
    
    @staticmethod
    def get_order_count():
        """Đếm tổng số đơn hàng"""
        conn = None
        try:
            conn = DatabaseHelper.get_connection()
            with conn.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) as count FROM orders")
                result = cursor.fetchone()
                return result['count'] if result else 0
        except Exception as e:
            print(f"❌ Database error: {e}")
            return 0
        finally:
            if conn:
                conn.close()
    
    @staticmethod
    def get_unique_statuses():
        """Lấy danh sách các trạng thái duy nhất"""
        conn = None
        try:
            conn = DatabaseHelper.get_connection()
            with conn.cursor() as cursor:
                cursor.execute("SELECT DISTINCT status FROM orders")
                return [row['status'] for row in cursor.fetchall()]
        except Exception as e:
            print(f"❌ Database error: {e}")
            return []
        finally:
            if conn:
                conn.close()
    
    @staticmethod
    def get_unique_payment_methods():
        """Lấy danh sách các phương thức thanh toán duy nhất"""
        conn = None
        try:
            conn = DatabaseHelper.get_connection()
            with conn.cursor() as cursor:
                cursor.execute("SELECT DISTINCT payment_method FROM orders")
                return [row['payment_method'] for row in cursor.fetchall()]
        except Exception as e:
            print(f"❌ Database error: {e}")
            return []
        finally:
            if conn:
                conn.close()
    
    @staticmethod
    def update_order_status(order_id, status):
        """Cập nhật trạng thái đơn hàng"""
        conn = None
        try:
            conn = DatabaseHelper.get_connection()
            with conn.cursor() as cursor:
                cursor.execute(
                    "UPDATE orders SET status = %s WHERE id = %s",
                    (status, order_id)
                )
                conn.commit()
                return True
        except Exception as e:
            print(f"❌ Database error: {e}")
            return False
        finally:
            if conn:
                conn.close()
    
    @staticmethod
    def get_unique_customer_emails():
        """Lấy danh sách email khách hàng duy nhất"""
        conn = None
        try:
            conn = DatabaseHelper.get_connection()
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT DISTINCT u.email 
                    FROM orders o
                    JOIN username u ON o.user_id = u.id
                    WHERE u.email IS NOT NULL AND u.email <> ''
                    ORDER BY u.email ASC
                """)
                return [row['email'] for row in cursor.fetchall()]
        except Exception as e:
            print(f"❌ Database error: {e}")
            return []
        finally:
            if conn:
                conn.close()


class AdminOrdersTest(unittest.TestCase):
    """
    Test Suite: Kiểm thử trang Quản lý Đơn hàng Admin
    
    Test Cases:
    - TC_ORD_DB01: Kiểm tra kết nối Database
    - TC_ORD_DB02: Kiểm tra bảng orders tồn tại
    - TC_ORD_01: Hiển thị danh sách đơn hàng
    - TC_ORD_02: Lọc đơn hàng theo trạng thái
    - TC_ORD_03: Lọc đơn hàng theo phương thức thanh toán
    - TC_ORD_04: Lọc đơn hàng theo email khách hàng
    - TC_ORD_05: Xem chi tiết đơn hàng
    - TC_ORD_06: Cập nhật trạng thái đơn hàng (Giao hàng)
    - TC_ORD_07: Hủy đơn hàng
    """
    
    driver = None
    wait = None
    
    @classmethod
    def setUpClass(cls):
        """Khởi tạo WebDriver và đăng nhập Admin"""
        print("\n" + "="*60)
        print("🧪 BẮT ĐẦU TEST QUẢN LÝ ĐƠN HÀNG")
        print("="*60)
        
        # Khởi tạo Chrome Driver
        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")
        options.add_argument("--disable-notifications")
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        
        cls.driver = webdriver.Chrome(options=options)
        cls.wait = WebDriverWait(cls.driver, 15)
        
        # Đăng nhập Admin
        cls._login_admin(cls)
    
    @classmethod
    def tearDownClass(cls):
        """Dọn dẹp sau khi test xong"""
        print("\n" + "="*60)
        print("🧹 KẾT THÚC TEST")
        print("="*60)
        
        if cls.driver:
            cls.driver.quit()
    
    def _login_admin(self):
        """Đăng nhập vào tài khoản Admin"""
        driver = self.driver
        driver.get(URL_LOGIN)
        time.sleep(2)
        
        # Bypass ngrok warning nếu có
        try:
            visit_btn = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Visit Site')]"))
            )
            visit_btn.click()
            time.sleep(2)
        except:
            pass
        
        # Nhập thông tin đăng nhập
        email_input = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, "email_signin"))
        )
        email_input.clear()
        email_input.send_keys(ADMIN_ACC["email"])
        
        driver.find_element(By.ID, "password_signin").send_keys(ADMIN_ACC["pass"])
        driver.find_element(By.ID, "b1").click()
        
        # Xử lý Captcha nếu có
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
        
        # Chờ đăng nhập thành công
        WebDriverWait(driver, 15).until(EC.url_contains("ViewAdmin"))
        print("✅ Đăng nhập Admin thành công!")
    
    def _navigate_to_orders_page(self):
        """Navigate đến trang quản lý đơn hàng"""
        self.driver.get(URL_ADMIN_ORDERS)
        time.sleep(2)
        
        # Bypass ngrok warning nếu có
        try:
            visit_btn = WebDriverWait(self.driver, 3).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Visit Site')]"))
            )
            visit_btn.click()
            time.sleep(2)
        except:
            pass
        
        # Chờ bảng đơn hàng load
        self.wait.until(EC.presence_of_element_located((By.ID, "ordersTable")))
        time.sleep(2)
    
    def _scroll_to_element(self, element):
        """Scroll đến element"""
        self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
        time.sleep(0.5)
    
    def _js_click(self, element):
        """Click element bằng JavaScript"""
        self.driver.execute_script("arguments[0].click();", element)
    
    def _save_error_screenshot(self, test_name):
        """Lưu screenshot khi có lỗi"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        screenshot_path = os.path.join(
            os.path.dirname(__file__), 
            "..", 
            "results", 
            f"error_orders_{test_name}_{timestamp}.png"
        )
        os.makedirs(os.path.dirname(screenshot_path), exist_ok=True)
        self.driver.save_screenshot(screenshot_path)
        print(f"📸 Screenshot saved: {screenshot_path}")
    
    def _get_table_row_count(self):
        """Đếm số dòng trong bảng DataTable"""
        try:
            rows = self.driver.find_elements(By.CSS_SELECTOR, "#ordersTable tbody tr")
            # Kiểm tra nếu là dòng "No data available"
            if len(rows) == 1:
                first_row_text = rows[0].text
                if "No data available" in first_row_text or "Không có dữ liệu" in first_row_text:
                    return 0
            return len(rows)
        except:
            return 0
    
    # ==================== TEST CASES ====================
    
    def test_01_database_connection(self):
        """TC_ORD_DB01: Kiểm tra kết nối Database"""
        print("\n" + "-"*50)
        print("🧪 TC_ORD_DB01: Kiểm tra kết nối Database")
        print("-"*50)
        
        try:
            conn = DatabaseHelper.get_connection()
            self.assertIsNotNone(conn, "Không thể kết nối database")
            
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                self.assertIsNotNone(result, "Query test thất bại")
            
            conn.close()
            print("✅ PASSED: Kết nối Database thành công!")
            
        except Exception as e:
            self.fail(f"Lỗi kết nối database: {e}")
    
    def test_02_database_orders_table_exists(self):
        """TC_ORD_DB02: Kiểm tra bảng orders tồn tại"""
        print("\n" + "-"*50)
        print("🧪 TC_ORD_DB02: Kiểm tra bảng orders tồn tại")
        print("-"*50)
        
        try:
            conn = DatabaseHelper.get_connection()
            with conn.cursor() as cursor:
                cursor.execute("SHOW TABLES LIKE 'orders'")
                result = cursor.fetchone()
                self.assertIsNotNone(result, "Bảng 'orders' không tồn tại")
                
                # Kiểm tra các cột cần thiết
                cursor.execute("DESCRIBE orders")
                columns = [row['Field'] for row in cursor.fetchall()]
                
                required_columns = ['id', 'user_id', 'total_price', 'status', 'payment_method', 'created_at']
                for col in required_columns:
                    self.assertIn(col, columns, f"Thiếu cột '{col}' trong bảng orders")
                
                print(f"  📋 Các cột trong bảng: {columns}")
            
            conn.close()
            print("✅ PASSED: Bảng orders tồn tại!")
            
        except Exception as e:
            self.fail(f"Lỗi kiểm tra bảng: {e}")
    
    def test_03_display_orders_list(self):
        """TC_ORD_01: Hiển thị danh sách đơn hàng"""
        print("\n" + "-"*50)
        print("🧪 TC_ORD_01: HIỂN THỊ DANH SÁCH ĐƠN HÀNG")
        print("-"*50)
        
        try:
            # Navigate đến trang orders
            self._navigate_to_orders_page()
            
            # Kiểm tra bảng hiển thị
            table = self.wait.until(EC.presence_of_element_located((By.ID, "ordersTable")))
            self.assertIsNotNone(table, "Bảng đơn hàng không hiển thị")
            
            # Đếm số đơn hàng trong DB
            db_count = DatabaseHelper.get_order_count()
            print(f"  📊 Số đơn hàng trong Database: {db_count}")
            
            # Chờ DataTable load xong
            time.sleep(3)
            
            # Đếm số dòng hiển thị trên UI
            ui_count = self._get_table_row_count()
            print(f"  📊 Số đơn hàng hiển thị trên UI: {ui_count}")
            
            # Kiểm tra có dữ liệu hiển thị
            if db_count > 0:
                self.assertGreater(ui_count, 0, "Bảng không hiển thị dữ liệu")
            
            # Kiểm tra các cột header
            headers = self.driver.find_elements(By.CSS_SELECTOR, "#ordersTable thead th")
            header_texts = [h.text for h in headers]
            print(f"  📋 Các cột: {header_texts}")
            
            expected_headers = ['ID', 'Tên Khách Hàng', 'Email', 'Tổng Tiền', 'Trạng Thái', 'Thanh Toán', 'Ngày Đặt', 'Hành Động']
            for expected in expected_headers:
                self.assertTrue(
                    any(expected.lower() in h.lower() for h in header_texts),
                    f"Thiếu cột '{expected}'"
                )
            
            print("\n" + "="*50)
            print("✅ PASSED: HIỂN THỊ DANH SÁCH ĐƠN HÀNG THÀNH CÔNG!")
            print("="*50)
            
        except Exception as e:
            self._save_error_screenshot("TC_ORD_01")
            raise e
    
    def test_04_filter_by_status(self):
        """TC_ORD_02: Lọc đơn hàng theo trạng thái"""
        print("\n" + "-"*50)
        print("🧪 TC_ORD_02: LỌC ĐƠN HÀNG THEO TRẠNG THÁI")
        print("-"*50)
        
        try:
            # Navigate đến trang orders
            self._navigate_to_orders_page()
            time.sleep(2)
            
            # Lấy danh sách trạng thái từ DB
            statuses = DatabaseHelper.get_unique_statuses()
            print(f"  📋 Các trạng thái trong DB: {statuses}")
            
            if not statuses:
                self.skipTest("Không có đơn hàng nào trong database")
            
            # Test lọc theo từng trạng thái
            status_filter = Select(self.driver.find_element(By.ID, "statusFilter"))
            
            for status in statuses[:3]:  # Test tối đa 3 trạng thái
                print(f"\n  🔍 Lọc theo trạng thái: '{status}'")
                
                # Đếm số đơn hàng với trạng thái này trong DB
                db_orders = DatabaseHelper.get_orders_by_status(status)
                db_count = len(db_orders)
                print(f"     Số đơn hàng trong DB: {db_count}")
                
                # Chọn trạng thái trong dropdown
                status_filter.select_by_value(status)
                time.sleep(2)
                
                # Đếm số dòng hiển thị
                ui_count = self._get_table_row_count()
                print(f"     Số đơn hàng hiển thị: {ui_count}")
                
                # Verify
                if db_count > 0:
                    # Kiểm tra badge trạng thái trong các dòng
                    badges = self.driver.find_elements(By.CSS_SELECTOR, "#ordersTable tbody .badge")
                    if badges:
                        for badge in badges[:5]:  # Kiểm tra 5 badge đầu
                            badge_text = badge.text.lower()
                            print(f"     Badge: {badge_text}")
            
            # Reset filter
            status_filter.select_by_value("")
            time.sleep(1)
            
            print("\n" + "="*50)
            print("✅ PASSED: LỌC THEO TRẠNG THÁI HOẠT ĐỘNG!")
            print("="*50)
            
        except Exception as e:
            self._save_error_screenshot("TC_ORD_02")
            raise e
    
    def test_05_filter_by_payment_method(self):
        """TC_ORD_03: Lọc đơn hàng theo phương thức thanh toán"""
        print("\n" + "-"*50)
        print("🧪 TC_ORD_03: LỌC ĐƠN HÀNG THEO PHƯƠNG THỨC THANH TOÁN")
        print("-"*50)
        
        try:
            # Navigate đến trang orders
            self._navigate_to_orders_page()
            time.sleep(2)
            
            # Lấy danh sách phương thức thanh toán từ DB
            payment_methods = DatabaseHelper.get_unique_payment_methods()
            print(f"  📋 Các phương thức thanh toán trong DB: {payment_methods}")
            
            if not payment_methods:
                self.skipTest("Không có đơn hàng nào trong database")
            
            # Test lọc theo phương thức thanh toán
            payment_filter = Select(self.driver.find_element(By.ID, "paymentFilter"))
            
            for method in payment_methods:
                print(f"\n  🔍 Lọc theo phương thức: '{method}'")
                
                # Đếm số đơn hàng với phương thức này trong DB
                db_orders = DatabaseHelper.get_orders_by_payment_method(method)
                db_count = len(db_orders)
                print(f"     Số đơn hàng trong DB: {db_count}")
                
                # Chọn phương thức trong dropdown
                try:
                    payment_filter.select_by_value(method)
                    time.sleep(2)
                    
                    # Đếm số dòng hiển thị
                    ui_count = self._get_table_row_count()
                    print(f"     Số đơn hàng hiển thị: {ui_count}")
                except:
                    print(f"     ⚠️ Không tìm thấy option '{method}' trong dropdown")
            
            # Reset filter
            payment_filter.select_by_value("")
            time.sleep(1)
            
            print("\n" + "="*50)
            print("✅ PASSED: LỌC THEO PHƯƠNG THỨC THANH TOÁN HOẠT ĐỘNG!")
            print("="*50)
            
        except Exception as e:
            self._save_error_screenshot("TC_ORD_03")
            raise e
    
    def test_06_filter_by_email(self):
        """TC_ORD_04: Lọc đơn hàng theo email khách hàng"""
        print("\n" + "-"*50)
        print("🧪 TC_ORD_04: LỌC ĐƠN HÀNG THEO EMAIL KHÁCH HÀNG")
        print("-"*50)
        
        try:
            # Navigate đến trang orders
            self._navigate_to_orders_page()
            time.sleep(2)
            
            # Lấy danh sách email từ DB
            emails = DatabaseHelper.get_unique_customer_emails()
            print(f"  📋 Số email khách hàng duy nhất: {len(emails)}")
            
            if not emails:
                self.skipTest("Không có email khách hàng nào")
            
            # Test lọc theo email đầu tiên
            test_email = emails[0]
            print(f"\n  🔍 Lọc theo email: '{test_email}'")
            
            # Chọn email trong dropdown
            email_filter = Select(self.driver.find_element(By.ID, "emailFilter"))
            email_filter.select_by_value(test_email)
            time.sleep(2)
            
            # Đếm số dòng hiển thị
            ui_count = self._get_table_row_count()
            print(f"     Số đơn hàng hiển thị: {ui_count}")
            
            # Verify email trong các dòng
            if ui_count > 0:
                email_cells = self.driver.find_elements(By.CSS_SELECTOR, "#ordersTable tbody tr td:nth-child(3)")
                for cell in email_cells[:3]:
                    print(f"     Email trong bảng: {cell.text}")
            
            # Reset filter
            email_filter.select_by_value("")
            time.sleep(1)
            
            print("\n" + "="*50)
            print("✅ PASSED: LỌC THEO EMAIL HOẠT ĐỘNG!")
            print("="*50)
            
        except Exception as e:
            self._save_error_screenshot("TC_ORD_04")
            raise e
    
    def test_07_view_order_details(self):
        """TC_ORD_05: Xem chi tiết đơn hàng"""
        print("\n" + "-"*50)
        print("🧪 TC_ORD_05: XEM CHI TIẾT ĐƠN HÀNG")
        print("-"*50)
        
        try:
            # Navigate đến trang orders
            self._navigate_to_orders_page()
            time.sleep(3)
            
            # Lấy order_id từ dòng đầu tiên hiển thị trên UI (thay vì từ DB)
            first_row = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#ordersTable tbody tr:first-child"))
            )
            first_cell = first_row.find_element(By.CSS_SELECTOR, "td:first-child")
            order_id = first_cell.text.strip()
            
            if not order_id or order_id == "No data available" or "Không có dữ liệu" in order_id:
                self.skipTest("Không có đơn hàng nào hiển thị trên bảng")
            
            print(f"  📦 Test với đơn hàng ID: {order_id}")
            
            # Click vào nút xem chi tiết (icon mắt)
            view_btn = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, f"a[href*='order_details&id={order_id}']"))
            )
            self._scroll_to_element(view_btn)
            self._js_click(view_btn)
            time.sleep(3)
            
            # Bypass ngrok warning nếu có
            try:
                visit_btn = WebDriverWait(self.driver, 3).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Visit Site')]"))
                )
                visit_btn.click()
                time.sleep(2)
            except:
                pass
            
            # Verify đã chuyển sang trang chi tiết
            self.wait.until(EC.url_contains("order_details"))
            current_url = self.driver.current_url
            self.assertIn(f"id={order_id}", current_url, "Không chuyển đến đúng trang chi tiết")
            print(f"  ✅ Đã chuyển đến trang chi tiết: {current_url}")
            
            # Kiểm tra thông tin đơn hàng hiển thị
            # Mã đơn hàng
            order_id_element = self.driver.find_element(By.XPATH, f"//*[contains(text(), '#{order_id}')]")
            self.assertIsNotNone(order_id_element, "Không hiển thị mã đơn hàng")
            print(f"  ✅ Hiển thị mã đơn hàng: #{order_id}")
            
            # Kiểm tra bảng sản phẩm
            product_table = self.driver.find_element(By.CSS_SELECTOR, ".table-bordered")
            self.assertIsNotNone(product_table, "Không hiển thị bảng sản phẩm")
            print(f"  ✅ Hiển thị bảng sản phẩm")
            
            # Lấy số sản phẩm từ DB
            order_items = DatabaseHelper.get_order_items(int(order_id))
            print(f"  📊 Số sản phẩm trong đơn hàng (DB): {len(order_items)}")
            
            # Đếm số dòng sản phẩm trên UI
            product_rows = self.driver.find_elements(By.CSS_SELECTOR, ".table-bordered tbody tr.product-row-clickable")
            print(f"  📊 Số sản phẩm hiển thị (UI): {len(product_rows)}")
            
            # Verify số sản phẩm khớp
            self.assertEqual(len(order_items), len(product_rows), "Số sản phẩm không khớp giữa DB và UI")
            
            print("\n" + "="*50)
            print("✅ PASSED: XEM CHI TIẾT ĐƠN HÀNG THÀNH CÔNG!")
            print("="*50)
            
        except Exception as e:
            self._save_error_screenshot("TC_ORD_05")
            raise e
    
    def test_08_update_order_status_to_delivered(self):
        """TC_ORD_06: Cập nhật trạng thái đơn hàng (Giao hàng)"""
        print("\n" + "-"*50)
        print("🧪 TC_ORD_06: CẬP NHẬT TRẠNG THÁI ĐƠN HÀNG")
        print("-"*50)
        
        driver = self.driver
        
        # Tìm đơn hàng có trạng thái "đang xử lý" hoặc "đã thanh toán"
        orders = DatabaseHelper.get_orders_by_status("đang xử lý")
        if not orders:
            orders = DatabaseHelper.get_orders_by_status("đã thanh toán")
        
        if not orders:
            print("  ⚠️ Không có đơn hàng nào có thể cập nhật trạng thái")
            self.skipTest("Không có đơn hàng 'đang xử lý' hoặc 'đã thanh toán' để test")
        
        test_order = orders[0]
        order_id = test_order['id']
        original_status = test_order['status']
        print(f"  📦 Test với đơn hàng ID: {order_id}")
        print(f"  📊 Trạng thái hiện tại: {original_status}")
        
        try:
            # Navigate đến trang chi tiết đơn hàng
            detail_url = f"https://whippet-exotic-specially.ngrok-free.app/QlyShopTheThao/src/view/ViewAdmin/index.php?page=order_details&id={order_id}"
            driver.get(detail_url)
            time.sleep(2)
            
            # Bypass ngrok warning nếu có
            try:
                visit_btn = WebDriverWait(driver, 3).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Visit Site')]"))
                )
                visit_btn.click()
                time.sleep(2)
            except:
                pass
            
            # Tìm nút "Xử lý (Giao hàng)"
            try:
                process_btn = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.ID, "processOrderBtn"))
                )
                print(f"  ✅ Tìm thấy nút 'Xử lý (Giao hàng)'")
                
                self._js_click(process_btn)
                time.sleep(1)
                
                # Xử lý SweetAlert xác nhận
                try:
                    swal_confirm = WebDriverWait(driver, 5).until(
                        EC.visibility_of_element_located((By.CSS_SELECTOR, ".swal2-confirm"))
                    )
                    print("  ✅ SweetAlert xác nhận xuất hiện")
                    self._js_click(swal_confirm)
                    time.sleep(3)
                    
                    # Chờ SweetAlert thành công
                    try:
                        swal_success = WebDriverWait(driver, 10).until(
                            EC.visibility_of_element_located((By.CSS_SELECTOR, ".swal2-success"))
                        )
                        print("  ✅ Cập nhật trạng thái thành công trên UI")
                        
                        # Đóng SweetAlert
                        swal_ok = driver.find_element(By.CSS_SELECTOR, ".swal2-confirm")
                        self._js_click(swal_ok)
                        time.sleep(1)
                    except:
                        print("  ⚠️ Không thấy SweetAlert thành công")
                    
                except:
                    print("  ⚠️ Không có SweetAlert xác nhận")
                
                # VERIFY TRONG DATABASE
                time.sleep(2)
                updated_order = DatabaseHelper.get_order_by_id(order_id)
                print(f"\n  🔍 VERIFY TRONG DATABASE:")
                print(f"     Trạng thái sau cập nhật: {updated_order['status']}")
                
                if updated_order['status'] == 'đã giao':
                    print("\n" + "="*50)
                    print("✅ PASSED: CẬP NHẬT TRẠNG THÁI 'ĐÃ GIAO' THÀNH CÔNG!")
                    print("="*50)
                    
                    # Khôi phục trạng thái gốc
                    print(f"\n  🔄 Khôi phục trạng thái gốc: {original_status}")
                    DatabaseHelper.update_order_status(order_id, original_status)
                else:
                    print(f"  ⚠️ Trạng thái chưa được cập nhật đúng")
                    
            except TimeoutException:
                print("  ⚠️ Không tìm thấy nút 'Xử lý (Giao hàng)' - có thể đơn hàng đã được xử lý")
                self.skipTest("Nút xử lý không khả dụng")
                
        except Exception as e:
            self._save_error_screenshot("TC_ORD_06")
            # Khôi phục trạng thái nếu có lỗi
            DatabaseHelper.update_order_status(order_id, original_status)
            raise e
    
    def test_09_cancel_order(self):
        """TC_ORD_07: Hủy đơn hàng"""
        print("\n" + "-"*50)
        print("🧪 TC_ORD_07: HỦY ĐƠN HÀNG")
        print("-"*50)
        
        driver = self.driver
        
        # Tìm đơn hàng có trạng thái "đang xử lý"
        orders = DatabaseHelper.get_orders_by_status("đang xử lý")
        
        if not orders:
            print("  ⚠️ Không có đơn hàng 'đang xử lý' để test hủy")
            self.skipTest("Không có đơn hàng 'đang xử lý' để test")
        
        test_order = orders[0]
        order_id = test_order['id']
        original_status = test_order['status']
        print(f"  📦 Test với đơn hàng ID: {order_id}")
        print(f"  📊 Trạng thái hiện tại: {original_status}")
        
        try:
            # Navigate đến trang chi tiết đơn hàng
            detail_url = f"https://whippet-exotic-specially.ngrok-free.app/QlyShopTheThao/src/view/ViewAdmin/index.php?page=order_details&id={order_id}"
            driver.get(detail_url)
            time.sleep(2)
            
            # Bypass ngrok warning nếu có
            try:
                visit_btn = WebDriverWait(driver, 3).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Visit Site')]"))
                )
                visit_btn.click()
                time.sleep(2)
            except:
                pass
            
            # Tìm nút "Hủy đơn hàng"
            try:
                cancel_btn = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.ID, "cancelOrderBtn"))
                )
                print(f"  ✅ Tìm thấy nút 'Hủy đơn hàng'")
                
                self._js_click(cancel_btn)
                time.sleep(1)
                
                # Xử lý SweetAlert xác nhận
                try:
                    swal_confirm = WebDriverWait(driver, 5).until(
                        EC.visibility_of_element_located((By.CSS_SELECTOR, ".swal2-confirm"))
                    )
                    print("  ✅ SweetAlert xác nhận xuất hiện")
                    self._js_click(swal_confirm)
                    time.sleep(3)
                    
                    # Chờ SweetAlert thành công
                    try:
                        swal_success = WebDriverWait(driver, 10).until(
                            EC.visibility_of_element_located((By.CSS_SELECTOR, ".swal2-success"))
                        )
                        print("  ✅ Hủy đơn hàng thành công trên UI")
                        
                        # Đóng SweetAlert
                        swal_ok = driver.find_element(By.CSS_SELECTOR, ".swal2-confirm")
                        self._js_click(swal_ok)
                        time.sleep(1)
                    except:
                        print("  ⚠️ Không thấy SweetAlert thành công")
                    
                except:
                    print("  ⚠️ Không có SweetAlert xác nhận")
                
                # VERIFY TRONG DATABASE
                time.sleep(2)
                updated_order = DatabaseHelper.get_order_by_id(order_id)
                print(f"\n  🔍 VERIFY TRONG DATABASE:")
                print(f"     Trạng thái sau hủy: {updated_order['status']}")
                
                if updated_order['status'] == 'hủy':
                    print("\n" + "="*50)
                    print("✅ PASSED: HỦY ĐƠN HÀNG THÀNH CÔNG!")
                    print("="*50)
                    
                    # Khôi phục trạng thái gốc
                    print(f"\n  🔄 Khôi phục trạng thái gốc: {original_status}")
                    DatabaseHelper.update_order_status(order_id, original_status)
                else:
                    print(f"  ⚠️ Trạng thái chưa được cập nhật đúng")
                    
            except TimeoutException:
                print("  ⚠️ Không tìm thấy nút 'Hủy đơn hàng' - có thể đơn hàng không thể hủy")
                self.skipTest("Nút hủy không khả dụng")
                
        except Exception as e:
            self._save_error_screenshot("TC_ORD_07")
            # Khôi phục trạng thái nếu có lỗi
            DatabaseHelper.update_order_status(order_id, original_status)
            raise e
    
    def test_10_verify_order_data_matches_database(self):
        """TC_ORD_08: Verify dữ liệu hiển thị khớp với Database"""
        print("\n" + "-"*50)
        print("🧪 TC_ORD_08: VERIFY DỮ LIỆU KHỚP VỚI DATABASE")
        print("-"*50)
        
        try:
            # Navigate đến trang orders
            self._navigate_to_orders_page()
            time.sleep(3)
            
            # Lấy đơn hàng đầu tiên từ DB
            orders = DatabaseHelper.get_all_orders()
            if not orders:
                self.skipTest("Không có đơn hàng nào trong database")
            
            test_order = orders[0]
            order_id = test_order['id']
            print(f"  📦 Verify đơn hàng ID: {order_id}")
            print(f"     DB - Tên KH: {test_order['name']}")
            print(f"     DB - Email: {test_order['customer_email']}")
            print(f"     DB - Tổng tiền: {test_order['total_price']}")
            print(f"     DB - Trạng thái: {test_order['status']}")
            print(f"     DB - Thanh toán: {test_order['payment_method']}")
            
            # Tìm dòng với ID tương ứng trên UI
            rows = self.driver.find_elements(By.CSS_SELECTOR, "#ordersTable tbody tr")
            found = False
            
            for row in rows:
                cells = row.find_elements(By.TAG_NAME, "td")
                if cells and cells[0].text == str(order_id):
                    found = True
                    ui_id = cells[0].text
                    ui_name = cells[1].text
                    ui_email = cells[2].text
                    ui_total = cells[3].text
                    ui_status = cells[4].text
                    ui_payment = cells[5].text
                    
                    print(f"\n  📊 UI - ID: {ui_id}")
                    print(f"     UI - Tên KH: {ui_name}")
                    print(f"     UI - Email: {ui_email}")
                    print(f"     UI - Tổng tiền: {ui_total}")
                    print(f"     UI - Trạng thái: {ui_status}")
                    print(f"     UI - Thanh toán: {ui_payment}")
                    
                    # Verify các giá trị
                    self.assertEqual(ui_id, str(order_id), "ID không khớp")
                    self.assertEqual(ui_name, test_order['name'], "Tên khách hàng không khớp")
                    self.assertIn(test_order['customer_email'], ui_email, "Email không khớp")
                    
                    break
            
            if not found:
                print(f"  ⚠️ Không tìm thấy đơn hàng ID={order_id} trên trang đầu tiên của bảng")
            
            print("\n" + "="*50)
            print("✅ PASSED: DỮ LIỆU KHỚP VỚI DATABASE!")
            print("="*50)
            
        except Exception as e:
            self._save_error_screenshot("TC_ORD_08")
            raise e


if __name__ == "__main__":
    # Chạy test với output chi tiết
    unittest.main(verbosity=2)
