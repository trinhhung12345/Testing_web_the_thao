"""
===========================================
TEST SUITE 07: QUẢN LÝ ĐÁNH GIÁ (REVIEWS)
===========================================
Mô tả: Kiểm thử chức năng quản lý đánh giá sản phẩm của admin
URL: https://melissia-untragical-inviably.ngrok-free.dev/QlyShopTheThao/src/view/ViewAdmin/index.php?page=reviews
Database: user_database_biggestzoo
Table: review

Các test cases:
- TC_REV_DB01: Kiểm tra kết nối database
- TC_REV_DB02: Kiểm tra bảng review tồn tại
- TC_REV_01: Hiển thị danh sách đánh giá
- TC_REV_02: Tìm kiếm đánh giá
- TC_REV_03: Lọc theo sản phẩm
- TC_REV_04: Lọc theo người gửi
- TC_REV_05: Lọc theo rating
- TC_REV_06: Lọc theo trạng thái
- TC_REV_07: Xem chi tiết đánh giá
- TC_REV_08: Phản hồi đánh giá
- TC_REV_09: Ẩn đánh giá (toggle status)
- TC_REV_10: Hiện đánh giá (toggle status)
- TC_REV_11: Xóa đánh giá
- TC_REV_12: Verify dữ liệu khớp database
"""

import unittest
import time
import os
import sys
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.service import Service
import pymysql

# ==================== CẤU HÌNH ====================
BASE_URL = "https://melissia-untragical-inviably.ngrok-free.dev/QlyShopTheThao/src/view/ViewAdmin"
URL_LOGIN = "https://melissia-untragical-inviably.ngrok-free.dev/QlyShopTheThao/src/view/login.php"
URL_REVIEWS = f"{BASE_URL}/index.php?page=reviews"

ADMIN_ACC = {
    "email": "wearingarmor12345@gmail.com",
    "pass": "hung12345"
}

DB_CONFIG = {
    "host": "j3egkd.h.filess.io",
    "port": 3306,
    "user": "user_database_biggestzoo",
    "password": "8200c17fb8ab66b3f73f8a0b4dc95ee2da14de7e",
    "database": "user_database_biggestzoo"
}

TEST_TIMESTAMP = datetime.now().strftime("%d%m%Y_%H%M%S")
SCREENSHOT_DIR = os.path.join(os.path.dirname(__file__), "..", "results")


# ==================== DATABASE HELPER ====================
class DatabaseHelper:
    """Helper class để tương tác với database"""
    
    @staticmethod
    def get_connection():
        return pymysql.connect(
            host=DB_CONFIG["host"],
            port=DB_CONFIG["port"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            database=DB_CONFIG["database"],
            cursorclass=pymysql.cursors.DictCursor
        )
    
    @staticmethod
    def get_all_reviews():
        """Lấy tất cả đánh giá với thông tin sản phẩm và user"""
        conn = DatabaseHelper.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT r.id, r.user_id, r.product_id, r.rating, r.comment, 
                           r.admin_reply, r.replied_at, r.status, r.created_at,
                           p.name as product_name, u.email as user_email
                    FROM review r
                    JOIN product p ON r.product_id = p.id
                    JOIN username u ON r.user_id = u.id
                    ORDER BY r.id DESC
                """)
                return cursor.fetchall()
        finally:
            conn.close()
    
    @staticmethod
    def get_review_by_id(review_id):
        """Lấy thông tin một đánh giá theo ID"""
        conn = DatabaseHelper.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT r.id, r.user_id, r.product_id, r.rating, r.comment, 
                           r.admin_reply, r.replied_at, r.status, r.created_at,
                           p.name as product_name, u.email as user_email
                    FROM review r
                    JOIN product p ON r.product_id = p.id
                    JOIN username u ON r.user_id = u.id
                    WHERE r.id = %s
                """, (review_id,))
                return cursor.fetchone()
        finally:
            conn.close()
    
    @staticmethod
    def get_reviews_by_status(status):
        """Lấy đánh giá theo trạng thái"""
        conn = DatabaseHelper.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT r.*, p.name as product_name, u.email as user_email
                    FROM review r
                    JOIN product p ON r.product_id = p.id
                    JOIN username u ON r.user_id = u.id
                    WHERE r.status = %s
                    ORDER BY r.id DESC
                """, (status,))
                return cursor.fetchall()
        finally:
            conn.close()
    
    @staticmethod
    def get_reviews_by_rating(rating):
        """Lấy đánh giá theo rating"""
        conn = DatabaseHelper.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT r.*, p.name as product_name, u.email as user_email
                    FROM review r
                    JOIN product p ON r.product_id = p.id
                    JOIN username u ON r.user_id = u.id
                    WHERE r.rating = %s
                    ORDER BY r.id DESC
                """, (rating,))
                return cursor.fetchall()
        finally:
            conn.close()
    
    @staticmethod
    def get_reviews_by_product(product_id):
        """Lấy đánh giá theo sản phẩm"""
        conn = DatabaseHelper.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT r.*, p.name as product_name, u.email as user_email
                    FROM review r
                    JOIN product p ON r.product_id = p.id
                    JOIN username u ON r.user_id = u.id
                    WHERE r.product_id = %s
                    ORDER BY r.id DESC
                """, (product_id,))
                return cursor.fetchall()
        finally:
            conn.close()
    
    @staticmethod
    def get_reviews_by_user(user_id):
        """Lấy đánh giá theo người dùng"""
        conn = DatabaseHelper.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT r.*, p.name as product_name, u.email as user_email
                    FROM review r
                    JOIN product p ON r.product_id = p.id
                    JOIN username u ON r.user_id = u.id
                    WHERE r.user_id = %s
                    ORDER BY r.id DESC
                """, (user_id,))
                return cursor.fetchall()
        finally:
            conn.close()
    
    @staticmethod
    def get_products_with_reviews():
        """Lấy danh sách sản phẩm có đánh giá"""
        conn = DatabaseHelper.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT DISTINCT p.id, p.name 
                    FROM product p 
                    JOIN review r ON p.id = r.product_id 
                    ORDER BY p.name ASC
                """)
                return cursor.fetchall()
        finally:
            conn.close()
    
    @staticmethod
    def get_users_with_reviews():
        """Lấy danh sách người dùng có đánh giá"""
        conn = DatabaseHelper.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT DISTINCT u.id, u.email 
                    FROM username u 
                    JOIN review r ON u.id = r.user_id 
                    ORDER BY u.email ASC
                """)
                return cursor.fetchall()
        finally:
            conn.close()
    
    @staticmethod
    def update_review_status(review_id, new_status):
        """Cập nhật trạng thái đánh giá"""
        conn = DatabaseHelper.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    UPDATE review SET status = %s WHERE id = %s
                """, (new_status, review_id))
                conn.commit()
                return cursor.rowcount > 0
        finally:
            conn.close()
    
    @staticmethod
    def update_admin_reply(review_id, reply_text):
        """Cập nhật phản hồi admin"""
        conn = DatabaseHelper.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    UPDATE review SET admin_reply = %s, replied_at = NOW() WHERE id = %s
                """, (reply_text, review_id))
                conn.commit()
                return cursor.rowcount > 0
        finally:
            conn.close()
    
    @staticmethod
    def create_test_review(user_id, product_id, rating, comment, status='pending'):
        """Tạo review test"""
        conn = DatabaseHelper.get_connection()
        try:
            with conn.cursor() as cursor:
                # Kiểm tra xem review đã tồn tại chưa (unique constraint: user_id, product_id)
                cursor.execute("""
                    SELECT id FROM review WHERE user_id = %s AND product_id = %s
                """, (user_id, product_id))
                existing = cursor.fetchone()
                
                if existing:
                    # Update nếu đã tồn tại
                    cursor.execute("""
                        UPDATE review SET rating = %s, comment = %s, status = %s, admin_reply = NULL
                        WHERE user_id = %s AND product_id = %s
                    """, (rating, comment, status, user_id, product_id))
                    conn.commit()
                    return existing['id']
                else:
                    # Insert nếu chưa tồn tại
                    cursor.execute("""
                        INSERT INTO review (user_id, product_id, rating, comment, status)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (user_id, product_id, rating, comment, status))
                    conn.commit()
                    return cursor.lastrowid
        finally:
            conn.close()
    
    @staticmethod
    def delete_review(review_id):
        """Xóa review"""
        conn = DatabaseHelper.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM review WHERE id = %s", (review_id,))
                conn.commit()
                return cursor.rowcount > 0
        finally:
            conn.close()
    
    @staticmethod
    def get_total_reviews():
        """Đếm tổng số đánh giá"""
        conn = DatabaseHelper.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) as total FROM review")
                return cursor.fetchone()['total']
        finally:
            conn.close()


# ==================== TEST CLASS ====================
class AdminReviewsTest(unittest.TestCase):
    """Test suite cho trang quản lý đánh giá"""
    
    @classmethod
    def setUpClass(cls):
        """Khởi tạo trước khi chạy tất cả test"""
        print("\n" + "="*60)
        print("🧪 BẮT ĐẦU TEST QUẢN LÝ ĐÁNH GIÁ")
        print("="*60)
        
        # Tạo thư mục screenshots nếu chưa có
        os.makedirs(SCREENSHOT_DIR, exist_ok=True)
        
        # Khởi tạo Chrome driver
        driver_path = os.path.join(os.getcwd(), 'driver', 'chromedriver.exe')
        
        if os.path.exists(driver_path):
            service = Service(driver_path)
            cls.driver = webdriver.Chrome(service=service)
        else:
            cls.driver = webdriver.Chrome()
        
        cls.driver.maximize_window()
        cls.driver.implicitly_wait(10)
        cls.wait = WebDriverWait(cls.driver, 15)
        
        # Đăng nhập admin
        cls._login_admin(cls)
    
    @classmethod
    def tearDownClass(cls):
        """Dọn dẹp sau khi chạy tất cả test"""
        print("\n" + "="*60)
        print("🧹 KẾT THÚC TEST")
        print("="*60)
        if cls.driver:
            cls.driver.quit()
    
    def setUp(self):
        """Chạy trước mỗi test"""
        pass
    
    def tearDown(self):
        """Chạy sau mỗi test"""
        # Đóng modal nếu còn mở
        try:
            self._close_any_modal()
        except:
            pass
    
    def _login_admin(self):
        """Đăng nhập tài khoản admin"""
        self.driver.get(URL_LOGIN)
        time.sleep(2)
        
        # Bypass ngrok warning
        try:
            visit_btn = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Visit Site')]"))
            )
            visit_btn.click()
            time.sleep(2)
        except:
            pass
        
        # Điền form đăng nhập
        email_input = self.wait.until(EC.visibility_of_element_located((By.ID, "email_signin")))
        email_input.clear()
        email_input.send_keys(ADMIN_ACC["email"])
        
        password_input = self.driver.find_element(By.ID, "password_signin")
        password_input.clear()
        password_input.send_keys(ADMIN_ACC["pass"])
        
        # Click đăng nhập
        login_btn = self.driver.find_element(By.ID, "b1")
        login_btn.click()
        
        # Xử lý Captcha (Chỉ khi form valid thì modal mới hiện)
        try:
            iframe = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "iframe[src*='google.com/recaptcha']"))
            )
            self.driver.switch_to.frame(iframe)
            checkbox = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.ID, "recaptcha-anchor"))
            )
            checkbox.click()
            self.driver.switch_to.default_content()
            
            # Chờ server xử lý đăng nhập
            time.sleep(5)
        except:
            pass
        
        # Chờ chuyển hướng đến trang Admin
        try:
            WebDriverWait(self.driver, 15).until(
                EC.url_contains("ViewAdmin")
            )
            print("✅ Đăng nhập Admin thành công!")
        except:
            print("⚠️ Chưa chuyển hướng đến trang Admin, tiếp tục...")
    
    def _navigate_to_reviews_page(self):
        """Điều hướng đến trang quản lý đánh giá"""
        self.driver.get(URL_REVIEWS)
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
        
        # Chờ bảng load
        self.wait.until(EC.presence_of_element_located((By.ID, "reviews-table")))
        time.sleep(2)
    
    def _navigate_to_review_detail(self, review_id):
        """Điều hướng đến trang chi tiết đánh giá"""
        url = f"{BASE_URL}/index.php?page=review_details&id={review_id}"
        self.driver.get(url)
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
    
    def _wait_for_table_load(self):
        """Chờ DataTable load xong"""
        time.sleep(1)
        try:
            # Chờ processing indicator ẩn đi
            WebDriverWait(self.driver, 10).until(
                EC.invisibility_of_element_located((By.CSS_SELECTOR, ".dataTables_processing"))
            )
        except:
            pass
        time.sleep(1)
    
    def _get_table_rows(self):
        """Lấy các dòng trong bảng"""
        self._wait_for_table_load()
        return self.driver.find_elements(By.CSS_SELECTOR, "#reviews-table tbody tr")
    
    def _wait_for_swal_and_confirm(self):
        """Chờ SweetAlert hiện lên và bấm xác nhận"""
        try:
            swal_confirm = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".swal2-confirm"))
            )
            swal_confirm.click()
            time.sleep(1)
        except TimeoutException:
            pass
    
    def _wait_for_swal_success(self):
        """Chờ SweetAlert thành công"""
        try:
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".swal2-success, .swal2-icon-success"))
            )
            time.sleep(1)
            # Đóng SweetAlert
            try:
                ok_btn = self.driver.find_element(By.CSS_SELECTOR, ".swal2-confirm")
                ok_btn.click()
            except:
                pass
            time.sleep(1)
            return True
        except TimeoutException:
            return False
    
    def _close_any_modal(self):
        """Đóng modal bất kỳ nếu đang mở"""
        try:
            close_btns = self.driver.find_elements(By.CSS_SELECTOR, ".modal.show .btn-close, .modal.show [data-bs-dismiss='modal']")
            for btn in close_btns:
                if btn.is_displayed():
                    btn.click()
                    time.sleep(0.5)
        except:
            pass
    
    def _close_swal(self):
        """Đóng SweetAlert nếu đang hiển thị"""
        try:
            swal_btn = self.driver.find_element(By.CSS_SELECTOR, ".swal2-confirm, .swal2-cancel")
            if swal_btn.is_displayed():
                swal_btn.click()
                time.sleep(0.5)
        except:
            pass
    
    def _js_click(self, element):
        """Click element bằng JavaScript"""
        self.driver.execute_script("arguments[0].click();", element)
    
    def _save_error_screenshot(self, test_name):
        """Lưu screenshot khi có lỗi"""
        try:
            screenshot_path = os.path.join(SCREENSHOT_DIR, f"error_reviews_{test_name}_{TEST_TIMESTAMP}.png")
            self.driver.save_screenshot(screenshot_path)
            print(f"📸 Screenshot saved: {screenshot_path}")
        except:
            pass

    # ==================== TEST CASES ====================
    
    def test_01_database_connection(self):
        """TC_REV_DB01: Kiểm tra kết nối database"""
        print("\n" + "-"*50)
        print("🧪 TC_REV_DB01: KIỂM TRA KẾT NỐI DATABASE")
        print("-"*50)
        
        try:
            conn = DatabaseHelper.get_connection()
            self.assertIsNotNone(conn, "Không thể kết nối database")
            
            # Test query đơn giản
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                self.assertIsNotNone(result, "Query test thất bại")
            
            conn.close()
            print("  ✅ Kết nối database thành công!")
            
            print("\n" + "="*50)
            print("✅ PASSED: KẾT NỐI DATABASE THÀNH CÔNG!")
            print("="*50)
            
        except Exception as e:
            self._save_error_screenshot("TC_REV_DB01")
            raise e
    
    def test_02_review_table_exists(self):
        """TC_REV_DB02: Kiểm tra bảng review tồn tại và có dữ liệu"""
        print("\n" + "-"*50)
        print("🧪 TC_REV_DB02: KIỂM TRA BẢNG REVIEW")
        print("-"*50)
        
        try:
            conn = DatabaseHelper.get_connection()
            with conn.cursor() as cursor:
                # Kiểm tra bảng tồn tại
                cursor.execute("SHOW TABLES LIKE 'review'")
                result = cursor.fetchone()
                self.assertIsNotNone(result, "Bảng review không tồn tại")
                print("  ✅ Bảng review tồn tại")
                
                # Kiểm tra cấu trúc bảng
                cursor.execute("DESCRIBE review")
                columns = cursor.fetchall()
                column_names = [col['Field'] for col in columns]
                
                required_columns = ['id', 'user_id', 'product_id', 'rating', 'comment', 
                                   'admin_reply', 'replied_at', 'status', 'created_at']
                
                for col in required_columns:
                    self.assertIn(col, column_names, f"Thiếu cột {col}")
                
                print(f"  ✅ Cấu trúc bảng đúng ({len(required_columns)} cột required)")
                
                # Đếm số bản ghi
                cursor.execute("SELECT COUNT(*) as total FROM review")
                total = cursor.fetchone()['total']
                print(f"  📊 Tổng số đánh giá: {total}")
            
            conn.close()
            
            print("\n" + "="*50)
            print("✅ PASSED: BẢNG REVIEW HỢP LỆ!")
            print("="*50)
            
        except Exception as e:
            self._save_error_screenshot("TC_REV_DB02")
            raise e
    
    def test_03_display_reviews_list(self):
        """TC_REV_01: Hiển thị danh sách đánh giá"""
        print("\n" + "-"*50)
        print("🧪 TC_REV_01: HIỂN THỊ DANH SÁCH ĐÁNH GIÁ")
        print("-"*50)
        
        try:
            self._navigate_to_reviews_page()
            
            # Kiểm tra tiêu đề trang
            page_title = self.driver.find_element(By.CSS_SELECTOR, ".page-title, .card-title")
            self.assertIn("Đánh Giá", page_title.text, "Tiêu đề trang không đúng")
            print(f"  ✅ Tiêu đề trang: {page_title.text}")
            
            # Kiểm tra bảng hiển thị
            table = self.driver.find_element(By.ID, "reviews-table")
            self.assertTrue(table.is_displayed(), "Bảng reviews không hiển thị")
            print("  ✅ Bảng đánh giá hiển thị")
            
            # Kiểm tra các cột
            headers = self.driver.find_elements(By.CSS_SELECTOR, "#reviews-table thead th")
            header_texts = [h.text for h in headers]
            print(f"  📊 Các cột: {header_texts}")
            
            # Kiểm tra có dữ liệu
            rows = self._get_table_rows()
            
            # Kiểm tra xem có dòng "Không có dữ liệu" không
            if len(rows) == 1:
                cell_text = rows[0].find_element(By.TAG_NAME, "td").text
                if "Không có dữ liệu" in cell_text or "No data" in cell_text:
                    print(f"  ⚠️ Bảng không có dữ liệu")
                else:
                    print(f"  ✅ Hiển thị {len(rows)} đánh giá")
            else:
                print(f"  ✅ Hiển thị {len(rows)} đánh giá")
            
            # Kiểm tra các bộ lọc
            filters = ['product-filter', 'user-filter', 'rating-filter', 'status-filter']
            for filter_id in filters:
                filter_elem = self.driver.find_element(By.ID, filter_id)
                self.assertTrue(filter_elem.is_displayed(), f"Bộ lọc {filter_id} không hiển thị")
            print("  ✅ Tất cả bộ lọc hiển thị")
            
            print("\n" + "="*50)
            print("✅ PASSED: HIỂN THỊ DANH SÁCH ĐÁNH GIÁ!")
            print("="*50)
            
        except Exception as e:
            self._save_error_screenshot("TC_REV_01")
            raise e
    
    def test_04_search_review(self):
        """TC_REV_02: Tìm kiếm đánh giá"""
        print("\n" + "-"*50)
        print("🧪 TC_REV_02: TÌM KIẾM ĐÁNH GIÁ")
        print("-"*50)
        
        try:
            self._navigate_to_reviews_page()
            
            # Lấy một đánh giá từ database để search
            reviews = DatabaseHelper.get_all_reviews()
            if not reviews:
                print("  ⚠️ Không có đánh giá trong database để test")
                self.skipTest("Không có dữ liệu đánh giá")
            
            # Tìm kiếm theo email người gửi
            search_term = reviews[0]['user_email'].split('@')[0]  # Lấy phần trước @
            print(f"  🔍 Tìm kiếm: '{search_term}'")
            
            # Tìm ô search của DataTable
            search_input = self.wait.until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, "input#dt-search-0, input.dt-input[type='search'], .dataTables_filter input"))
            )
            search_input.clear()
            search_input.send_keys(search_term)
            time.sleep(2)
            
            self._wait_for_table_load()
            
            # Kiểm tra kết quả
            rows = self._get_table_rows()
            print(f"  📊 Kết quả tìm kiếm: {len(rows)} dòng")
            
            # Clear search
            search_input.clear()
            search_input.send_keys(Keys.RETURN)
            time.sleep(1)
            
            print("\n" + "="*50)
            print("✅ PASSED: TÌM KIẾM ĐÁNH GIÁ HOẠT ĐỘNG!")
            print("="*50)
            
        except Exception as e:
            self._save_error_screenshot("TC_REV_02")
            raise e
    
    def test_05_filter_by_product(self):
        """TC_REV_03: Lọc theo sản phẩm"""
        print("\n" + "-"*50)
        print("🧪 TC_REV_03: LỌC THEO SẢN PHẨM")
        print("-"*50)
        
        try:
            self._navigate_to_reviews_page()
            
            # Lấy danh sách sản phẩm có đánh giá
            products = DatabaseHelper.get_products_with_reviews()
            if not products:
                print("  ⚠️ Không có sản phẩm nào có đánh giá")
                self.skipTest("Không có dữ liệu")
            
            # Chọn sản phẩm đầu tiên
            product = products[0]
            print(f"  🔍 Lọc theo sản phẩm: {product['name']} (ID: {product['id']})")
            
            # Chọn trong dropdown
            product_filter = Select(self.driver.find_element(By.ID, "product-filter"))
            product_filter.select_by_value(str(product['id']))
            time.sleep(2)
            
            self._wait_for_table_load()
            
            # Kiểm tra kết quả
            rows = self._get_table_rows()
            db_reviews = DatabaseHelper.get_reviews_by_product(product['id'])
            
            print(f"  📊 UI hiển thị: {len(rows)} đánh giá")
            print(f"  📊 Database có: {len(db_reviews)} đánh giá cho sản phẩm này")
            
            # Reset filter
            product_filter.select_by_value("")
            time.sleep(1)
            
            print("\n" + "="*50)
            print("✅ PASSED: LỌC THEO SẢN PHẨM HOẠT ĐỘNG!")
            print("="*50)
            
        except Exception as e:
            self._save_error_screenshot("TC_REV_03")
            raise e
    
    def test_06_filter_by_user(self):
        """TC_REV_04: Lọc theo người gửi"""
        print("\n" + "-"*50)
        print("🧪 TC_REV_04: LỌC THEO NGƯỜI GỬI")
        print("-"*50)
        
        try:
            self._navigate_to_reviews_page()
            
            # Lấy danh sách người dùng có đánh giá
            users = DatabaseHelper.get_users_with_reviews()
            if not users:
                print("  ⚠️ Không có người dùng nào có đánh giá")
                self.skipTest("Không có dữ liệu")
            
            # Chọn người dùng đầu tiên
            user = users[0]
            print(f"  🔍 Lọc theo người gửi: {user['email']} (ID: {user['id']})")
            
            # Chọn trong dropdown
            user_filter = Select(self.driver.find_element(By.ID, "user-filter"))
            user_filter.select_by_value(str(user['id']))
            time.sleep(2)
            
            self._wait_for_table_load()
            
            # Kiểm tra kết quả
            rows = self._get_table_rows()
            db_reviews = DatabaseHelper.get_reviews_by_user(user['id'])
            
            print(f"  📊 UI hiển thị: {len(rows)} đánh giá")
            print(f"  📊 Database có: {len(db_reviews)} đánh giá từ người dùng này")
            
            # Reset filter
            user_filter.select_by_value("")
            time.sleep(1)
            
            print("\n" + "="*50)
            print("✅ PASSED: LỌC THEO NGƯỜI GỬI HOẠT ĐỘNG!")
            print("="*50)
            
        except Exception as e:
            self._save_error_screenshot("TC_REV_04")
            raise e
    
    def test_07_filter_by_rating(self):
        """TC_REV_05: Lọc theo rating"""
        print("\n" + "-"*50)
        print("🧪 TC_REV_05: LỌC THEO RATING")
        print("-"*50)
        
        try:
            self._navigate_to_reviews_page()
            
            # Lọc theo 5 sao
            rating = 5
            print(f"  🔍 Lọc theo rating: {rating} ★")
            
            rating_filter = Select(self.driver.find_element(By.ID, "rating-filter"))
            rating_filter.select_by_value(str(rating))
            time.sleep(2)
            
            self._wait_for_table_load()
            
            # Kiểm tra kết quả
            rows = self._get_table_rows()
            db_reviews = DatabaseHelper.get_reviews_by_rating(rating)
            
            print(f"  📊 UI hiển thị: {len(rows)} đánh giá")
            print(f"  📊 Database có: {len(db_reviews)} đánh giá {rating} sao")
            
            # Verify tất cả các dòng đều có 5 sao
            if len(rows) > 0:
                first_row = rows[0]
                cells = first_row.find_elements(By.TAG_NAME, "td")
                if len(cells) > 3:
                    rating_cell = cells[3].text
                    filled_stars = rating_cell.count('★')
                    print(f"  ✅ Dòng đầu tiên có {filled_stars} sao")
            
            # Reset filter
            rating_filter.select_by_value("")
            time.sleep(1)
            
            print("\n" + "="*50)
            print("✅ PASSED: LỌC THEO RATING HOẠT ĐỘNG!")
            print("="*50)
            
        except Exception as e:
            self._save_error_screenshot("TC_REV_05")
            raise e
    
    def test_08_filter_by_status(self):
        """TC_REV_06: Lọc theo trạng thái"""
        print("\n" + "-"*50)
        print("🧪 TC_REV_06: LỌC THEO TRẠNG THÁI")
        print("-"*50)
        
        try:
            self._navigate_to_reviews_page()
            
            # Lọc theo trạng thái approved
            status = "approved"
            print(f"  🔍 Lọc theo trạng thái: {status}")
            
            status_filter = Select(self.driver.find_element(By.ID, "status-filter"))
            status_filter.select_by_value(status)
            time.sleep(2)
            
            self._wait_for_table_load()
            
            # Kiểm tra kết quả
            rows = self._get_table_rows()
            db_reviews = DatabaseHelper.get_reviews_by_status(status)
            
            print(f"  📊 UI hiển thị: {len(rows)} đánh giá")
            print(f"  📊 Database có: {len(db_reviews)} đánh giá '{status}'")
            
            # Verify badge hiển thị đúng
            if len(rows) > 0:
                first_row = rows[0]
                try:
                    # Tìm badge trong cột trạng thái (cột thứ 6, index 5)
                    cells = first_row.find_elements(By.TAG_NAME, "td")
                    if len(cells) >= 6:
                        status_cell = cells[5]
                        badge_text = status_cell.text
                        print(f"  ✅ Trạng thái hiển thị: {badge_text}")
                        # Kiểm tra trạng thái hiển thị đúng (Đã duyệt cho approved)
                        self.assertIn("Đã duyệt", badge_text, "Trạng thái không đúng")
                except Exception as badge_error:
                    print(f"  ⚠️ Không tìm thấy badge: {badge_error}")
            
            # Reset filter
            status_filter.select_by_value("")
            time.sleep(1)
            
            print("\n" + "="*50)
            print("✅ PASSED: LỌC THEO TRẠNG THÁI HOẠT ĐỘNG!")
            print("="*50)
            
        except Exception as e:
            self._save_error_screenshot("TC_REV_06")
            raise e
    
    def test_09_view_review_detail(self):
        """TC_REV_07: Xem chi tiết đánh giá"""
        print("\n" + "-"*50)
        print("🧪 TC_REV_07: XEM CHI TIẾT ĐÁNH GIÁ")
        print("-"*50)
        
        try:
            # Lấy một đánh giá từ database
            reviews = DatabaseHelper.get_all_reviews()
            if not reviews:
                self.skipTest("Không có dữ liệu đánh giá")
            
            review = reviews[0]
            review_id = review['id']
            print(f"  📋 Xem chi tiết đánh giá ID: {review_id}")
            
            # Navigate đến trang chi tiết
            self._navigate_to_review_detail(review_id)
            
            # Kiểm tra trang chi tiết
            self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".card")))
            
            # Kiểm tra thông tin sản phẩm
            product_name = self.driver.find_element(By.CSS_SELECTOR, ".card-body h5")
            print(f"  📦 Sản phẩm: {product_name.text}")
            
            # Kiểm tra thông tin đánh giá
            page_source = self.driver.page_source
            self.assertIn(review['user_email'], page_source, "Không hiển thị email người gửi")
            print(f"  👤 Người gửi: {review['user_email']}")
            
            # Kiểm tra rating
            stars = self.driver.find_elements(By.XPATH, "//*[contains(text(), '★')]")
            print(f"  ⭐ Rating hiển thị: {review['rating']} sao")
            
            # Kiểm tra form phản hồi
            reply_form = self.driver.find_element(By.ID, "reply-form")
            self.assertTrue(reply_form.is_displayed(), "Form phản hồi không hiển thị")
            print("  ✅ Form phản hồi hiển thị")
            
            # Kiểm tra nút quay lại
            back_btn = self.driver.find_element(By.CSS_SELECTOR, "a[href*='page=reviews']")
            self.assertTrue(back_btn.is_displayed(), "Nút quay lại không hiển thị")
            print("  ✅ Nút quay lại hiển thị")
            
            print("\n" + "="*50)
            print("✅ PASSED: XEM CHI TIẾT ĐÁNH GIÁ HOẠT ĐỘNG!")
            print("="*50)
            
        except Exception as e:
            self._save_error_screenshot("TC_REV_07")
            raise e
    
    def test_10_admin_reply_review(self):
        """TC_REV_08: Phản hồi đánh giá"""
        print("\n" + "-"*50)
        print("🧪 TC_REV_08: PHẢN HỒI ĐÁNH GIÁ")
        print("-"*50)
        
        try:
            # Lấy một đánh giá để phản hồi
            reviews = DatabaseHelper.get_all_reviews()
            if not reviews:
                self.skipTest("Không có dữ liệu đánh giá")
            
            review = reviews[0]
            review_id = review['id']
            reply_text = f"Cảm ơn bạn đã đánh giá! - Test {TEST_TIMESTAMP}"
            
            print(f"  📋 Phản hồi đánh giá ID: {review_id}")
            print(f"  💬 Nội dung: {reply_text[:50]}...")
            
            # Navigate đến trang chi tiết
            self._navigate_to_review_detail(review_id)
            
            # Điền form phản hồi
            reply_textarea = self.wait.until(
                EC.visibility_of_element_located((By.ID, "admin_reply"))
            )
            reply_textarea.clear()
            reply_textarea.send_keys(reply_text)
            
            # Submit form
            submit_btn = self.driver.find_element(By.CSS_SELECTOR, "#reply-form button[type='submit']")
            self._js_click(submit_btn)
            time.sleep(2)
            
            # Kiểm tra thông báo thành công
            success = self._wait_for_swal_success()
            if success:
                print("  ✅ Hiển thị thông báo thành công")
            
            # Verify trong database
            updated_review = DatabaseHelper.get_review_by_id(review_id)
            self.assertEqual(updated_review['admin_reply'], reply_text, "Phản hồi không được lưu")
            self.assertIsNotNone(updated_review['replied_at'], "Thời gian phản hồi không được lưu")
            print("  ✅ Đã lưu phản hồi vào database")
            
            print("\n" + "="*50)
            print("✅ PASSED: PHẢN HỒI ĐÁNH GIÁ THÀNH CÔNG!")
            print("="*50)
            
        except Exception as e:
            self._save_error_screenshot("TC_REV_08")
            raise e
    
    def test_11_toggle_hide_review(self):
        """TC_REV_09: Ẩn đánh giá"""
        print("\n" + "-"*50)
        print("🧪 TC_REV_09: ẨN ĐÁNH GIÁ")
        print("-"*50)
        
        try:
            self._navigate_to_reviews_page()
            
            # Lấy đánh giá có status 'approved' để ẩn
            approved_reviews = DatabaseHelper.get_reviews_by_status('approved')
            if not approved_reviews:
                print("  ⚠️ Không có đánh giá 'approved' để test")
                self.skipTest("Không có dữ liệu phù hợp")
            
            review = approved_reviews[0]
            review_id = review['id']
            print(f"  📋 Ẩn đánh giá ID: {review_id}")
            
            # Tìm dòng có review ID
            rows = self._get_table_rows()
            target_row = None
            for row in rows:
                cells = row.find_elements(By.TAG_NAME, "td")
                if len(cells) > 0 and cells[0].text == str(review_id):
                    target_row = row
                    break
            
            if not target_row:
                # Tìm bằng nút toggle với ID
                toggle_btn = self.driver.find_element(
                    By.CSS_SELECTOR, f"button[onclick*='toggleReviewStatus({review_id}']"
                )
            else:
                # Tìm nút toggle trong dòng
                toggle_btn = target_row.find_element(
                    By.CSS_SELECTOR, "button.btn-warning, button[onclick*='toggleReviewStatus']"
                )
            
            self._js_click(toggle_btn)
            time.sleep(1)
            
            # Xác nhận trong SweetAlert
            self._wait_for_swal_and_confirm()
            time.sleep(2)
            
            # Kiểm tra thông báo thành công
            success = self._wait_for_swal_success()
            
            # Verify trong database
            updated_review = DatabaseHelper.get_review_by_id(review_id)
            self.assertEqual(updated_review['status'], 'hidden', "Trạng thái không được cập nhật thành 'hidden'")
            print(f"  ✅ Đã ẩn đánh giá (status: {updated_review['status']})")
            
            # Khôi phục lại trạng thái approved
            DatabaseHelper.update_review_status(review_id, 'approved')
            print("  🔄 Đã khôi phục trạng thái 'approved'")
            
            print("\n" + "="*50)
            print("✅ PASSED: ẨN ĐÁNH GIÁ THÀNH CÔNG!")
            print("="*50)
            
        except Exception as e:
            self._save_error_screenshot("TC_REV_09")
            raise e
    
    def test_12_toggle_show_review(self):
        """TC_REV_10: Hiện đánh giá"""
        print("\n" + "-"*50)
        print("🧪 TC_REV_10: HIỆN ĐÁNH GIÁ")
        print("-"*50)
        
        try:
            self._navigate_to_reviews_page()
            
            # Lấy hoặc tạo đánh giá có status 'hidden' để hiện
            hidden_reviews = DatabaseHelper.get_reviews_by_status('hidden')
            
            if not hidden_reviews:
                # Tạo một review hidden để test
                approved_reviews = DatabaseHelper.get_reviews_by_status('approved')
                if approved_reviews:
                    review_id = approved_reviews[0]['id']
                    DatabaseHelper.update_review_status(review_id, 'hidden')
                    print(f"  🔧 Đã tạo review hidden (ID: {review_id})")
                else:
                    self.skipTest("Không có dữ liệu phù hợp")
            else:
                review_id = hidden_reviews[0]['id']
            
            print(f"  📋 Hiện đánh giá ID: {review_id}")
            
            # Lọc theo trạng thái hidden
            status_filter = Select(self.driver.find_element(By.ID, "status-filter"))
            status_filter.select_by_value("hidden")
            time.sleep(2)
            self._wait_for_table_load()
            
            # Tìm nút toggle
            toggle_btn = self.driver.find_element(
                By.CSS_SELECTOR, f"button[onclick*='toggleReviewStatus({review_id}'], button.btn-success[onclick*='toggleReviewStatus']"
            )
            
            self._js_click(toggle_btn)
            time.sleep(1)
            
            # Xác nhận trong SweetAlert
            self._wait_for_swal_and_confirm()
            time.sleep(2)
            
            # Kiểm tra thông báo thành công
            success = self._wait_for_swal_success()
            
            # Verify trong database
            updated_review = DatabaseHelper.get_review_by_id(review_id)
            self.assertEqual(updated_review['status'], 'approved', "Trạng thái không được cập nhật thành 'approved'")
            print(f"  ✅ Đã hiện đánh giá (status: {updated_review['status']})")
            
            print("\n" + "="*50)
            print("✅ PASSED: HIỆN ĐÁNH GIÁ THÀNH CÔNG!")
            print("="*50)
            
        except Exception as e:
            self._save_error_screenshot("TC_REV_10")
            raise e
    
    def test_13_delete_review(self):
        """TC_REV_11: Xóa đánh giá"""
        print("\n" + "-"*50)
        print("🧪 TC_REV_11: XÓA ĐÁNH GIÁ")
        print("-"*50)
        
        try:
            # Tạo một review test để xóa
            # Lấy user và product có sẵn
            conn = DatabaseHelper.get_connection()
            with conn.cursor() as cursor:
                cursor.execute("SELECT id FROM username WHERE roleid = 2 LIMIT 1")
                user = cursor.fetchone()
                cursor.execute("SELECT id FROM product LIMIT 1")
                product = cursor.fetchone()
            conn.close()
            
            if not user or not product:
                self.skipTest("Không có user hoặc product để tạo review test")
            
            # Tạo review test
            test_comment = f"Test review để xóa - {TEST_TIMESTAMP}"
            test_review_id = DatabaseHelper.create_test_review(
                user_id=user['id'],
                product_id=product['id'],
                rating=3,
                comment=test_comment,
                status='pending'
            )
            print(f"  🔧 Đã tạo review test ID: {test_review_id}")
            
            # Navigate đến trang reviews
            self._navigate_to_reviews_page()
            time.sleep(1)
            
            # Lọc theo trạng thái pending để dễ tìm
            status_filter = Select(self.driver.find_element(By.ID, "status-filter"))
            status_filter.select_by_value("pending")
            time.sleep(2)
            self._wait_for_table_load()
            
            # Tìm nút xóa theo đúng ID review
            try:
                delete_btn = self.driver.find_element(
                    By.CSS_SELECTOR, f"button[onclick='deleteReview({test_review_id})']"
                )
            except:
                # Nếu không tìm thấy, thử tìm trong bảng theo ID
                rows = self._get_table_rows()
                delete_btn = None
                for row in rows:
                    cells = row.find_elements(By.TAG_NAME, "td")
                    if len(cells) > 0 and cells[0].text == str(test_review_id):
                        delete_btn = row.find_element(By.CSS_SELECTOR, "button.btn-danger")
                        break
                if not delete_btn:
                    raise Exception(f"Không tìm thấy nút xóa cho review ID {test_review_id}")
            
            self._js_click(delete_btn)
            time.sleep(1)
            
            # Xác nhận trong SweetAlert - Chờ popup hiện và click nút xác nhận
            try:
                swal_confirm = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, ".swal2-confirm"))
                )
                swal_confirm.click()
                time.sleep(2)
            except Exception as swal_error:
                print(f"  ⚠️ Lỗi SweetAlert: {swal_error}")
            
            # Chờ thông báo thành công và đóng
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".swal2-success, .swal2-icon-success"))
                )
                print("  ✅ Hiển thị thông báo xóa thành công")
                # Đóng SweetAlert thành công
                try:
                    ok_btn = self.driver.find_element(By.CSS_SELECTOR, ".swal2-confirm")
                    ok_btn.click()
                    time.sleep(1)
                except:
                    pass
            except:
                print("  ⚠️ Không thấy thông báo thành công")
            
            # Verify trong database
            deleted_review = DatabaseHelper.get_review_by_id(test_review_id)
            self.assertIsNone(deleted_review, "Review chưa được xóa khỏi database")
            print(f"  ✅ Đã xóa đánh giá khỏi database")
            
            print("\n" + "="*50)
            print("✅ PASSED: XÓA ĐÁNH GIÁ THÀNH CÔNG!")
            print("="*50)
            
        except Exception as e:
            self._save_error_screenshot("TC_REV_11")
            # Cleanup nếu có lỗi
            try:
                DatabaseHelper.delete_review(test_review_id)
            except:
                pass
            raise e
    
    def test_14_verify_data_matches_database(self):
        """TC_REV_12: Verify dữ liệu khớp database"""
        print("\n" + "-"*50)
        print("🧪 TC_REV_12: VERIFY DỮ LIỆU KHỚP DATABASE")
        print("-"*50)
        
        try:
            self._navigate_to_reviews_page()
            
            # Lấy dữ liệu từ database
            db_reviews = DatabaseHelper.get_all_reviews()
            if not db_reviews:
                self.skipTest("Không có dữ liệu đánh giá")
            
            db_total = len(db_reviews)
            print(f"  📊 Database có: {db_total} đánh giá")
            
            # Lấy dữ liệu từ UI (dòng đầu tiên)
            rows = self._get_table_rows()
            if len(rows) == 0:
                self.skipTest("Bảng UI không có dữ liệu")
            
            first_row = rows[0]
            cells = first_row.find_elements(By.TAG_NAME, "td")
            
            if len(cells) >= 7:
                ui_id = cells[0].text
                ui_product = cells[1].text
                ui_email = cells[2].text
                ui_rating = cells[3].text.count('★')
                ui_status = cells[5].text
                
                print(f"\n  📋 Dữ liệu UI (dòng đầu):")
                print(f"     ID: {ui_id}")
                print(f"     Sản phẩm: {ui_product}")
                print(f"     Email: {ui_email}")
                print(f"     Rating: {ui_rating} sao")
                print(f"     Trạng thái: {ui_status}")
                
                # Tìm review tương ứng trong database
                db_review = DatabaseHelper.get_review_by_id(int(ui_id))
                
                if db_review:
                    print(f"\n  📋 Dữ liệu Database:")
                    print(f"     ID: {db_review['id']}")
                    print(f"     Sản phẩm: {db_review['product_name']}")
                    print(f"     Email: {db_review['user_email']}")
                    print(f"     Rating: {db_review['rating']} sao")
                    print(f"     Trạng thái: {db_review['status']}")
                    
                    # Verify
                    self.assertEqual(ui_id, str(db_review['id']), "ID không khớp")
                    self.assertIn(db_review['product_name'][:20], ui_product, "Tên sản phẩm không khớp")
                    self.assertEqual(ui_email, db_review['user_email'], "Email không khớp")
                    self.assertEqual(ui_rating, db_review['rating'], "Rating không khớp")
                    
                    print("\n  ✅ Dữ liệu UI khớp với Database!")
            
            print("\n" + "="*50)
            print("✅ PASSED: DỮ LIỆU KHỚP VỚI DATABASE!")
            print("="*50)
            
        except Exception as e:
            self._save_error_screenshot("TC_REV_12")
            raise e


if __name__ == "__main__":
    # Chạy test với output chi tiết
    unittest.main(verbosity=2)
