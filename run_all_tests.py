import unittest
import os
import sys
from HtmlTestRunner import HTMLTestRunner

# 1. Cấu hình đường dẫn
# Lấy đường dẫn thư mục hiện tại (Project Root)
current_directory = os.getcwd()
# Đường dẫn folder chứa test case (users)
start_dir = os.path.join(current_directory, 'users')
# Đường dẫn folder xuất báo cáo (results)
report_dir = os.path.join(current_directory, 'results')

# 2. Tự động tìm tất cả các Test Case
# Pattern='test_suite_*.py' nghĩa là chỉ chạy các file bắt đầu bằng "test_suite_"
loader = unittest.TestLoader()
suite = loader.discover(start_dir=start_dir, pattern='test_suite_*.py')

# 3. Cấu hình & Chạy Test Runner xuất HTML
if __name__ == "__main__":
    # Tạo folder results nếu chưa có
    if not os.path.exists(report_dir):
        os.makedirs(report_dir)

    # Khởi chạy
    runner = HTMLTestRunner(
        output=report_dir,                  # Xuất vào folder results
        report_name="User_Module_Report",   # Tên file báo cáo
        report_title="Báo Cáo Kiểm Thử Tự Động - Web Thể Thao",
        descriptions="Kiểm thử luồng người dùng: Login, Filter, Detail, Cart, Payment",
        combine_reports=True,               # Gộp tất cả vào 1 file HTML duy nhất
        add_timestamp=True,                 # Thêm thời gian vào tên file
        open_in_browser=True                # Tự động mở file html sau khi chạy xong
    )

    runner.run(suite)