import unittest
import os
import sys
import io
import builtins

# Fix encoding cho Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Monkey patch built-in open để force UTF-8 khi ghi file HTML
_original_open = builtins.open

def _patched_open(file, mode='r', *args, **kwargs):
    # Nếu đang ghi file HTML và không có encoding được chỉ định
    if 'w' in mode and isinstance(file, str) and file.endswith('.html'):
        if 'encoding' not in kwargs:
            kwargs['encoding'] = 'utf-8'
    return _original_open(file, mode, *args, **kwargs)

builtins.open = _patched_open

from HtmlTestRunner import HTMLTestRunner

# 1. Cấu hình đường dẫn
# Lấy đường dẫn thư mục hiện tại (Project Root)
current_directory = os.getcwd()

# Đường dẫn folder chứa test case
users_test_dir = os.path.join(current_directory, 'users')
admin_test_dir = os.path.join(current_directory, 'admin')

# Đường dẫn folder xuất báo cáo (trong folder results)
results_dir = os.path.join(current_directory, 'results')
users_report_dir = os.path.join(results_dir, 'Users_test_result')
admin_report_dir = os.path.join(results_dir, 'Admin_test_result')


def run_users_tests():
    """Chay tat ca test cases cho luong Users"""
    print("\n" + "="*60)
    print("[TEST] BAT DAU CHAY TEST LUONG USERS")
    print("="*60 + "\n")
    
    # Tạo folder kết quả nếu chưa có
    if not os.path.exists(users_report_dir):
        os.makedirs(users_report_dir)
    
    # Tự động tìm tất cả các Test Case trong folder users
    loader = unittest.TestLoader()
    suite = loader.discover(start_dir=users_test_dir, pattern='test_suite_*.py')
    
    # Cấu hình & Chạy Test Runner xuất HTML
    runner = HTMLTestRunner(
        output=users_report_dir,
        report_name="Users_Module_Report",
        report_title="Bao Cao Kiem Thu Tu Dong - Luong Nguoi Dung",
        descriptions="Kiem thu luong nguoi dung: Login, Signup, Filter, Detail, Cart, Payment",
        combine_reports=True,
        add_timestamp=True,
        open_in_browser=False
    )
    
    result = runner.run(suite)
    return result


def run_admin_tests():
    """Chay tat ca test cases cho luong Admin"""
    print("\n" + "="*60)
    print("[TEST] BAT DAU CHAY TEST LUONG ADMIN")
    print("="*60 + "\n")
    
    # Tạo folder kết quả nếu chưa có
    if not os.path.exists(admin_report_dir):
        os.makedirs(admin_report_dir)
    
    # Tự động tìm tất cả các Test Case trong folder admin
    loader = unittest.TestLoader()
    suite = loader.discover(start_dir=admin_test_dir, pattern='test_suite_*.py')
    
    # Cấu hình & Chạy Test Runner xuất HTML
    runner = HTMLTestRunner(
        output=admin_report_dir,
        report_name="Admin_Module_Report",
        report_title="Bao Cao Kiem Thu Tu Dong - Luong Quan Tri",
        descriptions="Kiem thu luong admin: Dashboard, Products, Categories, Orders, Users, Reviews",
        combine_reports=True,
        add_timestamp=True,
        open_in_browser=False
    )
    
    result = runner.run(suite)
    return result


def print_summary(users_result, admin_result):
    """In tong ket ket qua test"""
    print("\n" + "="*60)
    print("[SUMMARY] TONG KET KET QUA KIEM THU")
    print("="*60)
    
    # Thống kê Users
    if users_result:
        users_total = users_result.testsRun
        users_failures = len(users_result.failures)
        users_errors = len(users_result.errors)
        users_skipped = len(users_result.skipped)
        users_passed = users_total - users_failures - users_errors - users_skipped
        
        print(f"\n[USERS] LUONG USERS:")
        print(f"   [PASS]    Passed:  {users_passed}")
        print(f"   [FAIL]    Failed:  {users_failures}")
        print(f"   [ERROR]   Errors:  {users_errors}")
        print(f"   [SKIP]    Skipped: {users_skipped}")
        print(f"   [TOTAL]   Total:   {users_total}")
        print(f"   [REPORT]  Report:  {users_report_dir}")
    
    # Thống kê Admin
    if admin_result:
        admin_total = admin_result.testsRun
        admin_failures = len(admin_result.failures)
        admin_errors = len(admin_result.errors)
        admin_skipped = len(admin_result.skipped)
        admin_passed = admin_total - admin_failures - admin_errors - admin_skipped
        
        print(f"\n[ADMIN] LUONG ADMIN:")
        print(f"   [PASS]    Passed:  {admin_passed}")
        print(f"   [FAIL]    Failed:  {admin_failures}")
        print(f"   [ERROR]   Errors:  {admin_errors}")
        print(f"   [SKIP]    Skipped: {admin_skipped}")
        print(f"   [TOTAL]   Total:   {admin_total}")
        print(f"   [REPORT]  Report:  {admin_report_dir}")
    
    print("\n" + "="*60)
    print("[DONE] HOAN TAT KIEM THU!")
    print("="*60 + "\n")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Chay kiem thu tu dong cho Web The Thao')
    parser.add_argument('--users', action='store_true', help='Chi chay test luong Users')
    parser.add_argument('--admin', action='store_true', help='Chi chay test luong Admin')
    parser.add_argument('--all', action='store_true', help='Chay tat ca test (mac dinh)')
    
    args = parser.parse_args()
    
    users_result = None
    admin_result = None
    
    # Nếu không có tham số nào, chạy tất cả
    if not args.users and not args.admin:
        args.all = True
    
    # Chạy test theo tham số
    if args.users or args.all:
        users_result = run_users_tests()
    
    if args.admin or args.all:
        admin_result = run_admin_tests()
    
    # In tổng kết
    print_summary(users_result, admin_result)
    
    # Mở báo cáo trong browser (file mới nhất)
    import glob
    import webbrowser
    
    if args.users or args.all:
        users_reports = glob.glob(os.path.join(users_report_dir, '*.html'))
        if users_reports:
            latest_users_report = max(users_reports, key=os.path.getctime)
            webbrowser.open('file://' + latest_users_report)
    
    if args.admin or args.all:
        admin_reports = glob.glob(os.path.join(admin_report_dir, '*.html'))
        if admin_reports:
            latest_admin_report = max(admin_reports, key=os.path.getctime)
            webbrowser.open('file://' + latest_admin_report)