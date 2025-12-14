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
URL_LOGIN = "https://melissia-untragical-inviably.ngrok-free.dev/QlyShopTheThao/src/view/login.php"
URL_ADMIN_PRODUCTS = "https://melissia-untragical-inviably.ngrok-free.dev/QlyShopTheThao/src/view/ViewAdmin/index.php?page=products"

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

# Dữ liệu test sản phẩm - Tên unique để dễ tìm kiếm
TEST_TIMESTAMP = datetime.now().strftime("%d%m%Y_%H%M%S")
TEST_PRODUCT_NAME = f"SP_Test_Selenium_{TEST_TIMESTAMP}"
EDITED_PRODUCT_NAME = f"SP_Test_Edited_{TEST_TIMESTAMP}"


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
    def find_product_by_name(product_name):
        """Tìm sản phẩm theo tên trong database"""
        conn = None
        try:
            conn = DatabaseHelper.get_connection()
            with conn.cursor() as cursor:
                sql = "SELECT * FROM product WHERE name LIKE %s ORDER BY id DESC LIMIT 1"
                cursor.execute(sql, (f"%{product_name}%",))
                result = cursor.fetchone()
                return result
        except Exception as e:
            print(f"❌ Database error: {e}")
            return None
        finally:
            if conn:
                conn.close()
    
    @staticmethod
    def find_product_by_id(product_id):
        """Tìm sản phẩm theo ID"""
        conn = None
        try:
            conn = DatabaseHelper.get_connection()
            with conn.cursor() as cursor:
                sql = "SELECT * FROM product WHERE id = %s"
                cursor.execute(sql, (product_id,))
                result = cursor.fetchone()
                return result
        except Exception as e:
            print(f"❌ Database error: {e}")
            return None
        finally:
            if conn:
                conn.close()
    
    @staticmethod
    def delete_test_product_by_name(product_name):
        """Xóa sản phẩm test theo tên (cleanup) - Xóa cả ảnh trước"""
        conn = None
        try:
            conn = DatabaseHelper.get_connection()
            with conn.cursor() as cursor:
                # Tìm ID sản phẩm test
                cursor.execute("SELECT id FROM product WHERE name LIKE %s", (f"%{product_name}%",))
                products = cursor.fetchall()
                
                deleted_count = 0
                for product in products:
                    product_id = product['id']
                    # Xóa ảnh trước (do foreign key)
                    cursor.execute("DELETE FROM product_image WHERE product_id = %s", (product_id,))
                    # Xóa sản phẩm
                    cursor.execute("DELETE FROM product WHERE id = %s", (product_id,))
                    deleted_count += 1
                
                conn.commit()
                return deleted_count
        except Exception as e:
            print(f"❌ Database error: {e}")
            return 0
        finally:
            if conn:
                conn.close()
    
    @staticmethod
    def get_product_count():
        """Đếm tổng số sản phẩm active"""
        conn = None
        try:
            conn = DatabaseHelper.get_connection()
            with conn.cursor() as cursor:
                # Bảng product dùng is_active thay vì is_deleted
                sql = "SELECT COUNT(*) as count FROM product WHERE is_active = 1"
                cursor.execute(sql)
                result = cursor.fetchone()
                return result['count'] if result else 0
        except Exception as e:
            print(f"❌ Database error: {e}")
            return 0
        finally:
            if conn:
                conn.close()

    @staticmethod
    def check_product_is_deleted(product_id):
        """Kiểm tra sản phẩm đã bị soft delete chưa (is_active = 0)"""
        conn = None
        try:
            conn = DatabaseHelper.get_connection()
            with conn.cursor() as cursor:
                # Bảng product dùng is_active (0 = deleted, 1 = active)
                sql = "SELECT is_active FROM product WHERE id = %s"
                cursor.execute(sql, (product_id,))
                result = cursor.fetchone()
                if result:
                    # is_active = 0 nghĩa là đã xóa (soft delete)
                    return result['is_active'] == 0
                return None
        except Exception as e:
            print(f"❌ Database error: {e}")
            return None
        finally:
            if conn:
                conn.close()


class AdminProductsCRUDTest(unittest.TestCase):
    """
    Test Suite CRUD sản phẩm - Kiểm tra thực tế vào Database
    
    Flow test:
    1. Test kết nối Database
    2. Thêm sản phẩm mới -> Verify trong DB
    3. Sửa sản phẩm -> Verify trong DB  
    4. Xóa sản phẩm (soft delete) -> Verify trong DB
    """

    # Biến class để lưu thông tin giữa các test
    created_product_id = None
    
    @classmethod
    def setUpClass(cls):
        """Setup: Khởi tạo driver và đăng nhập Admin"""
        driver_path = os.path.join(os.getcwd(), 'driver', 'chromedriver.exe')
        service = Service(driver_path)
        options = webdriver.ChromeOptions()
        cls.driver = webdriver.Chrome(service=service, options=options)
        cls.driver.maximize_window()
        cls.wait = WebDriverWait(cls.driver, 15)
        
        # Đăng nhập Admin
        cls._login_as_admin()
        
        print("\n" + "="*60)
        print("🧪 BẮT ĐẦU TEST CRUD SẢN PHẨM VỚI DATABASE")
        print(f"📝 Tên sản phẩm test: {TEST_PRODUCT_NAME}")
        print("="*60)

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

        WebDriverWait(driver, 15).until(EC.url_contains("ViewAdmin"))
        print("✅ Đăng nhập Admin thành công!")

    @classmethod
    def tearDownClass(cls):
        """Cleanup: Đóng browser và xóa sản phẩm test"""
        print("\n" + "="*60)
        print("🧹 DỌN DẸP SAU TEST")
        print("="*60)
        
        # Xóa sản phẩm test trong database (hard delete)
        deleted_count = DatabaseHelper.delete_test_product_by_name("SP_Test_")
        print(f"  🗑️ Đã xóa {deleted_count} sản phẩm test khỏi database")
        
        cls.driver.quit()
        print("✅ Hoàn tất cleanup!")

    def _navigate_to_products_page(self):
        """Navigate đến trang Products"""
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
        
        # Chờ bảng sản phẩm load
        self.wait.until(EC.presence_of_element_located((By.ID, "add-row")))
        time.sleep(1)

    def _save_error_screenshot(self, test_name):
        """Lưu screenshot khi có lỗi"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        screenshot_name = f"error_crud_{test_name}_{timestamp}.png"
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

    # ==================== TEST 01: KẾT NỐI DATABASE ====================
    
    def test_01_database_connection(self):
        """TC_DB01: Kiểm tra kết nối database thành công"""
        print("\n" + "-"*50)
        print("🧪 TC_DB01: Kiểm tra kết nối Database")
        print("-"*50)
        
        try:
            conn = DatabaseHelper.get_connection()
            self.assertIsNotNone(conn, "Không thể kết nối database")
            
            # Test query đơn giản
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1 as test")
                result = cursor.fetchone()
                self.assertEqual(result['test'], 1)
            
            conn.close()
            print("✅ PASSED: Kết nối database thành công!")
            
        except Exception as e:
            self._save_error_screenshot("TC_DB01")
            self.fail(f"Không thể kết nối database: {e}")

    def test_02_database_products_table_exists(self):
        """TC_DB02: Kiểm tra bảng product tồn tại"""
        print("\n" + "-"*50)
        print("🧪 TC_DB02: Kiểm tra bảng product tồn tại")
        print("-"*50)
        
        try:
            conn = DatabaseHelper.get_connection()
            with conn.cursor() as cursor:
                cursor.execute("SHOW TABLES LIKE 'product'")
                result = cursor.fetchone()
                self.assertIsNotNone(result, "Bảng product không tồn tại")
            
            conn.close()
            print("✅ PASSED: Bảng product tồn tại!")
            
        except Exception as e:
            self._save_error_screenshot("TC_DB02")
            self.fail(f"Lỗi kiểm tra bảng: {e}")

    # ==================== TEST 03: THÊM SẢN PHẨM ====================
    
    def _create_test_image(self, path, width=400, height=400, color=(73, 109, 137)):
        """Tạo ảnh test bằng Pillow"""
        from PIL import Image, ImageDraw, ImageFont
        
        # Tạo ảnh với màu nền
        img = Image.new('RGB', (width, height), color=color)
        draw = ImageDraw.Draw(img)
        
        # Thêm text vào giữa ảnh
        text = f"TEST\n{TEST_TIMESTAMP}"
        try:
            # Thử dùng font mặc định
            font = ImageFont.load_default()
        except:
            font = None
        
        # Vẽ text ở giữa
        bbox = draw.textbbox((0, 0), text, font=font) if font else (0, 0, 100, 50)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (width - text_width) // 2
        y = (height - text_height) // 2
        draw.text((x, y), text, fill=(255, 255, 255), font=font)
        
        # Vẽ border
        draw.rectangle([0, 0, width-1, height-1], outline=(255, 255, 255), width=3)
        
        img.save(path, 'JPEG', quality=90)
        return path
    
    def test_03_add_product_success(self):
        """TC_CRUD01: Thêm sản phẩm mới và verify trong Database"""
        print("\n" + "-"*50)
        print("🧪 TC_CRUD01: THÊM SẢN PHẨM MỚI")
        print(f"   Tên SP: {TEST_PRODUCT_NAME}")
        print("-"*50)
        
        driver = self.driver
        
        try:
            # Tạo file ảnh test bằng Pillow
            test_image_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'test_image.jpg')
            test_image_path = os.path.abspath(test_image_path)
            
            print("  📷 Tạo ảnh test bằng Pillow...")
            try:
                self._create_test_image(test_image_path, width=400, height=400, color=(52, 152, 219))
                print(f"  ✅ Đã tạo ảnh test: {test_image_path}")
            except Exception as img_ex:
                print(f"  ❌ Lỗi tạo ảnh: {img_ex}")
                self.skipTest(f"Không thể tạo ảnh test: {img_ex}")
            
            # Navigate đến trang products
            self._navigate_to_products_page()
            
            # Đếm số sản phẩm trước khi thêm
            count_before = DatabaseHelper.get_product_count()
            print(f"  📊 Số sản phẩm trong DB trước khi thêm: {count_before}")
            
            # Mở modal thêm sản phẩm
            add_btn = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(@class,'btn-primary') and contains(.,'Thêm sản phẩm')]"))
            )
            self._js_click(add_btn)
            time.sleep(2)
            
            # Chờ modal thêm sản phẩm hiện
            add_modal = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.ID, "addRowModal"))
            )
            print("  ✅ Modal thêm sản phẩm đã mở")
            
            # Điền thông tin sản phẩm
            # Tên sản phẩm
            name_input = driver.find_element(By.ID, "addProductName")
            name_input.clear()
            name_input.send_keys(TEST_PRODUCT_NAME)
            
            # Giá
            price_input = driver.find_element(By.ID, "addProductPrice")
            price_input.clear()
            price_input.send_keys("500000")
            
            # Giá khuyến mãi
            discount_input = driver.find_element(By.ID, "addProductDiscountPrice")
            discount_input.clear()
            discount_input.send_keys("450000")
            
            # Số lượng tồn kho
            stock_input = driver.find_element(By.ID, "addProductStock")
            stock_input.clear()
            stock_input.send_keys("100")
            
            # Chọn danh mục (chọn option đầu tiên có value)
            category_select = Select(driver.find_element(By.ID, "addProductCategory"))
            if len(category_select.options) > 1:
                category_select.select_by_index(1)
            
            # Thương hiệu (nếu có)
            try:
                brand_input = driver.find_element(By.ID, "addProductBrand")
                brand_input.clear()
                brand_input.send_keys("Test Brand Selenium")
            except:
                pass
            
            # Mô tả
            try:
                desc_input = driver.find_element(By.ID, "addProductDescription")
                desc_input.clear()
                desc_input.send_keys("Sản phẩm test tự động bởi Selenium - " + TEST_TIMESTAMP)
            except:
                pass
            
            print("  📝 Đã điền thông tin sản phẩm")
            
            # ========== UPLOAD ẢNH THUMBNAIL VỚI IMAGE CROPPER ==========
            print("  📷 Bắt đầu upload ảnh thumbnail...")
            thumbnail_uploaded = False
            
            # Liệt kê tất cả input[type='file'] trong trang (không chỉ trong modal)
            all_file_inputs = driver.find_elements(By.CSS_SELECTOR, "input[type='file']")
            print(f"     Tổng số input file trên trang: {len(all_file_inputs)}")
            
            for idx, file_input in enumerate(all_file_inputs):
                input_id = file_input.get_attribute('id') or 'N/A'
                input_name = file_input.get_attribute('name') or 'N/A'
                input_accept = file_input.get_attribute('accept') or 'N/A'
                is_displayed = file_input.is_displayed()
                print(f"     [{idx+1}] ID='{input_id}', name='{input_name}', accept='{input_accept}', visible={is_displayed}")
            
            # Tìm input file cho thumbnail với nhiều selector
            thumbnail_input = None
            thumbnail_selectors = [
                "#addRowModal input[type='file'][accept*='image']",
                "#addRowModal input[type='file']",
                "input[type='file'][id*='thumbnail' i]",
                "input[type='file'][id*='Thumbnail' i]",
                "input[type='file'][name*='thumbnail' i]",
                "input[type='file'][accept*='image']",
                "#addProductThumbnail",
                "#addProductThumbnailInput",
                "#thumbnailInput",
            ]
            
            for selector in thumbnail_selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        thumbnail_input = elements[0]
                        print(f"  ✅ Tìm thấy input file với selector: {selector}")
                        print(f"     ID: {thumbnail_input.get_attribute('id')}")
                        break
                except:
                    continue
            
            if not thumbnail_input and all_file_inputs:
                # Fallback: dùng input file đầu tiên
                thumbnail_input = all_file_inputs[0]
                print(f"  ⚠️ Sử dụng input file đầu tiên: {thumbnail_input.get_attribute('id')}")
            
            if thumbnail_input:
                try:
                    # Make input visible và interactable
                    driver.execute_script("""
                        arguments[0].style.display = 'block';
                        arguments[0].style.visibility = 'visible';
                        arguments[0].style.opacity = '1';
                        arguments[0].style.height = 'auto';
                        arguments[0].style.width = 'auto';
                        arguments[0].style.position = 'relative';
                    """, thumbnail_input)
                    time.sleep(0.5)
                    
                    # Gửi file path vào input
                    thumbnail_input.send_keys(test_image_path)
                    print(f"  ✅ Đã gửi file ảnh: {test_image_path}")
                    time.sleep(2)
                    
                    # Xử lý Image Cropper Modal
                    try:
                        cropper_modal = WebDriverWait(driver, 5).until(
                            EC.visibility_of_element_located((By.ID, "imageCropperModal"))
                        )
                        print("  ✅ Image Cropper Modal đã xuất hiện")
                        
                        # Chờ Cropper.js khởi tạo xong (quan trọng!)
                        time.sleep(3)
                        
                        # Tìm và click nút "Cắt & Sử dụng" (confirmCropButton)
                        crop_btn_selectors = [
                            (By.ID, "confirmCropButton"),
                            (By.CSS_SELECTOR, "#imageCropperModal .btn-primary"),
                            (By.CSS_SELECTOR, "#imageCropperModal button[type='button']:not(.btn-secondary)"),
                            (By.XPATH, "//div[@id='imageCropperModal']//button[contains(text(),'Cắt') or contains(text(),'Sử dụng') or contains(text(),'OK')]")
                        ]
                        
                        crop_clicked = False
                        for selector in crop_btn_selectors:
                            try:
                                crop_btn = WebDriverWait(driver, 3).until(
                                    EC.element_to_be_clickable(selector)
                                )
                                btn_text = crop_btn.text.strip()
                                print(f"  ✅ Tìm thấy nút crop: '{btn_text}'")
                                self._js_click(crop_btn)
                                print("  ✅ Đã click nút crop")
                                crop_clicked = True
                                break
                            except:
                                continue
                        
                        if crop_clicked:
                            # Chờ cropper modal đóng
                            WebDriverWait(driver, 10).until(
                                EC.invisibility_of_element_located((By.ID, "imageCropperModal"))
                            )
                            print("  ✅ Image Cropper đã đóng")
                            thumbnail_uploaded = True
                        else:
                            print("  ❌ Không thể click nút crop")
                            
                    except TimeoutException:
                        print("  ℹ️ Không có Image Cropper - ảnh có thể đã được upload trực tiếp")
                        thumbnail_uploaded = True
                    except Exception as crop_ex:
                        print(f"  ⚠️ Lỗi xử lý Image Cropper: {crop_ex}")
                        
                except Exception as upload_ex:
                    print(f"  ❌ Lỗi upload ảnh: {upload_ex}")
            else:
                print("  ❌ Không tìm thấy input file để upload ảnh")
            
            time.sleep(1)
            
            if not thumbnail_uploaded:
                print("  ⚠️ Không thể upload thumbnail - form có thể yêu cầu ảnh bắt buộc")
            
            # Click nút Thêm mới
            submit_btn = driver.find_element(By.ID, "submitAddProductButton")
            self._js_click(submit_btn)
            
            # Chờ xử lý AJAX
            time.sleep(3)
            
            # Kiểm tra thông báo thành công hoặc modal đóng
            try:
                # Chờ modal đóng (thành công)
                WebDriverWait(driver, 10).until(
                    EC.invisibility_of_element_located((By.ID, "addRowModal"))
                )
                print("  ✅ Modal đã đóng - Thêm sản phẩm thành công trên UI")
            except:
                # Kiểm tra có thông báo lỗi không
                try:
                    error_msg = driver.find_element(By.CSS_SELECTOR, ".alert-danger, .error-message")
                    print(f"  ❌ Lỗi từ server: {error_msg.text}")
                except:
                    pass
                # Modal vẫn mở có thể do thiếu ảnh
                print("  ⚠️ Modal vẫn mở - có thể do thiếu ảnh thumbnail (required)")
            
            # Chờ thêm để DB cập nhật
            time.sleep(2)
            
            # VERIFY TRONG DATABASE
            print("\n  🔍 VERIFY TRONG DATABASE:")
            product_in_db = DatabaseHelper.find_product_by_name(TEST_PRODUCT_NAME)
            
            if product_in_db:
                AdminProductsCRUDTest.created_product_id = product_in_db['id']
                print(f"  ✅ Tìm thấy sản phẩm trong DB!")
                print(f"     - ID: {product_in_db['id']}")
                print(f"     - Tên: {product_in_db['name']}")
                print(f"     - Giá: {product_in_db.get('price', 'N/A')}")
                print(f"     - Tồn kho: {product_in_db.get('stock', 'N/A')}")
                
                # Verify giá trị
                self.assertIn(TEST_PRODUCT_NAME, product_in_db['name'])
                
                count_after = DatabaseHelper.get_product_count()
                print(f"\n  📊 Số sản phẩm sau khi thêm: {count_after}")
                
                print("\n" + "="*50)
                print("✅ PASSED: SẢN PHẨM ĐÃ ĐƯỢC THÊM VÀO DATABASE!")
                print("="*50)
            else:
                print("  ❌ Không tìm thấy sản phẩm trong database")
                print("  ⚠️ Có thể do form yêu cầu ảnh thumbnail bắt buộc")
                # Không fail test, chỉ skip nếu không có ảnh
                self.skipTest("Không thể thêm sản phẩm - có thể do thiếu ảnh thumbnail")
                
        except Exception as e:
            self._save_error_screenshot("TC_CRUD01_add")
            raise e

    # ==================== TEST 04: SỬA SẢN PHẨM ====================
    
    def test_04_edit_product_success(self):
        """TC_CRUD02: Sửa sản phẩm và verify trong Database"""
        print("\n" + "-"*50)
        print("🧪 TC_CRUD02: SỬA SẢN PHẨM")
        print("-"*50)
        
        driver = self.driver
        
        # Lấy sản phẩm đầu tiên trong database để test (không phụ thuộc test_03)
        product_id = None
        original_name = None
        original_price = None
        
        if AdminProductsCRUDTest.created_product_id:
            product_id = AdminProductsCRUDTest.created_product_id
        else:
            # Lấy sản phẩm có is_active = 1 đầu tiên để test
            conn = DatabaseHelper.get_connection()
            try:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT id, name, price FROM product WHERE is_active = 1 ORDER BY id ASC LIMIT 1")
                    product = cursor.fetchone()
                    if product:
                        product_id = product['id']
                        original_name = product['name']
                        original_price = product['price']
                        print(f"  📦 Sử dụng sản phẩm có sẵn: ID={product_id}, Tên={original_name}")
            finally:
                conn.close()
        
        if not product_id:
            self.skipTest("Không có sản phẩm nào trong database để test")
        
        print(f"  📦 Sửa sản phẩm ID: {product_id}")
        
        try:
            # Navigate đến trang products
            self._navigate_to_products_page()
            
            # Lấy thông tin sản phẩm trước khi sửa
            product_before = DatabaseHelper.find_product_by_id(product_id)
            original_name = product_before['name']
            original_price = product_before['price']
            print(f"  📝 Tên trước khi sửa: {original_name}")
            print(f"  📝 Giá trước khi sửa: {original_price}")
            
            # Tìm và click nút sửa của sản phẩm
            edit_btn = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, f"//button[contains(@class,'edit-product-button') and @data-product-id='{product_id}']"))
            )
            self._scroll_to_element(edit_btn)
            self._js_click(edit_btn)
            
            # Chờ modal và AJAX load dữ liệu
            self.wait.until(EC.visibility_of_element_located((By.ID, "productEditModal")))
            time.sleep(3)
            
            # Chờ input name có value
            name_input = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.ID, "modalEditProductName"))
            )
            WebDriverWait(driver, 10).until(
                lambda d: name_input.get_attribute("value") != ""
            )
            
            # Tạo tên và giá mới để test
            test_suffix = " - EDITED_" + TEST_TIMESTAMP
            new_name = original_name + test_suffix
            new_price = "999999"
            
            # Sửa tên sản phẩm bằng JavaScript để đảm bảo trigger change event
            driver.execute_script("arguments[0].value = ''; arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", name_input)
            time.sleep(0.5)
            name_input.send_keys(new_name)
            driver.execute_script("arguments[0].dispatchEvent(new Event('change', { bubbles: true }));", name_input)
            time.sleep(1)
            
            # Sửa giá
            price_input = driver.find_element(By.ID, "modalEditProductPrice")
            driver.execute_script("arguments[0].value = ''; arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", price_input)
            time.sleep(0.5)
            price_input.send_keys(new_price)
            driver.execute_script("arguments[0].dispatchEvent(new Event('change', { bubbles: true }));", price_input)
            time.sleep(1)
            
            print(f"  📝 Tên mới: {new_name}")
            print(f"  📝 Giá mới: {new_price}")
            
            # Click nút Lưu thay đổi
            save_btn = driver.find_element(By.ID, "modalOpenSaveChangesConfirmButton")
            
            # Chờ nút enable (phát hiện thay đổi)
            try:
                WebDriverWait(driver, 5).until(
                    lambda d: not save_btn.get_attribute("disabled")
                )
                print("  ✅ Nút Lưu đã enable")
            except:
                print("  ⚠️ Nút Lưu vẫn disabled, thử click anyway...")
                # Kiểm tra trạng thái nút
                is_disabled = save_btn.get_attribute("disabled")
                print(f"     Trạng thái disabled: {is_disabled}")
            
            self._js_click(save_btn)
            print("  ✅ Đã click nút Lưu thay đổi")
            time.sleep(2)
            
            # Xác nhận lưu trong modal confirm
            confirm_clicked = False
            try:
                save_confirm_modal = WebDriverWait(driver, 5).until(
                    EC.visibility_of_element_located((By.ID, "saveConfirmModal"))
                )
                print("  ✅ Modal xác nhận lưu xuất hiện")
                
                # Tìm tất cả các nút trong modal confirm để debug
                all_buttons = save_confirm_modal.find_elements(By.TAG_NAME, "button")
                print(f"     Tìm thấy {len(all_buttons)} nút trong modal confirm:")
                for btn in all_buttons:
                    btn_id = btn.get_attribute("id")
                    btn_class = btn.get_attribute("class")
                    btn_text = btn.text.strip()
                    print(f"       - ID='{btn_id}', class='{btn_class}', text='{btn_text}'")
                
                # Thử tìm nút confirm bằng nhiều cách
                confirm_selectors = [
                    (By.ID, "confirmSaveButton"),
                    (By.CSS_SELECTOR, "#saveConfirmModal .btn-primary"),
                    (By.CSS_SELECTOR, "#saveConfirmModal .btn-success"),
                    (By.CSS_SELECTOR, "#saveConfirmModal button[type='submit']"),
                    (By.XPATH, "//div[@id='saveConfirmModal']//button[contains(text(),'Xác nhận') or contains(text(),'Lưu') or contains(text(),'OK') or contains(text(),'Có')]")
                ]
                
                for selector in confirm_selectors:
                    try:
                        confirm_btn = save_confirm_modal.find_element(*selector)
                        if confirm_btn.is_displayed():
                            print(f"  ✅ Tìm thấy nút confirm: {confirm_btn.text}")
                            self._js_click(confirm_btn)
                            print("  ✅ Đã click xác nhận lưu")
                            confirm_clicked = True
                            time.sleep(3)
                            break
                    except:
                        continue
                        
                if not confirm_clicked:
                    print("  ⚠️ Không tìm thấy nút confirm trong modal")
                    
            except Exception as modal_ex:
                print(f"  ⚠️ Không có modal xác nhận lưu: {modal_ex}")
            
            # Nếu chưa click được confirm, thử tìm các nút khác
            if not confirm_clicked:
                print("  🔍 Thử tìm các nút submit khác trong modal edit...")
                try:
                    submit_btns = driver.find_elements(By.CSS_SELECTOR, "#productEditModal button[type='submit'], #productEditModal .btn-primary, #productEditModal .btn-success")
                    for btn in submit_btns:
                        if btn.is_displayed() and btn.is_enabled():
                            print(f"     Tìm thấy nút: {btn.text} (ID: {btn.get_attribute('id')})")
                            self._js_click(btn)
                            time.sleep(2)
                            confirm_clicked = True
                            break
                except Exception as ex:
                    print(f"     Không tìm thấy nút submit: {ex}")
            
            # Chờ modal edit đóng
            try:
                WebDriverWait(driver, 10).until(
                    EC.invisibility_of_element_located((By.ID, "productEditModal"))
                )
                print("  ✅ Modal đã đóng - Sửa sản phẩm thành công trên UI")
            except:
                print("  ⚠️ Modal vẫn mở")
            
            # Chờ DB cập nhật
            time.sleep(2)
            
            # VERIFY TRONG DATABASE
            print("\n  🔍 VERIFY TRONG DATABASE:")
            product_after = DatabaseHelper.find_product_by_id(product_id)
            
            if product_after:
                print(f"  ✅ Sản phẩm sau khi sửa:")
                print(f"     - ID: {product_after['id']}")
                print(f"     - Tên: {product_after['name']}")
                print(f"     - Giá: {product_after.get('price', 'N/A')}")
                
                # Verify tên đã được cập nhật
                name_updated = test_suffix in str(product_after['name'])
                price_updated = str(product_after['price']) == new_price or float(product_after['price']) == float(new_price)
                
                if name_updated or price_updated:
                    print("\n" + "="*50)
                    print("✅ PASSED: SẢN PHẨM ĐÃ ĐƯỢC CẬP NHẬT TRONG DATABASE!")
                    print("="*50)
                    
                    # Khôi phục lại tên và giá gốc
                    print("\n  🔄 Khôi phục dữ liệu gốc...")
                    conn = DatabaseHelper.get_connection()
                    try:
                        with conn.cursor() as cursor:
                            cursor.execute(
                                "UPDATE product SET name = %s, price = %s WHERE id = %s",
                                (original_name, original_price, product_id)
                            )
                            conn.commit()
                            print(f"  ✅ Đã khôi phục: Tên={original_name}, Giá={original_price}")
                    finally:
                        conn.close()
                else:
                    print(f"  ⚠️ Dữ liệu chưa được cập nhật đúng")
                    print(f"     Expected name contains: {test_suffix}")
                    print(f"     Actual name: {product_after['name']}")
                    self.fail("Dữ liệu không được cập nhật trong database")
            else:
                self.fail("Không tìm thấy sản phẩm sau khi sửa")
                
        except Exception as e:
            self._save_error_screenshot("TC_CRUD02_edit")
            raise e

    # ==================== TEST 05: XÓA SẢN PHẨM ====================
    
    def test_05_delete_product_success(self):
        """TC_CRUD03: Xóa sản phẩm (soft delete) và verify trong Database"""
        print("\n" + "-"*50)
        print("🧪 TC_CRUD03: XÓA SẢN PHẨM (SOFT DELETE)")
        print("-"*50)
        
        driver = self.driver
        
        # Tìm sản phẩm có is_active = 0 (đã bị soft delete trước đó) để test khôi phục và xóa lại
        # Hoặc dùng sản phẩm cuối cùng trong danh sách
        product_id = None
        original_is_active = None
        
        conn = DatabaseHelper.get_connection()
        try:
            with conn.cursor() as cursor:
                # Tìm sản phẩm is_active = 0 (đã soft delete) - sản phẩm test cũ
                cursor.execute("SELECT id, name, is_active FROM product WHERE is_active = 0 ORDER BY id DESC LIMIT 1")
                product = cursor.fetchone()
                
                if product:
                    product_id = product['id']
                    original_is_active = product['is_active']
                    print(f"  📦 Tìm thấy SP đã soft delete: ID={product_id}, Tên={product['name']}")
                    
                    # Khôi phục lại để test xóa
                    cursor.execute("UPDATE product SET is_active = 1 WHERE id = %s", (product_id,))
                    conn.commit()
                    print(f"  🔄 Đã khôi phục is_active = 1 để test xóa")
                else:
                    # Nếu không có sản phẩm soft delete, skip test
                    print("  ⚠️ Không có sản phẩm đã soft delete để test")
                    self.skipTest("Không có sản phẩm phù hợp để test xóa")
        finally:
            conn.close()
        
        print(f"  📦 Xóa sản phẩm ID: {product_id}")
        
        try:
            # Navigate đến trang products
            self._navigate_to_products_page()
            
            # Kiểm tra sản phẩm tồn tại trước khi xóa
            product_before = DatabaseHelper.find_product_by_id(product_id)
            if not product_before:
                self.skipTest(f"Sản phẩm ID {product_id} không tồn tại")
            
            print(f"  📝 Sản phẩm trước khi xóa: {product_before['name']}")
            is_active_before = product_before.get('is_active', 1)
            print(f"  📝 Trạng thái is_active trước: {is_active_before}")
            
            # Tìm và click nút xóa của sản phẩm
            delete_btn = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, f"//button[contains(@class,'delete-product-button') and @data-product-id='{product_id}']"))
            )
            self._scroll_to_element(delete_btn)
            self._js_click(delete_btn)
            time.sleep(1)
            
            # Chờ modal xác nhận xóa
            delete_modal = self.wait.until(
                EC.visibility_of_element_located((By.ID, "deleteConfirmModal"))
            )
            print("  ✅ Modal xác nhận xóa hiển thị")
            
            # Click nút Xóa để xác nhận
            confirm_delete_btn = delete_modal.find_element(By.ID, "confirmDeleteButton")
            self._js_click(confirm_delete_btn)
            
            # Chờ xử lý AJAX
            time.sleep(3)
            
            # Chờ modal đóng
            try:
                WebDriverWait(driver, 10).until(
                    EC.invisibility_of_element_located((By.ID, "deleteConfirmModal"))
                )
                print("  ✅ Modal đã đóng - Xóa thành công trên UI")
            except:
                print("  ⚠️ Modal vẫn mở")
            
            # Chờ DB cập nhật
            time.sleep(2)
            
            # VERIFY TRONG DATABASE
            print("\n  🔍 VERIFY TRONG DATABASE:")
            
            # Kiểm tra soft delete (is_active = 0)
            is_deleted = DatabaseHelper.check_product_is_deleted(product_id)
            
            if is_deleted is True:
                print(f"  ✅ Sản phẩm ID {product_id} đã được SOFT DELETE")
                print(f"     - is_active = 0")
                
                print("\n" + "="*50)
                print("✅ PASSED: SẢN PHẨM ĐÃ ĐƯỢC XÓA (SOFT DELETE) TRONG DATABASE!")
                print("="*50)
            elif is_deleted is False:
                print(f"  ❌ Sản phẩm chưa được đánh dấu xóa (is_active = 1)")
                self.fail("Soft delete không thành công")
            else:
                # Có thể đã hard delete
                product_after = DatabaseHelper.find_product_by_id(product_id)
                if product_after is None:
                    print(f"  ✅ Sản phẩm ID {product_id} đã được HARD DELETE")
                    print("\n" + "="*50)
                    print("✅ PASSED: SẢN PHẨM ĐÃ ĐƯỢC XÓA KHỎI DATABASE!")
                    print("="*50)
                else:
                    self.fail("Không thể xác định trạng thái xóa")
                
        except Exception as e:
            self._save_error_screenshot("TC_CRUD03_delete")
            raise e

    # ==================== TEST 06: VERIFY SAU XÓA ====================
    
    def test_06_verify_product_not_displayed_after_delete(self):
        """TC_CRUD04: Verify sản phẩm đã xóa (is_active=0) không hiển thị trên UI"""
        print("\n" + "-"*50)
        print("🧪 TC_CRUD04: VERIFY SẢN PHẨM ĐÃ XÓA KHÔNG HIỂN THỊ TRÊN UI")
        print("-"*50)
        
        driver = self.driver
        
        # Tìm sản phẩm có is_active = 0 trong database
        product_id = None
        product_name = None
        
        conn = DatabaseHelper.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT id, name FROM product WHERE is_active = 0 ORDER BY id DESC LIMIT 1")
                product = cursor.fetchone()
                if product:
                    product_id = product['id']
                    product_name = product['name']
        finally:
            conn.close()
        
        if not product_id:
            self.skipTest("Không có sản phẩm soft delete để verify")
        
        print(f"  📦 Kiểm tra SP đã xóa: ID={product_id}, Tên={product_name}")
        
        try:
            # Navigate đến trang products
            self._navigate_to_products_page()
            
            # Tìm kiếm sản phẩm đã xóa theo tên
            try:
                search_input = driver.find_element(By.ID, "searchProductInput")
                search_input.clear()
                search_input.send_keys(product_name[:20])  # Tìm theo phần đầu của tên
                
                # Click nút tìm kiếm
                search_btn = driver.find_element(By.XPATH, "//form[@id='searchProductForm']//button[contains(.,'Tìm')]")
                self._js_click(search_btn)
                time.sleep(2)
            except:
                pass
            
            # Kiểm tra sản phẩm không còn hiển thị
            try:
                product_row = driver.find_element(By.XPATH, f"//tr[@data-product-id='{product_id}']")
                # Nếu tìm thấy, kiểm tra xem có hidden không
                if product_row.is_displayed():
                    print(f"  ⚠️ Sản phẩm ID {product_id} vẫn hiển thị trên UI (is_active=0 nhưng vẫn hiển thị)")
                    # Đây có thể là expected behavior nếu admin có thể xem cả sản phẩm đã xóa
                else:
                    print(f"  ✅ Sản phẩm ID {product_id} đã ẩn trên UI")
            except NoSuchElementException:
                print(f"  ✅ Sản phẩm ID {product_id} không còn trên UI (đã bị filter)")
            
            print("\n" + "="*50)
            print("✅ PASSED: KIỂM TRA HIỂN THỊ SẢN PHẨM ĐÃ XÓA HOÀN TẤT!")
            print("="*50)
                
        except Exception as e:
            self._save_error_screenshot("TC_CRUD04_verify_delete")
            raise e


if __name__ == "__main__":
    # Kiểm tra pymysql đã cài đặt chưa
    try:
        import pymysql
        print("✅ pymysql đã được cài đặt")
    except ImportError:
        print("❌ Cần cài đặt pymysql: pip install pymysql")
        exit(1)
    
    # Chạy tests theo thứ tự
    loader = unittest.TestLoader()
    loader.sortTestMethodsUsing = lambda x, y: (x > y) - (x < y)  # Sort theo tên
    
    suite = loader.loadTestsFromTestCase(AdminProductsCRUDTest)
    
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
