import unittest
import time
import os
import pymysql
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.keys import Keys

# --- CẤU HÌNH URL ---
URL_LOGIN = "https://whippet-exotic-specially.ngrok-free.app/QlyShopTheThao/src/view/login.php"
URL_ADMIN_CATEGORIES = "https://whippet-exotic-specially.ngrok-free.app/QlyShopTheThao/src/view/ViewAdmin/index.php?page=categories"

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

# Dữ liệu test danh mục - Tên unique để dễ tìm kiếm
TEST_TIMESTAMP = datetime.now().strftime("%d%m%Y_%H%M%S")
TEST_CATEGORY_NAME = f"DM_Test_Selenium_{TEST_TIMESTAMP}"
EDITED_CATEGORY_NAME = f"DM_Test_Edited_{TEST_TIMESTAMP}"


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
    def find_category_by_name(category_name):
        """Tìm danh mục theo tên trong database"""
        conn = None
        try:
            conn = DatabaseHelper.get_connection()
            with conn.cursor() as cursor:
                sql = "SELECT * FROM category WHERE name LIKE %s ORDER BY id DESC LIMIT 1"
                cursor.execute(sql, (f"%{category_name}%",))
                result = cursor.fetchone()
                return result
        except Exception as e:
            print(f"❌ Database error: {e}")
            return None
        finally:
            if conn:
                conn.close()
    
    @staticmethod
    def find_category_by_id(category_id):
        """Tìm danh mục theo ID"""
        conn = None
        try:
            conn = DatabaseHelper.get_connection()
            with conn.cursor() as cursor:
                sql = "SELECT * FROM category WHERE id = %s"
                cursor.execute(sql, (category_id,))
                result = cursor.fetchone()
                return result
        except Exception as e:
            print(f"❌ Database error: {e}")
            return None
        finally:
            if conn:
                conn.close()
    
    @staticmethod
    def get_category_count():
        """Đếm số danh mục trong database"""
        conn = None
        try:
            conn = DatabaseHelper.get_connection()
            with conn.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) as count FROM category")
                result = cursor.fetchone()
                return result['count'] if result else 0
        except Exception as e:
            print(f"❌ Database error: {e}")
            return 0
        finally:
            if conn:
                conn.close()
    
    @staticmethod
    def check_category_is_active(category_id):
        """Kiểm tra trạng thái is_active của danh mục"""
        conn = None
        try:
            conn = DatabaseHelper.get_connection()
            with conn.cursor() as cursor:
                cursor.execute("SELECT is_active FROM category WHERE id = %s", (category_id,))
                result = cursor.fetchone()
                if result:
                    is_active = result['is_active']
                    # Chuyển đổi bytes sang int nếu cần
                    if isinstance(is_active, bytes):
                        is_active = int.from_bytes(is_active, byteorder='little')
                    return int(is_active)
                return None
        except Exception as e:
            print(f"❌ Database error: {e}")
            return None
        finally:
            if conn:
                conn.close()
    
    @staticmethod
    def check_products_status_by_category(category_id):
        """Kiểm tra trạng thái is_active của các sản phẩm thuộc danh mục"""
        conn = None
        try:
            conn = DatabaseHelper.get_connection()
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT id, name, is_active 
                    FROM product 
                    WHERE category_id = %s
                """, (category_id,))
                products = cursor.fetchall()
                # Chuyển đổi bytes sang int cho is_active
                for product in products:
                    if isinstance(product['is_active'], bytes):
                        product['is_active'] = int.from_bytes(product['is_active'], byteorder='little')
                return products
        except Exception as e:
            print(f"❌ Database error: {e}")
            return []
        finally:
            if conn:
                conn.close()
    
    @staticmethod
    def delete_test_category_by_name(name_pattern):
        """Xóa danh mục test theo tên (hard delete cho cleanup)"""
        conn = None
        try:
            conn = DatabaseHelper.get_connection()
            with conn.cursor() as cursor:
                # Tìm và xóa danh mục test
                cursor.execute("DELETE FROM category WHERE name LIKE %s", (f"%{name_pattern}%",))
                deleted_count = cursor.rowcount
                conn.commit()
                return deleted_count
        except Exception as e:
            print(f"❌ Database error khi xóa danh mục test: {e}")
            return 0
        finally:
            if conn:
                conn.close()
    
    @staticmethod
    def restore_category_status(category_id, is_active=1):
        """Khôi phục trạng thái danh mục"""
        conn = None
        try:
            conn = DatabaseHelper.get_connection()
            with conn.cursor() as cursor:
                cursor.execute(
                    "UPDATE category SET is_active = %s WHERE id = %s",
                    (is_active, category_id)
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
    def create_test_products_for_category(category_id, count=2):
        """Tạo sản phẩm test cho danh mục để kiểm tra soft delete"""
        conn = None
        created_ids = []
        try:
            conn = DatabaseHelper.get_connection()
            with conn.cursor() as cursor:
                for i in range(count):
                    product_name = f"SP_Test_Category_{category_id}_{TEST_TIMESTAMP}_{i+1}"
                    cursor.execute("""
                        INSERT INTO product (name, price, stock, category_id, is_active, description)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (product_name, 100000, 10, category_id, 1, f"Sản phẩm test cho danh mục {category_id}"))
                    created_ids.append(cursor.lastrowid)
                conn.commit()
                print(f"  ✅ Đã tạo {count} sản phẩm test cho danh mục ID={category_id}")
                return created_ids
        except Exception as e:
            print(f"❌ Database error khi tạo sản phẩm test: {e}")
            return []
        finally:
            if conn:
                conn.close()
    
    @staticmethod
    def delete_test_products(product_ids):
        """Xóa sản phẩm test (hard delete)"""
        if not product_ids:
            return 0
        conn = None
        try:
            conn = DatabaseHelper.get_connection()
            with conn.cursor() as cursor:
                # Xóa ảnh sản phẩm trước (nếu có)
                placeholders = ','.join(['%s'] * len(product_ids))
                cursor.execute(f"DELETE FROM product_image WHERE product_id IN ({placeholders})", product_ids)
                # Xóa sản phẩm
                cursor.execute(f"DELETE FROM product WHERE id IN ({placeholders})", product_ids)
                deleted_count = cursor.rowcount
                conn.commit()
                return deleted_count
        except Exception as e:
            print(f"❌ Database error khi xóa sản phẩm test: {e}")
            return 0
        finally:
            if conn:
                conn.close()
    
    @staticmethod
    def delete_test_products_by_name(name_pattern):
        """Xóa sản phẩm test theo tên (hard delete)"""
        conn = None
        try:
            conn = DatabaseHelper.get_connection()
            with conn.cursor() as cursor:
                # Tìm ID sản phẩm test
                cursor.execute("SELECT id FROM product WHERE name LIKE %s", (f"%{name_pattern}%",))
                products = cursor.fetchall()
                if not products:
                    return 0
                
                product_ids = [p['id'] for p in products]
                placeholders = ','.join(['%s'] * len(product_ids))
                
                # Xóa ảnh sản phẩm trước
                cursor.execute(f"DELETE FROM product_image WHERE product_id IN ({placeholders})", product_ids)
                # Xóa sản phẩm
                cursor.execute(f"DELETE FROM product WHERE id IN ({placeholders})", product_ids)
                deleted_count = cursor.rowcount
                conn.commit()
                return deleted_count
        except Exception as e:
            print(f"❌ Database error khi xóa sản phẩm test: {e}")
            return 0
        finally:
            if conn:
                conn.close()
    
    @staticmethod
    def restore_products_status(product_ids, is_active=1):
        """Khôi phục trạng thái sản phẩm"""
        if not product_ids:
            return False
        conn = None
        try:
            conn = DatabaseHelper.get_connection()
            with conn.cursor() as cursor:
                placeholders = ','.join(['%s'] * len(product_ids))
                cursor.execute(f"UPDATE product SET is_active = %s WHERE id IN ({placeholders})", 
                             [is_active] + product_ids)
                conn.commit()
                return True
        except Exception as e:
            print(f"❌ Database error: {e}")
            return False
        finally:
            if conn:
                conn.close()


class AdminCategoryCRUDTest(unittest.TestCase):
    """
    Test Suite: Kiểm thử CRUD Danh mục Admin với Database Verification
    
    Test Cases:
    - TC_CAT_DB01: Kiểm tra kết nối Database
    - TC_CAT_DB02: Kiểm tra bảng category tồn tại
    - TC_CAT_CRUD01: Thêm danh mục mới và verify trong Database
    - TC_CAT_CRUD02: Sửa danh mục và verify trong Database
    - TC_CAT_CRUD03: Xóa mềm danh mục và verify trong Database
    - TC_CAT_CRUD04: Verify sản phẩm liên quan bị ẩn khi xóa danh mục
    """
    
    driver = None
    wait = None
    created_category_id = None  # Lưu ID danh mục đã tạo để dùng cho các test sau
    test_product_ids = []  # Lưu ID sản phẩm test đã tạo để cleanup
    
    @classmethod
    def setUpClass(cls):
        """Khởi tạo WebDriver và đăng nhập Admin"""
        print("\n" + "="*60)
        print("🧪 BẮT ĐẦU TEST CRUD DANH MỤC VỚI DATABASE")
        print(f"📝 Tên danh mục test: {TEST_CATEGORY_NAME}")
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
        
        # Xóa sản phẩm test đã tạo
        deleted_products = DatabaseHelper.delete_test_products_by_name("SP_Test_Category_")
        print(f"  🗑️ Đã xóa {deleted_products} sản phẩm test khỏi database")
        
        # Xóa danh mục test đã tạo
        deleted_categories = DatabaseHelper.delete_test_category_by_name("DM_Test_")
        print(f"  🗑️ Đã xóa {deleted_categories} danh mục test khỏi database")
        
        print("✅ Hoàn tất cleanup!")
        
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
    
    def _navigate_to_categories_page(self):
        """Navigate đến trang quản lý danh mục"""
        self.driver.get(URL_ADMIN_CATEGORIES)
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
        
        # Chờ bảng danh mục load
        self.wait.until(EC.presence_of_element_located((By.ID, "categoriesTable")))
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
            f"error_category_{test_name}_{timestamp}.png"
        )
        os.makedirs(os.path.dirname(screenshot_path), exist_ok=True)
        self.driver.save_screenshot(screenshot_path)
        print(f"📸 Screenshot saved: {screenshot_path}")
    
    # ==================== TEST CASES ====================
    
    def test_01_database_connection(self):
        """TC_CAT_DB01: Kiểm tra kết nối Database"""
        print("\n" + "-"*50)
        print("🧪 TC_CAT_DB01: Kiểm tra kết nối Database")
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
    
    def test_02_database_category_table_exists(self):
        """TC_CAT_DB02: Kiểm tra bảng category tồn tại"""
        print("\n" + "-"*50)
        print("🧪 TC_CAT_DB02: Kiểm tra bảng category tồn tại")
        print("-"*50)
        
        try:
            conn = DatabaseHelper.get_connection()
            with conn.cursor() as cursor:
                cursor.execute("SHOW TABLES LIKE 'category'")
                result = cursor.fetchone()
                self.assertIsNotNone(result, "Bảng 'category' không tồn tại")
                
                # Kiểm tra các cột cần thiết
                cursor.execute("DESCRIBE category")
                columns = [row['Field'] for row in cursor.fetchall()]
                
                required_columns = ['id', 'name', 'description', 'is_active']
                for col in required_columns:
                    self.assertIn(col, columns, f"Thiếu cột '{col}' trong bảng category")
                
                print(f"  📋 Các cột trong bảng: {columns}")
            
            conn.close()
            print("✅ PASSED: Bảng category tồn tại!")
            
        except Exception as e:
            self.fail(f"Lỗi kiểm tra bảng: {e}")
    
    def test_03_add_category_success(self):
        """TC_CAT_CRUD01: Thêm danh mục mới và verify trong Database"""
        print("\n" + "-"*50)
        print("🧪 TC_CAT_CRUD01: THÊM DANH MỤC MỚI")
        print(f"   Tên DM: {TEST_CATEGORY_NAME}")
        print("-"*50)
        
        driver = self.driver
        
        # Đếm số danh mục trước khi thêm
        count_before = DatabaseHelper.get_category_count()
        print(f"  📊 Số danh mục trong DB trước khi thêm: {count_before}")
        
        try:
            # Navigate đến trang categories
            self._navigate_to_categories_page()
            
            # Click nút "Thêm Danh Mục Mới"
            add_btn = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-bs-target='#addCategoryModal']"))
            )
            self._js_click(add_btn)
            
            # Chờ modal mở
            self.wait.until(EC.visibility_of_element_located((By.ID, "addCategoryModal")))
            time.sleep(1)
            
            # Điền thông tin danh mục
            name_input = driver.find_element(By.ID, "newCategoryName")
            name_input.clear()
            name_input.send_keys(TEST_CATEGORY_NAME)
            
            desc_input = driver.find_element(By.ID, "newCategoryDescription")
            desc_input.clear()
            desc_input.send_keys(f"Mô tả test cho danh mục {TEST_CATEGORY_NAME}")
            
            # Checkbox trạng thái (mặc định đã checked)
            status_checkbox = driver.find_element(By.ID, "newCategoryStatus")
            if not status_checkbox.is_selected():
                self._js_click(status_checkbox)
            
            print(f"  📝 Đã điền thông tin danh mục")
            
            # Click nút Lưu
            save_btn = driver.find_element(By.ID, "saveNewCategoryBtn")
            self._js_click(save_btn)
            time.sleep(2)
            
            # Xử lý SweetAlert xác nhận thêm
            try:
                swal_confirm = WebDriverWait(driver, 5).until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, ".swal2-confirm"))
                )
                self._js_click(swal_confirm)
                print("  ✅ Đã click xác nhận thêm")
                time.sleep(3)
            except:
                print("  ⚠️ Không có SweetAlert xác nhận")
            
            # Chờ SweetAlert thành công
            try:
                swal_success = WebDriverWait(driver, 10).until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, ".swal2-success"))
                )
                print("  ✅ Hiển thị thông báo thành công")
                
                # Đóng SweetAlert
                swal_ok = driver.find_element(By.CSS_SELECTOR, ".swal2-confirm")
                self._js_click(swal_ok)
                time.sleep(1)
            except:
                print("  ⚠️ Không thấy SweetAlert thành công")
            
            # VERIFY TRONG DATABASE
            print("\n  🔍 VERIFY TRONG DATABASE:")
            time.sleep(2)  # Chờ DB cập nhật
            
            category_in_db = DatabaseHelper.find_category_by_name(TEST_CATEGORY_NAME)
            
            if category_in_db:
                AdminCategoryCRUDTest.created_category_id = category_in_db['id']
                print(f"  ✅ Tìm thấy danh mục trong database:")
                print(f"     - ID: {category_in_db['id']}")
                print(f"     - Tên: {category_in_db['name']}")
                print(f"     - Mô tả: {category_in_db.get('description', 'N/A')}")
                print(f"     - Trạng thái: {'Hoạt động' if category_in_db.get('is_active') else 'Không hoạt động'}")
                
                # Verify số lượng tăng lên
                count_after = DatabaseHelper.get_category_count()
                print(f"  📊 Số danh mục sau khi thêm: {count_after}")
                
                self.assertEqual(count_after, count_before + 1, "Số danh mục không tăng sau khi thêm")
                
                print("\n" + "="*50)
                print("✅ PASSED: DANH MỤC ĐÃ ĐƯỢC THÊM VÀO DATABASE!")
                print("="*50)
            else:
                self._save_error_screenshot("TC_CAT_CRUD01_add")
                self.fail("Không tìm thấy danh mục trong database sau khi thêm")
                
        except Exception as e:
            self._save_error_screenshot("TC_CAT_CRUD01_add")
            raise e
    
    def test_04_edit_category_success(self):
        """TC_CAT_CRUD02: Sửa danh mục và verify trong Database"""
        print("\n" + "-"*50)
        print("🧪 TC_CAT_CRUD02: SỬA DANH MỤC")
        print("-"*50)
        
        driver = self.driver
        
        # Lấy danh mục để test (ưu tiên danh mục vừa tạo, nếu không có thì lấy danh mục có sẵn)
        category_id = None
        original_name = None
        original_description = None
        original_status = None
        
        if AdminCategoryCRUDTest.created_category_id:
            category_id = AdminCategoryCRUDTest.created_category_id
        else:
            # Lấy danh mục có is_active = 1 đầu tiên để test
            conn = DatabaseHelper.get_connection()
            try:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT id, name, description, is_active FROM category WHERE is_active = 1 ORDER BY id ASC LIMIT 1")
                    category = cursor.fetchone()
                    if category:
                        category_id = category['id']
                        original_name = category['name']
                        original_description = category['description']
                        original_status = category['is_active']
                        print(f"  📦 Sử dụng danh mục có sẵn: ID={category_id}, Tên={original_name}")
            finally:
                conn.close()
        
        if not category_id:
            self.skipTest("Không có danh mục nào trong database để test")
        
        print(f"  📦 Sửa danh mục ID: {category_id}")
        
        try:
            # Navigate đến trang categories
            self._navigate_to_categories_page()
            
            # Lấy thông tin danh mục trước khi sửa
            category_before = DatabaseHelper.find_category_by_id(category_id)
            original_name = category_before['name']
            original_description = category_before.get('description', '')
            original_status = category_before.get('is_active', 1)
            print(f"  📝 Tên trước khi sửa: {original_name}")
            print(f"  📝 Mô tả trước khi sửa: {original_description}")
            
            # Tìm và click nút sửa của danh mục
            # Chờ DataTable load xong
            time.sleep(2)
            
            edit_btn = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, f"button.edit-category-btn[data-id='{category_id}']"))
            )
            self._scroll_to_element(edit_btn)
            self._js_click(edit_btn)
            
            # Chờ modal mở
            self.wait.until(EC.visibility_of_element_located((By.ID, "editCategoryModal")))
            time.sleep(1)
            
            # Chờ input name có value
            name_input = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.ID, "editCategoryName"))
            )
            WebDriverWait(driver, 10).until(
                lambda d: name_input.get_attribute("value") != ""
            )
            
            # Tạo tên và mô tả mới để test
            test_suffix = " - EDITED_" + TEST_TIMESTAMP
            new_name = original_name + test_suffix
            new_description = "Mô tả đã sửa - " + TEST_TIMESTAMP
            
            # Sửa tên danh mục
            driver.execute_script("arguments[0].value = ''; arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", name_input)
            time.sleep(0.5)
            name_input.send_keys(new_name)
            driver.execute_script("arguments[0].dispatchEvent(new Event('change', { bubbles: true }));", name_input)
            time.sleep(0.5)
            
            # Sửa mô tả
            desc_input = driver.find_element(By.ID, "editCategoryDescription")
            driver.execute_script("arguments[0].value = ''; arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", desc_input)
            time.sleep(0.5)
            desc_input.send_keys(new_description)
            driver.execute_script("arguments[0].dispatchEvent(new Event('change', { bubbles: true }));", desc_input)
            time.sleep(0.5)
            
            print(f"  📝 Tên mới: {new_name}")
            print(f"  📝 Mô tả mới: {new_description}")
            
            # Click nút Lưu thay đổi
            save_btn = driver.find_element(By.ID, "saveCategoryChangesBtn")
            
            # Chờ nút enable (phát hiện thay đổi)
            try:
                WebDriverWait(driver, 5).until(
                    lambda d: not save_btn.get_attribute("disabled")
                )
                print("  ✅ Nút Lưu đã enable")
            except:
                print("  ⚠️ Nút Lưu vẫn disabled, thử click anyway...")
            
            self._js_click(save_btn)
            print("  ✅ Đã click nút Lưu thay đổi")
            time.sleep(2)
            
            # Xử lý SweetAlert xác nhận
            try:
                swal_confirm = WebDriverWait(driver, 5).until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, ".swal2-confirm"))
                )
                print("  ✅ SweetAlert xác nhận xuất hiện")
                self._js_click(swal_confirm)
                print("  ✅ Đã click xác nhận lưu")
                time.sleep(3)
            except:
                print("  ⚠️ Không có SweetAlert xác nhận")
            
            # Chờ SweetAlert thành công
            try:
                swal_success = WebDriverWait(driver, 10).until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, ".swal2-success"))
                )
                print("  ✅ Hiển thị thông báo thành công")
                
                # Đóng SweetAlert
                swal_ok = driver.find_element(By.CSS_SELECTOR, ".swal2-confirm")
                self._js_click(swal_ok)
                time.sleep(1)
            except:
                print("  ⚠️ Không thấy SweetAlert thành công")
            
            # Chờ modal đóng
            try:
                WebDriverWait(driver, 10).until(
                    EC.invisibility_of_element_located((By.ID, "editCategoryModal"))
                )
                print("  ✅ Modal đã đóng")
            except:
                print("  ⚠️ Modal vẫn mở")
            
            # Chờ DB cập nhật
            time.sleep(2)
            
            # VERIFY TRONG DATABASE
            print("\n  🔍 VERIFY TRONG DATABASE:")
            category_after = DatabaseHelper.find_category_by_id(category_id)
            
            if category_after:
                print(f"  ✅ Danh mục sau khi sửa:")
                print(f"     - ID: {category_after['id']}")
                print(f"     - Tên: {category_after['name']}")
                print(f"     - Mô tả: {category_after.get('description', 'N/A')}")
                
                # Verify tên đã được cập nhật
                name_updated = test_suffix in str(category_after['name'])
                
                if name_updated:
                    print("\n" + "="*50)
                    print("✅ PASSED: DANH MỤC ĐÃ ĐƯỢC CẬP NHẬT TRONG DATABASE!")
                    print("="*50)
                    
                    # Khôi phục lại tên và mô tả gốc
                    print("\n  🔄 Khôi phục dữ liệu gốc...")
                    conn = DatabaseHelper.get_connection()
                    try:
                        with conn.cursor() as cursor:
                            cursor.execute(
                                "UPDATE category SET name = %s, description = %s WHERE id = %s",
                                (original_name, original_description, category_id)
                            )
                            conn.commit()
                            print(f"  ✅ Đã khôi phục: Tên={original_name}")
                    finally:
                        conn.close()
                else:
                    print(f"  ⚠️ Dữ liệu chưa được cập nhật đúng")
                    print(f"     Expected name contains: {test_suffix}")
                    print(f"     Actual name: {category_after['name']}")
                    self.fail("Dữ liệu không được cập nhật trong database")
            else:
                self.fail("Không tìm thấy danh mục sau khi sửa")
                
        except Exception as e:
            self._save_error_screenshot("TC_CAT_CRUD02_edit")
            raise e
    
    def test_05_delete_category_success(self):
        """TC_CAT_CRUD03: Xóa mềm danh mục và verify trong Database"""
        print("\n" + "-"*50)
        print("🧪 TC_CAT_CRUD03: XÓA MỀM DANH MỤC")
        print("-"*50)
        
        driver = self.driver
        
        # Tìm danh mục để test xóa
        category_id = None
        category_name = None
        
        # Ưu tiên dùng danh mục test đã tạo
        if AdminCategoryCRUDTest.created_category_id:
            category_id = AdminCategoryCRUDTest.created_category_id
            category = DatabaseHelper.find_category_by_id(category_id)
            if category:
                category_name = category['name']
        else:
            # Tìm danh mục có is_active = 1 để test
            conn = DatabaseHelper.get_connection()
            try:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        SELECT id, name FROM category 
                        WHERE is_active = 1 
                        AND name LIKE '%Test%'
                        ORDER BY id DESC LIMIT 1
                    """)
                    category = cursor.fetchone()
                    if category:
                        category_id = category['id']
                        category_name = category['name']
            finally:
                conn.close()
        
        if not category_id:
            self.skipTest("Không có danh mục test nào để xóa")
        
        print(f"  📦 Xóa mềm danh mục: ID={category_id}, Tên={category_name}")
        
        # Kiểm tra trạng thái trước khi xóa
        status_before = DatabaseHelper.check_category_is_active(category_id)
        print(f"  📊 Trạng thái danh mục trước khi xóa: is_active = {status_before}")
        
        # Nếu đã bị xóa mềm rồi, khôi phục trước
        if status_before == 0:
            print("  🔄 Danh mục đã bị ẩn, khôi phục trước...")
            DatabaseHelper.restore_category_status(category_id, 1)
            time.sleep(1)
        
        # TẠO SẢN PHẨM TEST CHO DANH MỤC NÀY
        print("\n  📦 TẠO SẢN PHẨM TEST CHO DANH MỤC:")
        test_product_ids = DatabaseHelper.create_test_products_for_category(category_id, count=3)
        AdminCategoryCRUDTest.test_product_ids = test_product_ids  # Lưu để cleanup
        
        if test_product_ids:
            print(f"  ✅ Đã tạo {len(test_product_ids)} sản phẩm test: IDs = {test_product_ids}")
            # Kiểm tra trạng thái sản phẩm trước khi xóa danh mục
            products_before = DatabaseHelper.check_products_status_by_category(category_id)
            print(f"  📊 Sản phẩm thuộc danh mục trước khi xóa:")
            for p in products_before:
                status = "Hoạt động" if p['is_active'] == 1 else "Ẩn"
                print(f"     - ID={p['id']}: {p['name'][:40]}... - {status}")
        
        try:
            # Navigate đến trang categories
            self._navigate_to_categories_page()
            time.sleep(2)
            
            # Tìm và click nút xóa của danh mục
            delete_btn = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, f"button.delete-category-btn-table[data-id='{category_id}']"))
            )
            self._scroll_to_element(delete_btn)
            self._js_click(delete_btn)
            print("\n  ✅ Đã click nút Xóa danh mục")
            time.sleep(1)
            
            # Xử lý SweetAlert xác nhận xóa
            try:
                swal_confirm = WebDriverWait(driver, 5).until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, ".swal2-confirm"))
                )
                print("  ✅ SweetAlert xác nhận xóa xuất hiện")
                self._js_click(swal_confirm)
                print("  ✅ Đã click xác nhận xóa")
                time.sleep(3)
            except:
                print("  ⚠️ Không có SweetAlert xác nhận xóa")
            
            # Chờ SweetAlert thành công
            try:
                swal_success = WebDriverWait(driver, 10).until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, ".swal2-success"))
                )
                print("  ✅ Hiển thị thông báo xóa thành công")
                
                # Đóng SweetAlert
                swal_ok = driver.find_element(By.CSS_SELECTOR, ".swal2-confirm")
                self._js_click(swal_ok)
                time.sleep(1)
            except:
                print("  ⚠️ Không thấy SweetAlert thành công")
            
            # Chờ DB cập nhật
            time.sleep(2)
            
            # VERIFY TRONG DATABASE
            print("\n  🔍 VERIFY TRONG DATABASE:")
            status_after = DatabaseHelper.check_category_is_active(category_id)
            print(f"  📊 Trạng thái sau khi xóa: is_active = {status_after}")
            
            if status_after == 0:
                print("\n" + "="*50)
                print("✅ PASSED: DANH MỤC ĐÃ ĐƯỢC XÓA MỀM (is_active = 0)!")
                print("="*50)
            else:
                self.fail(f"Danh mục chưa được xóa mềm. is_active = {status_after}")
                
        except Exception as e:
            self._save_error_screenshot("TC_CAT_CRUD03_delete")
            raise e
    
    def test_06_verify_related_products_hidden_after_delete_category(self):
        """TC_CAT_CRUD04: Verify sản phẩm liên quan bị ẩn khi xóa danh mục"""
        print("\n" + "-"*50)
        print("🧪 TC_CAT_CRUD04: VERIFY SẢN PHẨM LIÊN QUAN BỊ ẨN")
        print("-"*50)
        
        # Lấy danh mục vừa xóa mềm
        category_id = AdminCategoryCRUDTest.created_category_id
        
        if not category_id:
            # Tìm danh mục đã bị xóa mềm
            conn = DatabaseHelper.get_connection()
            try:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        SELECT id, name FROM category 
                        WHERE is_active = 0 
                        ORDER BY id DESC LIMIT 1
                    """)
                    category = cursor.fetchone()
                    if category:
                        category_id = category['id']
                        print(f"  📦 Kiểm tra danh mục: ID={category_id}, Tên={category['name']}")
            finally:
                conn.close()
        
        if not category_id:
            self.skipTest("Không có danh mục đã xóa mềm để kiểm tra")
        
        # Kiểm tra sản phẩm liên quan
        products = DatabaseHelper.check_products_status_by_category(category_id)
        
        print(f"\n  📊 Số sản phẩm thuộc danh mục ID={category_id}: {len(products)}")
        
        if len(products) == 0:
            print("  ℹ️ Không có sản phẩm nào thuộc danh mục này")
            print("\n" + "="*50)
            print("✅ PASSED: Không có sản phẩm liên quan cần kiểm tra")
            print("="*50)
            return
        
        # Kiểm tra tất cả sản phẩm đều bị ẩn
        all_hidden = True
        for product in products:
            status = "Ẩn" if product['is_active'] == 0 else "Hiển thị"
            print(f"     - Sản phẩm ID={product['id']}: {product['name'][:30]}... - {status}")
            if product['is_active'] != 0:
                all_hidden = False
        
        if all_hidden:
            print("\n" + "="*50)
            print("✅ PASSED: TẤT CẢ SẢN PHẨM LIÊN QUAN ĐÃ BỊ ẨN!")
            print("="*50)
        else:
            self.fail("Một số sản phẩm liên quan chưa bị ẩn")


if __name__ == "__main__":
    # Chạy test với output chi tiết
    unittest.main(verbosity=2)
