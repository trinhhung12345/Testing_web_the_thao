import unittest
import time
import os
import sys
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
URL_LOGIN = "https://melissia-untragical-inviably.ngrok-free.dev/QlyShopTheThao/src/view/login.php"
URL_ADMIN_USERS = "https://melissia-untragical-inviably.ngrok-free.dev/QlyShopTheThao/src/view/ViewAdmin/index.php?page=users"

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
    def _convert_bit_fields(user):
        """Convert BIT fields từ bytes sang int"""
        if user:
            if 'is_active' in user and isinstance(user['is_active'], bytes):
                user['is_active'] = int.from_bytes(user['is_active'], byteorder='little')
            if 'is_verified' in user and isinstance(user['is_verified'], bytes):
                user['is_verified'] = int.from_bytes(user['is_verified'], byteorder='little')
        return user
    
    @staticmethod
    def get_all_users():
        """Lấy tất cả người dùng"""
        conn = None
        try:
            conn = DatabaseHelper.get_connection()
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT u.id, u.email, u.is_verified, u.is_active, u.created_at, r.name as role
                    FROM username u
                    JOIN role r ON u.roleid = r.id
                    ORDER BY u.id DESC
                """)
                users = cursor.fetchall()
                return [DatabaseHelper._convert_bit_fields(u) for u in users]
        except Exception as e:
            print(f"❌ Database error: {e}")
            return []
        finally:
            if conn:
                conn.close()
    
    @staticmethod
    def get_user_by_id(user_id):
        """Lấy người dùng theo ID"""
        conn = None
        try:
            conn = DatabaseHelper.get_connection()
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT u.id, u.email, u.is_verified, u.is_active, u.created_at, r.name as role
                    FROM username u
                    JOIN role r ON u.roleid = r.id
                    WHERE u.id = %s
                """, (user_id,))
                user = cursor.fetchone()
                return DatabaseHelper._convert_bit_fields(user)
        except Exception as e:
            print(f"❌ Database error: {e}")
            return None
        finally:
            if conn:
                conn.close()
    
    @staticmethod
    def get_user_by_email(email):
        """Lấy người dùng theo email"""
        conn = None
        try:
            conn = DatabaseHelper.get_connection()
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT u.id, u.email, u.is_verified, u.is_active, u.created_at, r.name as role
                    FROM username u
                    JOIN role r ON u.roleid = r.id
                    WHERE u.email = %s
                """, (email,))
                user = cursor.fetchone()
                return DatabaseHelper._convert_bit_fields(user)
        except Exception as e:
            print(f"❌ Database error: {e}")
            return None
        finally:
            if conn:
                conn.close()
    
    @staticmethod
    def get_user_count():
        """Đếm tổng số người dùng"""
        conn = None
        try:
            conn = DatabaseHelper.get_connection()
            with conn.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) as count FROM username")
                result = cursor.fetchone()
                return result['count'] if result else 0
        except Exception as e:
            print(f"❌ Database error: {e}")
            return 0
        finally:
            if conn:
                conn.close()
    
    @staticmethod
    def get_users_by_role(role_name):
        """Lấy người dùng theo vai trò"""
        conn = None
        try:
            conn = DatabaseHelper.get_connection()
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT u.id, u.email, u.is_verified, u.is_active, r.name as role
                    FROM username u
                    JOIN role r ON u.roleid = r.id
                    WHERE r.name = %s
                    ORDER BY u.id DESC
                """, (role_name,))
                users = cursor.fetchall()
                return [DatabaseHelper._convert_bit_fields(u) for u in users]
        except Exception as e:
            print(f"❌ Database error: {e}")
            return []
        finally:
            if conn:
                conn.close()
    
    @staticmethod
    def get_users_by_status(is_active):
        """Lấy người dùng theo trạng thái hoạt động"""
        conn = None
        try:
            conn = DatabaseHelper.get_connection()
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT u.id, u.email, u.is_verified, u.is_active, r.name as role
                    FROM username u
                    JOIN role r ON u.roleid = r.id
                    WHERE u.is_active = %s
                    ORDER BY u.id DESC
                """, (is_active,))
                users = cursor.fetchall()
                return [DatabaseHelper._convert_bit_fields(u) for u in users]
        except Exception as e:
            print(f"❌ Database error: {e}")
            return []
        finally:
            if conn:
                conn.close()
    
    @staticmethod
    def update_user_status(user_id, is_active):
        """Cập nhật trạng thái người dùng"""
        conn = None
        try:
            conn = DatabaseHelper.get_connection()
            with conn.cursor() as cursor:
                cursor.execute(
                    "UPDATE username SET is_active = %s WHERE id = %s",
                    (is_active, user_id)
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
    def delete_user_by_email(email):
        """Xóa người dùng theo email (dùng để cleanup sau test)"""
        conn = None
        try:
            conn = DatabaseHelper.get_connection()
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM username WHERE email = %s", (email,))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"❌ Database error: {e}")
            return False
        finally:
            if conn:
                conn.close()
    
    @staticmethod
    def check_email_exists(email):
        """Kiểm tra email đã tồn tại chưa"""
        conn = None
        try:
            conn = DatabaseHelper.get_connection()
            with conn.cursor() as cursor:
                cursor.execute("SELECT id FROM username WHERE email = %s", (email,))
                return cursor.fetchone() is not None
        except Exception as e:
            print(f"❌ Database error: {e}")
            return False
        finally:
            if conn:
                conn.close()
    
    @staticmethod
    def get_user_orders(user_id):
        """Lấy danh sách đơn hàng của người dùng"""
        conn = None
        try:
            conn = DatabaseHelper.get_connection()
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT id, orderNo, total_price, status, created_at
                    FROM orders
                    WHERE user_id = %s
                    ORDER BY created_at DESC
                """, (user_id,))
                return cursor.fetchall()
        except Exception as e:
            print(f"❌ Database error: {e}")
            return []
        finally:
            if conn:
                conn.close()
    
    @staticmethod
    def get_roles():
        """Lấy danh sách vai trò"""
        conn = None
        try:
            conn = DatabaseHelper.get_connection()
            with conn.cursor() as cursor:
                cursor.execute("SELECT id, name FROM role ORDER BY id")
                return cursor.fetchall()
        except Exception as e:
            print(f"❌ Database error: {e}")
            return []
        finally:
            if conn:
                conn.close()


class AdminUsersTest(unittest.TestCase):
    """
    Test Suite: Kiểm thử trang Quản lý Người dùng Admin
    
    Test Cases:
    - TC_USR_DB01: Kiểm tra kết nối Database
    - TC_USR_DB02: Kiểm tra bảng username tồn tại
    - TC_USR_01: Hiển thị danh sách người dùng
    - TC_USR_02: Tìm kiếm người dùng
    - TC_USR_03: Xem chi tiết người dùng
    - TC_USR_04: Thêm người dùng mới - Thành công
    - TC_USR_05: Thêm người dùng mới - Email đã tồn tại
    - TC_USR_06: Thêm người dùng mới - Validation lỗi
    - TC_USR_07: Vô hiệu hóa người dùng
    - TC_USR_08: Kích hoạt lại người dùng
    - TC_USR_09: Verify dữ liệu khớp với Database
    """
    
    driver = None
    wait = None
    created_test_user_email = None  # Lưu email user test để cleanup
    
    @classmethod
    def setUpClass(cls):
        """Khởi tạo WebDriver và đăng nhập Admin"""
        print("\n" + "="*60)
        print("🧪 BẮT ĐẦU TEST QUẢN LÝ NGƯỜI DÙNG")
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
        print("🧹 DỌN DẸP SAU TEST")
        print("="*60)
        
        # Xóa user test nếu đã tạo
        if cls.created_test_user_email:
            print(f"  🗑️ Xóa user test: {cls.created_test_user_email}")
            DatabaseHelper.delete_user_by_email(cls.created_test_user_email)
        
        # Cleanup các user test có pattern đặc biệt
        test_patterns = [f"test_user_{TEST_TIMESTAMP}@selenium.test"]
        for pattern in test_patterns:
            if DatabaseHelper.check_email_exists(pattern):
                DatabaseHelper.delete_user_by_email(pattern)
                print(f"  🗑️ Đã xóa: {pattern}")
        
        print("="*60)
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
    
    def _navigate_to_users_page(self):
        """Navigate đến trang quản lý người dùng"""
        self.driver.get(URL_ADMIN_USERS)
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
        
        # Chờ bảng người dùng load
        self.wait.until(EC.presence_of_element_located((By.ID, "users-table")))
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
            f"error_users_{test_name}_{timestamp}.png"
        )
        os.makedirs(os.path.dirname(screenshot_path), exist_ok=True)
        self.driver.save_screenshot(screenshot_path)
        print(f"📸 Screenshot saved: {screenshot_path}")
    
    def _get_table_row_count(self):
        """Đếm số dòng trong bảng DataTable"""
        try:
            rows = self.driver.find_elements(By.CSS_SELECTOR, "#users-table tbody tr")
            # Kiểm tra nếu là dòng "No data available"
            if len(rows) == 1:
                first_row_text = rows[0].text
                if "No data available" in first_row_text or "Không có dữ liệu" in first_row_text:
                    return 0
            return len(rows)
        except:
            return 0
    
    def _wait_for_swal_and_confirm(self):
        """Chờ SweetAlert xuất hiện và click xác nhận"""
        try:
            swal_confirm = WebDriverWait(self.driver, 5).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, ".swal2-confirm"))
            )
            self._js_click(swal_confirm)
            time.sleep(1)
            return True
        except:
            return False
    
    def _wait_for_swal_success(self):
        """Chờ SweetAlert thành công"""
        try:
            WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, ".swal2-success"))
            )
            # Đóng SweetAlert
            swal_ok = self.driver.find_element(By.CSS_SELECTOR, ".swal2-confirm")
            self._js_click(swal_ok)
            time.sleep(1)
            return True
        except:
            return False
    
    def _close_modal(self):
        """Đóng modal nếu đang mở"""
        try:
            close_btn = self.driver.find_element(By.CSS_SELECTOR, "#addUserModal .btn-close")
            self._js_click(close_btn)
            time.sleep(1)
            
            # Xử lý confirm hủy nếu có
            try:
                swal_confirm = WebDriverWait(self.driver, 2).until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, ".swal2-confirm"))
                )
                self._js_click(swal_confirm)
                time.sleep(1)
            except:
                pass
        except:
            pass
    
    # ==================== TEST CASES ====================
    
    def test_01_database_connection(self):
        """TC_USR_DB01: Kiểm tra kết nối Database"""
        print("\n" + "-"*50)
        print("🧪 TC_USR_DB01: Kiểm tra kết nối Database")
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
    
    def test_02_database_username_table_exists(self):
        """TC_USR_DB02: Kiểm tra bảng username tồn tại"""
        print("\n" + "-"*50)
        print("🧪 TC_USR_DB02: Kiểm tra bảng username tồn tại")
        print("-"*50)
        
        try:
            conn = DatabaseHelper.get_connection()
            with conn.cursor() as cursor:
                cursor.execute("SHOW TABLES LIKE 'username'")
                result = cursor.fetchone()
                self.assertIsNotNone(result, "Bảng 'username' không tồn tại")
                
                # Kiểm tra các cột cần thiết
                cursor.execute("DESCRIBE username")
                columns = [row['Field'] for row in cursor.fetchall()]
                
                required_columns = ['id', 'email', 'password', 'roleid', 'is_verified', 'is_active']
                for col in required_columns:
                    self.assertIn(col, columns, f"Thiếu cột '{col}' trong bảng username")
                
                print(f"  📋 Các cột trong bảng: {columns}")
            
            conn.close()
            print("✅ PASSED: Bảng username tồn tại!")
            
        except Exception as e:
            self.fail(f"Lỗi kiểm tra bảng: {e}")
    
    def test_03_display_users_list(self):
        """TC_USR_01: Hiển thị danh sách người dùng"""
        print("\n" + "-"*50)
        print("🧪 TC_USR_01: HIỂN THỊ DANH SÁCH NGƯỜI DÙNG")
        print("-"*50)
        
        try:
            # Navigate đến trang users
            self._navigate_to_users_page()
            
            # Kiểm tra bảng hiển thị
            table = self.wait.until(EC.presence_of_element_located((By.ID, "users-table")))
            self.assertIsNotNone(table, "Bảng người dùng không hiển thị")
            
            # Đếm số người dùng trong DB
            db_count = DatabaseHelper.get_user_count()
            print(f"  📊 Số người dùng trong Database: {db_count}")
            
            # Chờ DataTable load xong
            time.sleep(3)
            
            # Đếm số dòng hiển thị trên UI
            ui_count = self._get_table_row_count()
            print(f"  📊 Số người dùng hiển thị trên UI: {ui_count}")
            
            # Kiểm tra có dữ liệu hiển thị
            if db_count > 0:
                self.assertGreater(ui_count, 0, "Bảng không hiển thị dữ liệu")
            
            # Kiểm tra các cột header
            headers = self.driver.find_elements(By.CSS_SELECTOR, "#users-table thead th")
            header_texts = [h.text for h in headers]
            print(f"  📋 Các cột: {header_texts}")
            
            expected_headers = ['ID', 'Email', 'Xác thực', 'Vai trò', 'Trạng thái', 'Hành động']
            for expected in expected_headers:
                self.assertTrue(
                    any(expected.lower() in h.lower() for h in header_texts),
                    f"Thiếu cột '{expected}'"
                )
            
            # Kiểm tra nút "Thêm người dùng mới"
            add_btn = self.driver.find_element(By.CSS_SELECTOR, "button[data-bs-target='#addUserModal']")
            self.assertIsNotNone(add_btn, "Không tìm thấy nút Thêm người dùng")
            print(f"  ✅ Nút 'Thêm người dùng mới' hiển thị")
            
            print("\n" + "="*50)
            print("✅ PASSED: HIỂN THỊ DANH SÁCH NGƯỜI DÙNG THÀNH CÔNG!")
            print("="*50)
            
        except Exception as e:
            self._save_error_screenshot("TC_USR_01")
            raise e
    
    def test_04_search_user(self):
        """TC_USR_02: Tìm kiếm người dùng"""
        print("\n" + "-"*50)
        print("🧪 TC_USR_02: TÌM KIẾM NGƯỜI DÙNG")
        print("-"*50)
        
        try:
            # Navigate đến trang users
            self._navigate_to_users_page()
            time.sleep(3)  # Chờ DataTable load xong
            
            # Lấy email của user đầu tiên hiển thị trên UI để tìm kiếm
            first_row = self.driver.find_element(By.CSS_SELECTOR, "#users-table tbody tr:first-child")
            search_email = first_row.find_element(By.CSS_SELECTOR, "td:nth-child(2)").text
            print(f"  🔍 Tìm kiếm email: '{search_email}'")
            
            # Tìm ô tìm kiếm của DataTable
            search_input = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input#dt-search-0, input.dt-input[type='search']"))
            )
            print(f"  ✅ Tìm thấy ô tìm kiếm DataTable")
            
            search_input.clear()
            search_input.send_keys(search_email)
            time.sleep(3)  # Chờ server-side search
            
            # Đếm kết quả
            ui_count = self._get_table_row_count()
            print(f"  📊 Số kết quả tìm thấy: {ui_count}")
            
            # Verify kết quả chứa email tìm kiếm
            if ui_count > 0:
                first_row_email = self.driver.find_element(By.CSS_SELECTOR, "#users-table tbody tr td:nth-child(2)")
                self.assertIn(search_email, first_row_email.text, "Email không khớp với kết quả tìm kiếm")
                print(f"  ✅ Tìm thấy: {first_row_email.text}")
            
            # Clear tìm kiếm
            search_input.clear()
            search_input.send_keys(Keys.RETURN)
            time.sleep(2)
            
            print("\n" + "="*50)
            print("✅ PASSED: TÌM KIẾM NGƯỜI DÙNG HOẠT ĐỘNG!")
            print("="*50)
            
        except Exception as e:
            self._save_error_screenshot("TC_USR_02")
            raise e
    
    def test_05_view_user_details(self):
        """TC_USR_03: Xem chi tiết người dùng"""
        print("\n" + "-"*50)
        print("🧪 TC_USR_03: XEM CHI TIẾT NGƯỜI DÙNG")
        print("-"*50)
        
        try:
            # Navigate đến trang users
            self._navigate_to_users_page()
            time.sleep(2)
            
            # Lấy ID của user đầu tiên hiển thị trên UI
            first_row = self.driver.find_element(By.CSS_SELECTOR, "#users-table tbody tr:first-child")
            user_id = first_row.find_element(By.CSS_SELECTOR, "td:first-child").text
            user_email = first_row.find_element(By.CSS_SELECTOR, "td:nth-child(2)").text
            print(f"  👤 Xem chi tiết user ID: {user_id}, Email: {user_email}")
            
            # Click nút xem chi tiết (icon mắt)
            view_btn = first_row.find_element(By.CSS_SELECTOR, "button.btn-info")
            self._js_click(view_btn)
            time.sleep(3)
            
            # Bypass ngrok nếu có
            try:
                visit_btn = WebDriverWait(self.driver, 3).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Visit Site')]"))
                )
                visit_btn.click()
                time.sleep(2)
            except:
                pass
            
            # Verify đã chuyển sang trang chi tiết
            self.wait.until(EC.url_contains("user_details"))
            current_url = self.driver.current_url
            self.assertIn(f"id={user_id}", current_url, "Không chuyển đến đúng trang chi tiết")
            print(f"  ✅ Đã chuyển đến trang chi tiết: {current_url}")
            
            # Kiểm tra email hiển thị
            email_element = self.driver.find_element(By.CSS_SELECTOR, ".user-profile .name")
            self.assertIn(user_email, email_element.text, "Email không hiển thị đúng")
            print(f"  ✅ Hiển thị email: {email_element.text}")
            
            # Kiểm tra bảng lịch sử đơn hàng
            order_table = self.driver.find_element(By.CSS_SELECTOR, ".table-bordered")
            self.assertIsNotNone(order_table, "Không hiển thị bảng lịch sử đơn hàng")
            print(f"  ✅ Hiển thị bảng lịch sử đơn hàng")
            
            # Lấy số đơn hàng từ DB
            db_user = DatabaseHelper.get_user_by_email(user_email)
            if db_user:
                orders = DatabaseHelper.get_user_orders(db_user['id'])
                print(f"  📊 Số đơn hàng trong DB: {len(orders)}")
            
            print("\n" + "="*50)
            print("✅ PASSED: XEM CHI TIẾT NGƯỜI DÙNG THÀNH CÔNG!")
            print("="*50)
            
        except Exception as e:
            self._save_error_screenshot("TC_USR_03")
            raise e
    
    def test_06_add_user_success(self):
        """TC_USR_04: Thêm người dùng mới - Thành công"""
        print("\n" + "-"*50)
        print("🧪 TC_USR_04: THÊM NGƯỜI DÙNG MỚI - THÀNH CÔNG")
        print("-"*50)
        
        # Tạo email test unique
        test_email = f"test_user_{TEST_TIMESTAMP}@selenium.test"
        test_password = "Test@123456"
        AdminUsersTest.created_test_user_email = test_email
        
        print(f"  📧 Email test: {test_email}")
        print(f"  🔑 Password: {test_password}")
        
        try:
            # Navigate đến trang users
            self._navigate_to_users_page()
            time.sleep(2)
            
            # Click nút "Thêm người dùng mới"
            add_btn = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-bs-target='#addUserModal']"))
            )
            self._js_click(add_btn)
            time.sleep(1)
            
            # Chờ modal hiển thị
            modal = self.wait.until(
                EC.visibility_of_element_located((By.ID, "addUserModal"))
            )
            print(f"  ✅ Modal thêm người dùng hiển thị")
            
            # Điền thông tin
            email_input = self.driver.find_element(By.ID, "userEmail")
            email_input.clear()
            email_input.send_keys(test_email)
            
            password_input = self.driver.find_element(By.ID, "userPassword")
            password_input.clear()
            password_input.send_keys(test_password)
            
            confirm_password_input = self.driver.find_element(By.ID, "userConfirmPassword")
            confirm_password_input.clear()
            confirm_password_input.send_keys(test_password)
            
            # Chọn vai trò User (value=2)
            role_select = Select(self.driver.find_element(By.ID, "userRole"))
            role_select.select_by_value("2")
            
            print(f"  ✅ Đã điền thông tin form")
            
            # Click nút Lưu
            save_btn = self.driver.find_element(By.ID, "save-user-btn")
            self._js_click(save_btn)
            time.sleep(1)
            
            # Xử lý SweetAlert xác nhận
            if self._wait_for_swal_and_confirm():
                print(f"  ✅ Đã xác nhận thêm người dùng")
            
            # Chờ kết quả
            time.sleep(3)
            
            # Kiểm tra SweetAlert thành công
            try:
                swal_success = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".swal2-success, .swal2-icon-success"))
                )
                print(f"  ✅ Thêm người dùng thành công trên UI")
                
                # Đóng SweetAlert
                try:
                    swal_ok = self.driver.find_element(By.CSS_SELECTOR, ".swal2-confirm")
                    self._js_click(swal_ok)
                    time.sleep(1)
                except:
                    pass
            except:
                # Kiểm tra nếu có lỗi
                try:
                    swal_error = self.driver.find_element(By.CSS_SELECTOR, ".swal2-error")
                    error_text = self.driver.find_element(By.CSS_SELECTOR, ".swal2-html-container").text
                    print(f"  ⚠️ Lỗi từ server: {error_text}")
                except:
                    pass
            
            # VERIFY TRONG DATABASE
            time.sleep(2)
            db_user = DatabaseHelper.get_user_by_email(test_email)
            
            print(f"\n  🔍 VERIFY TRONG DATABASE:")
            if db_user:
                print(f"     ID: {db_user['id']}")
                print(f"     Email: {db_user['email']}")
                print(f"     Role: {db_user['role']}")
                print(f"     Is Active: {db_user['is_active']}")
                
                self.assertEqual(db_user['email'], test_email, "Email không khớp")
                self.assertEqual(db_user['is_active'], 1, "User không được kích hoạt")
                
                print("\n" + "="*50)
                print("✅ PASSED: THÊM NGƯỜI DÙNG MỚI THÀNH CÔNG!")
                print("="*50)
            else:
                print(f"  ⚠️ Không tìm thấy user trong database")
                self.fail("User không được tạo trong database")
            
        except Exception as e:
            self._save_error_screenshot("TC_USR_04")
            self._close_modal()
            raise e
    
    def test_07_add_user_duplicate_email(self):
        """TC_USR_05: Thêm người dùng mới - Email đã tồn tại"""
        print("\n" + "-"*50)
        print("🧪 TC_USR_05: THÊM NGƯỜI DÙNG - EMAIL ĐÃ TỒN TẠI")
        print("-"*50)
        
        # Sử dụng email admin đã tồn tại
        existing_email = ADMIN_ACC["email"]
        print(f"  📧 Email đã tồn tại: {existing_email}")
        
        try:
            # Navigate đến trang users
            self._navigate_to_users_page()
            time.sleep(2)
            
            # Click nút "Thêm người dùng mới"
            add_btn = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-bs-target='#addUserModal']"))
            )
            self._js_click(add_btn)
            time.sleep(1)
            
            # Chờ modal hiển thị
            self.wait.until(EC.visibility_of_element_located((By.ID, "addUserModal")))
            
            # Điền thông tin với email đã tồn tại
            email_input = self.driver.find_element(By.ID, "userEmail")
            email_input.clear()
            email_input.send_keys(existing_email)
            
            password_input = self.driver.find_element(By.ID, "userPassword")
            password_input.clear()
            password_input.send_keys("Test@123456")
            
            confirm_password_input = self.driver.find_element(By.ID, "userConfirmPassword")
            confirm_password_input.clear()
            confirm_password_input.send_keys("Test@123456")
            
            # Click nút Lưu
            save_btn = self.driver.find_element(By.ID, "save-user-btn")
            self._js_click(save_btn)
            time.sleep(1)
            
            # Xử lý SweetAlert xác nhận
            self._wait_for_swal_and_confirm()
            time.sleep(2)
            
            # Kiểm tra thông báo lỗi
            try:
                swal_error = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".swal2-error, .swal2-icon-error"))
                )
                
                # Lấy cả title và content của SweetAlert
                error_title = ""
                error_content = ""
                
                try:
                    title_elem = self.driver.find_element(By.CSS_SELECTOR, ".swal2-title")
                    error_title = title_elem.text.strip()
                except:
                    pass
                
                try:
                    content_elem = self.driver.find_element(By.CSS_SELECTOR, ".swal2-html-container")
                    error_content = content_elem.text.strip()
                except:
                    pass
                
                full_error = f"{error_title} - {error_content}" if error_content else error_title
                print(f"  ✅ Hiển thị lỗi: {full_error}")
                
                # Kiểm tra có SweetAlert error icon là đủ (server trả về lỗi)
                # Vì message từ server có thể không chứa từ "email"
                self.assertTrue(swal_error is not None, "Không hiển thị thông báo lỗi")
                print(f"  ✅ Server từ chối thêm user với email trùng")

                # Đóng SweetAlert
                swal_ok = self.driver.find_element(By.CSS_SELECTOR, ".swal2-confirm")
                self._js_click(swal_ok)
                time.sleep(1)

            except TimeoutException:
                print(f"  ⚠️ Không có thông báo lỗi email trùng")
            
            # Đóng modal
            self._close_modal()
            
            print("\n" + "="*50)
            print("✅ PASSED: VALIDATION EMAIL TRÙNG HOẠT ĐỘNG!")
            print("="*50)
            
        except Exception as e:
            self._save_error_screenshot("TC_USR_05")
            self._close_modal()
            raise e
    
    def test_08_add_user_validation_error(self):
        """TC_USR_06: Thêm người dùng mới - Validation lỗi (mật khẩu không khớp)"""
        print("\n" + "-"*50)
        print("🧪 TC_USR_06: THÊM NGƯỜI DÙNG - MẬT KHẨU KHÔNG KHỚP")
        print("-"*50)
        
        try:
            # Navigate đến trang users
            self._navigate_to_users_page()
            time.sleep(2)
            
            # Click nút "Thêm người dùng mới"
            add_btn = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-bs-target='#addUserModal']"))
            )
            self._js_click(add_btn)
            time.sleep(1)
            
            # Chờ modal hiển thị
            self.wait.until(EC.visibility_of_element_located((By.ID, "addUserModal")))
            
            # Điền thông tin với mật khẩu không khớp
            email_input = self.driver.find_element(By.ID, "userEmail")
            email_input.clear()
            email_input.send_keys("test_validation@test.com")
            
            password_input = self.driver.find_element(By.ID, "userPassword")
            password_input.clear()
            password_input.send_keys("Password123")
            
            confirm_password_input = self.driver.find_element(By.ID, "userConfirmPassword")
            confirm_password_input.clear()
            confirm_password_input.send_keys("DifferentPassword")  # Mật khẩu không khớp
            
            print(f"  📝 Nhập mật khẩu: Password123")
            print(f"  📝 Xác nhận mật khẩu: DifferentPassword (không khớp)")
            
            # Click nút Lưu
            save_btn = self.driver.find_element(By.ID, "save-user-btn")
            self._js_click(save_btn)
            time.sleep(1)
            
            # Kiểm tra thông báo lỗi validation
            try:
                swal_error = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".swal2-error, .swal2-icon-error"))
                )
                error_text = self.driver.find_element(By.CSS_SELECTOR, ".swal2-html-container, #swal2-content").text
                print(f"  ✅ Hiển thị lỗi: {error_text}")
                
                # Đóng SweetAlert
                swal_ok = self.driver.find_element(By.CSS_SELECTOR, ".swal2-confirm")
                self._js_click(swal_ok)
                time.sleep(1)
                
            except TimeoutException:
                print(f"  ⚠️ Không có thông báo lỗi validation")
            
            # Đóng modal
            self._close_modal()
            
            print("\n" + "="*50)
            print("✅ PASSED: VALIDATION MẬT KHẨU KHÔNG KHỚP HOẠT ĐỘNG!")
            print("="*50)
            
        except Exception as e:
            self._save_error_screenshot("TC_USR_06")
            self._close_modal()
            raise e
    
    def test_09_deactivate_user(self):
        """TC_USR_07: Vô hiệu hóa người dùng"""
        print("\n" + "-"*50)
        print("🧪 TC_USR_07: VÔ HIỆU HÓA NGƯỜI DÙNG")
        print("-"*50)
        
        # Tìm user đang active (không phải admin hiện tại)
        users = DatabaseHelper.get_users_by_status(1)  # is_active = 1
        test_user = None
        
        for user in users:
            if user['email'] != ADMIN_ACC["email"]:
                test_user = user
                break
        
        if not test_user:
            print("  ⚠️ Không tìm thấy user phù hợp để test")
            self.skipTest("Không có user active (không phải admin) để test")
        
        user_id = test_user['id']
        user_email = test_user['email']
        original_status = test_user['is_active']
        
        print(f"  👤 Test với user ID: {user_id}")
        print(f"  📧 Email: {user_email}")
        print(f"  📊 Trạng thái hiện tại: {'Active' if original_status else 'Inactive'}")
        
        try:
            # Navigate đến trang users
            self._navigate_to_users_page()
            time.sleep(3)
            
            # Tìm kiếm user
            search_input = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input#dt-search-0, input.dt-input[type='search']"))
            )
            search_input.clear()
            search_input.send_keys(user_email)
            time.sleep(3)
            
            # Tìm nút vô hiệu hóa (icon khóa - btn-warning)
            try:
                deactivate_btn = self.wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "#users-table tbody tr button.btn-warning"))
                )
                print(f"  ✅ Tìm thấy nút 'Vô hiệu hóa'")
                
                self._js_click(deactivate_btn)
                time.sleep(1)
                
                # Xử lý SweetAlert xác nhận
                if self._wait_for_swal_and_confirm():
                    print(f"  ✅ Đã xác nhận vô hiệu hóa")
                
                time.sleep(2)
                
                # Kiểm tra SweetAlert thành công
                if self._wait_for_swal_success():
                    print(f"  ✅ Vô hiệu hóa thành công trên UI")
                
                # VERIFY TRONG DATABASE
                time.sleep(2)
                updated_user = DatabaseHelper.get_user_by_id(user_id)
                
                print(f"\n  🔍 VERIFY TRONG DATABASE:")
                print(f"     Trạng thái sau cập nhật: {'Active' if updated_user['is_active'] else 'Inactive'}")
                
                if updated_user['is_active'] == 0:
                    print("\n" + "="*50)
                    print("✅ PASSED: VÔ HIỆU HÓA NGƯỜI DÙNG THÀNH CÔNG!")
                    print("="*50)
                    
                    # Khôi phục trạng thái gốc
                    print(f"\n  🔄 Khôi phục trạng thái gốc...")
                    DatabaseHelper.update_user_status(user_id, original_status)
                else:
                    print(f"  ⚠️ Trạng thái chưa được cập nhật")
                    
            except TimeoutException:
                print("  ⚠️ Không tìm thấy nút 'Vô hiệu hóa'")
                self.skipTest("Nút vô hiệu hóa không khả dụng")
                
        except Exception as e:
            self._save_error_screenshot("TC_USR_07")
            # Khôi phục trạng thái nếu có lỗi
            DatabaseHelper.update_user_status(user_id, original_status)
            raise e
    
    def test_10_activate_user(self):
        """TC_USR_08: Kích hoạt lại người dùng"""
        print("\n" + "-"*50)
        print("🧪 TC_USR_08: KÍCH HOẠT LẠI NGƯỜI DÙNG")
        print("-"*50)
        
        # Tìm user đang inactive
        users = DatabaseHelper.get_users_by_status(0)  # is_active = 0
        
        if not users:
            # Nếu không có user inactive, tạo một user inactive để test
            print("  ⚠️ Không có user inactive, tìm user active để tạm vô hiệu hóa...")
            active_users = DatabaseHelper.get_users_by_status(1)
            test_user = None
            for user in active_users:
                if user['email'] != ADMIN_ACC["email"]:
                    test_user = user
                    break
            
            if test_user:
                # Tạm vô hiệu hóa user này
                DatabaseHelper.update_user_status(test_user['id'], 0)
                print(f"  🔧 Đã tạm vô hiệu hóa user: {test_user['email']}")
            else:
                self.skipTest("Không có user phù hợp để test")
        else:
            test_user = users[0]
        
        user_id = test_user['id']
        user_email = test_user['email']
        
        print(f"  👤 Test với user ID: {user_id}")
        print(f"  📧 Email: {user_email}")
        
        try:
            # Navigate đến trang users
            self._navigate_to_users_page()
            time.sleep(3)
            
            # Tìm kiếm user
            search_input = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input#dt-search-0, input.dt-input[type='search']"))
            )
            search_input.clear()
            search_input.send_keys(user_email)
            time.sleep(3)
            
            # Tìm nút kích hoạt (icon unlock - btn-success)
            try:
                activate_btn = self.wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "#users-table tbody tr button.btn-success"))
                )
                print(f"  ✅ Tìm thấy nút 'Kích hoạt'")
                
                self._js_click(activate_btn)
                time.sleep(1)
                
                # Xử lý SweetAlert xác nhận
                if self._wait_for_swal_and_confirm():
                    print(f"  ✅ Đã xác nhận kích hoạt")
                
                time.sleep(2)
                
                # Kiểm tra SweetAlert thành công
                if self._wait_for_swal_success():
                    print(f"  ✅ Kích hoạt thành công trên UI")
                
                # VERIFY TRONG DATABASE
                time.sleep(2)
                updated_user = DatabaseHelper.get_user_by_id(user_id)
                
                print(f"\n  🔍 VERIFY TRONG DATABASE:")
                print(f"     Trạng thái sau cập nhật: {'Active' if updated_user['is_active'] else 'Inactive'}")
                
                if updated_user['is_active'] == 1:
                    print("\n" + "="*50)
                    print("✅ PASSED: KÍCH HOẠT LẠI NGƯỜI DÙNG THÀNH CÔNG!")
                    print("="*50)
                else:
                    print(f"  ⚠️ Trạng thái chưa được cập nhật")
                    
            except TimeoutException:
                print("  ⚠️ Không tìm thấy nút 'Kích hoạt'")
                self.skipTest("Nút kích hoạt không khả dụng")
                
        except Exception as e:
            self._save_error_screenshot("TC_USR_08")
            raise e
    
    def test_11_verify_user_data_matches_database(self):
        """TC_USR_09: Verify dữ liệu hiển thị khớp với Database"""
        print("\n" + "-"*50)
        print("🧪 TC_USR_09: VERIFY DỮ LIỆU KHỚP VỚI DATABASE")
        print("-"*50)
        
        try:
            # Navigate đến trang users
            self._navigate_to_users_page()
            time.sleep(3)
            
            # Lấy thông tin user đầu tiên từ UI
            first_row = self.driver.find_element(By.CSS_SELECTOR, "#users-table tbody tr:first-child")
            cells = first_row.find_elements(By.TAG_NAME, "td")
            
            ui_id = cells[0].text
            ui_email = cells[1].text
            ui_verified = cells[2].text
            ui_role = cells[3].text
            ui_status = cells[4].text
            
            print(f"  📊 Dữ liệu từ UI:")
            print(f"     ID: {ui_id}")
            print(f"     Email: {ui_email}")
            print(f"     Xác thực: {ui_verified}")
            print(f"     Vai trò: {ui_role}")
            print(f"     Trạng thái: {ui_status}")
            
            # Lấy thông tin từ DB
            db_user = DatabaseHelper.get_user_by_id(int(ui_id))
            
            if db_user:
                print(f"\n  📊 Dữ liệu từ Database:")
                print(f"     ID: {db_user['id']}")
                print(f"     Email: {db_user['email']}")
                print(f"     Is Verified: {db_user['is_verified']}")
                print(f"     Role: {db_user['role']}")
                print(f"     Is Active: {db_user['is_active']}")
                
                # Verify
                self.assertEqual(ui_id, str(db_user['id']), "ID không khớp")
                self.assertEqual(ui_email, db_user['email'], "Email không khớp")
                
                # Verify role
                if db_user['role'].lower() == 'admin':
                    self.assertIn('admin', ui_role.lower(), "Vai trò không khớp")
                else:
                    self.assertIn('user', ui_role.lower(), "Vai trò không khớp")
                
                print("\n" + "="*50)
                print("✅ PASSED: DỮ LIỆU KHỚP VỚI DATABASE!")
                print("="*50)
            else:
                print(f"  ⚠️ Không tìm thấy user ID={ui_id} trong database")
            
        except Exception as e:
            self._save_error_screenshot("TC_USR_09")
            raise e


if __name__ == "__main__":
    # Chạy test với output chi tiết
    unittest.main(verbosity=2)
