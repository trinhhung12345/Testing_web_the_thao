# 🧪 Kiểm Thử Tự Động - Web Thể Thao

Dự án kiểm thử tự động cho website bán hàng thể thao sử dụng **Selenium WebDriver** và **Python**.

## 📋 Điều Kiện Tiên Quyết

> ⚠️ **Quan trọng:** Trước khi chạy kiểm thử, bạn cần đảm bảo đã setup và chạy web thể thao thành công.

### Yêu cầu hệ thống:
- **Python** 3.8 trở lên
- **Google Chrome** (phiên bản mới nhất)
- **ChromeDriver** tương thích với phiên bản Chrome
- **Web Thể Thao** đã được deploy và chạy (local hoặc ngrok)

## 🚀 Cài Đặt

### Bước 1: Clone repository

```bash
git clone https://github.com/trinhhung12345/Testing_web_the_thao.git
cd Testing_web_the_thao
```

### Bước 2: Cài đặt dependencies

```bash
pip install -r requirements.txt
```

### Bước 3: Cấu hình ChromeDriver

1. Kiểm tra phiên bản Chrome của bạn: `chrome://version`
2. Tải ChromeDriver phù hợp từ: https://chromedriver.chromium.org/downloads
3. Đặt file `chromedriver.exe` vào thư mục `driver/`

### Bước 4: Cấu hình URL và tài khoản test

Mở các file test trong thư mục `users/` và `admin/`, cập nhật:

```python
# URL của web (thay đổi theo môi trường của bạn)
URL_LOGIN = "https://your-domain/QlyShopTheThao/src/view/login.php"

# Tài khoản test
ADMIN_ACC = {"email": "admin@example.com", "pass": "your_password"}
USER_ACC = {"email": "user@example.com", "pass": "your_password"}
```

## 📁 Cấu Trúc Dự Án

```
Testing_web_the_thao/
├── driver/                     # Chứa ChromeDriver
│   └── chromedriver.exe
├── users/                      # Test cases cho luồng User
│   ├── test_suite_01_login.py
│   ├── test_suite_02_signup.py
│   ├── test_suite_03_product_filter.py
│   ├── test_suite_04_product_detail.py
│   ├── test_suite_05_cart.py
│   ├── test_suite_06_payment.py
│   └── test_suite_07_payment_full.py
├── admin/                      # Test cases cho luồng Admin
│   ├── test_suite_01_admin_dashboard.py
│   ├── test_suite_02_admin_products.py
│   ├── test_suite_03_admin_products_crud.py
│   ├── test_suite_04_admin_categories_crud.py
│   ├── test_suite_05_admin_orders.py
│   ├── test_suite_06_admin_users.py
│   └── test_suite_07_admin_reviews.py
├── results/                    # Kết quả kiểm thử
│   ├── Users_test_result/      # Báo cáo HTML luồng User
│   └── Admin_test_result/      # Báo cáo HTML luồng Admin
├── run_all_tests.py            # Script chạy toàn bộ test
├── requirements.txt            # Dependencies
└── README.md                   # File này
```

## ▶️ Cách Chạy Kiểm Thử

### Chạy tất cả test (cả Users và Admin)

```bash
python run_all_tests.py
```
hoặc
```bash
python run_all_tests.py --all
```

### Chỉ chạy test luồng Users

```bash
python run_all_tests.py --users
```

### Chỉ chạy test luồng Admin

```bash
python run_all_tests.py --admin
```

### Chạy một file test cụ thể

```bash
# Chạy test login
python -m pytest users/test_suite_01_login.py -v

# Chạy test admin dashboard
python -m pytest admin/test_suite_01_admin_dashboard.py -v
```

### Chạy một test case cụ thể

```bash
python -m pytest users/test_suite_01_login.py::LoginTest::test_01_login_admin_success -v
```

## 📊 Xem Kết Quả

Sau khi chạy test, báo cáo HTML sẽ được tạo tại:

- **Luồng Users:** `results/Users_test_result/Users_Module_Report_<timestamp>.html`
- **Luồng Admin:** `results/Admin_test_result/Admin_Module_Report_<timestamp>.html`

Báo cáo sẽ tự động mở trong trình duyệt sau khi test hoàn tất.

## 📝 Danh Sách Test Cases

### Luồng Users (7 test suites)

| File | Mô tả |
|------|-------|
| `test_suite_01_login.py` | Kiểm thử đăng nhập |
| `test_suite_02_signup.py` | Kiểm thử đăng ký |
| `test_suite_03_product_filter.py` | Kiểm thử lọc sản phẩm |
| `test_suite_04_product_detail.py` | Kiểm thử chi tiết sản phẩm |
| `test_suite_05_cart.py` | Kiểm thử giỏ hàng |
| `test_suite_06_payment.py` | Kiểm thử thanh toán |
| `test_suite_07_payment_full.py` | Kiểm thử luồng thanh toán đầy đủ |

### Luồng Admin (7 test suites)

| File | Mô tả |
|------|-------|
| `test_suite_01_admin_dashboard.py` | Kiểm thử dashboard admin |
| `test_suite_02_admin_products.py` | Kiểm thử hiển thị sản phẩm |
| `test_suite_03_admin_products_crud.py` | Kiểm thử CRUD sản phẩm |
| `test_suite_04_admin_categories_crud.py` | Kiểm thử CRUD danh mục |
| `test_suite_05_admin_orders.py` | Kiểm thử quản lý đơn hàng |
| `test_suite_06_admin_users.py` | Kiểm thử quản lý người dùng |
| `test_suite_07_admin_reviews.py` | Kiểm thử quản lý đánh giá |

## ⚙️ Cấu Hình Nâng Cao

### Chạy ở chế độ headless (không hiển thị trình duyệt)

Mở file test và bỏ comment dòng:

```python
options.add_argument("--headless")
```

### Cấu hình Database (cho test Admin Reviews)

Trong file `admin/test_suite_07_admin_reviews.py`, cập nhật:

```python
DB_CONFIG = {
    "host": "your_host",
    "port": 3306,
    "user": "your_user",
    "password": "your_password",
    "database": "your_database"
}
```

## 🐛 Xử Lý Lỗi Thường Gặp

### 1. ChromeDriver version mismatch

```
selenium.common.exceptions.SessionNotCreatedException: Message: session not created: This version of ChromeDriver only supports Chrome version XX
```

**Giải pháp:** Tải ChromeDriver đúng phiên bản với Chrome của bạn.

### 2. Element not found

```
selenium.common.exceptions.NoSuchElementException: Message: no such element
```

**Giải pháp:** Kiểm tra lại selector hoặc tăng thời gian wait.

### 3. Unicode encoding error (Windows)

```
UnicodeEncodeError: 'charmap' codec can't encode character
```

**Giải pháp:** Đã được xử lý trong `run_all_tests.py`.

## 👥 Tác Giả

- **trinhhung12345** - [GitHub](https://github.com/trinhhung12345)

## 📄 License

MIT License
