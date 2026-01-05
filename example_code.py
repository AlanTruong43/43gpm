# -*- coding: utf-8 -*-
"""
Generic Automation Template
Bản mẫu chuẩn cho các dự án automation sử dụng 43GPM và Selenium.
"""
import encoding_fix  # Fix Windows console encoding - must be first import

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time


def run(profile_data):
    """
    Main function to run the automation task.
    
    Args:
        profile_data: Dict containing:
            - profile_id: Profile ID
            - profile_name: Profile name
            - remote_debugging_address: e.g., "127.0.0.1:53378"
            - browser_location: Path to browser executable
            - driver_path: Path to ChromeDriver
    """
    PROJECT_NAME = "EXAMPLE"  # Thay tên dự án của bạn ở đây
    print(f">>> [{PROJECT_NAME}] Connecting to browser at: {profile_data['remote_debugging_address']}...")
    
    driver = None
    
    try:
        # Connect to the already opened browser profile
        chrome_options = Options()
        chrome_options.add_experimental_option(
            "debuggerAddress", 
            profile_data['remote_debugging_address']
        )
        
        print(f">>> [{PROJECT_NAME}] Initializing WebDriver (Connecting to browser)...")
        try:
            from selenium.webdriver.chrome.service import Service
            
            # Using specific driver_path from GPM if available
            driver_path = profile_data.get('driver_path')
            if driver_path:
                print(f">>> [{PROJECT_NAME}] Using specific driver: {driver_path}")
                service = Service(executable_path=driver_path)
                driver = webdriver.Chrome(service=service, options=chrome_options)
            else:
                print(f">>> [{PROJECT_NAME}] Using default system driver")
                driver = webdriver.Chrome(options=chrome_options)
                
        except Exception as chrome_err:
            print(f">>> [ERROR] Selenium could not connect to browser: {chrome_err}")
            print(">>> [TIP] Có thể driver_path không đúng hoặc trình duyệt chưa hỗ trợ Remote Debugging.")
            return
            
        print(f">>> [{PROJECT_NAME}] WebDriver initialized successfully!")
        
        # Step 0: Ensure we are using the correct window/tab
        print(f">>> [{PROJECT_NAME}] Scanning for a valid browser tab...")
        all_handles = driver.window_handles
        target_handle = None
        
        for handle in all_handles:
            driver.switch_to.window(handle)
            current_url = driver.current_url
            print(f">>> [{PROJECT_NAME}] Window {handle[:8]}: {current_url}")
            
            # Skip extension background pages and other internal chrome pages
            if not current_url.startswith("chrome-extension://") and not current_url.startswith("chrome://"):
                target_handle = handle
                break
        
        if not target_handle:
            print(f">>> [{PROJECT_NAME}] No active web tab found. Creating a new one...")
            driver.execute_script("window.open('about:blank', '_blank');")
            driver.switch_to.window(driver.window_handles[-1])
        else:
            print(f">>> [{PROJECT_NAME}] Selected valid tab: {driver.current_url}")
        
        # --- BẮT ĐẦU THỰC HIỆN CÁC BƯỚC AUTOMATION TẠI ĐÂY ---
        # Ví dụ: 
        # driver.get("https://google.com")
        # print(f">>> [{PROJECT_NAME}] Navigation complete!")
        
        print(f">>> [SUCCESS] Sẵn sàng để viết code cho dự án {PROJECT_NAME} tiếp theo.")

    except Exception as e:
        print(f">>> [ERROR] {PROJECT_NAME} failed: {e}")
        raise
    finally:
        if driver:
            print(f">>> [INFO] Tác vụ kết thúc. Trình duyệt vẫn đang mở.")

if __name__ == "__main__":
    # Test block - Dùng để chạy thử trực tiếp file này
    test_profile_data = {
        "remote_debugging_address": "127.0.0.1:9222", # Thay port thực tế của bạn
        "driver_path": ""
    }
    # run(test_profile_data)
