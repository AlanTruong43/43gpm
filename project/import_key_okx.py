# -*- coding: utf-8 -*-
import encoding_fix  # BẮT BUỘC: Fix lỗi font chữ trên Windows
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time

def run(profile_data):
    """
    Script automation cho ví OKX dựa trên quy trình:
    1. Truy cập chrome-extension://mcohilncbfahbmgdjkbpemcciiolgcge/popup.html#/initialize
    2. Click Import Wallet
    3. Click Seed Phrase or Private Key
    """
    print(f">>> [OKX] Đang kết nối tới trình duyệt: {profile_data['remote_debugging_address']}...")
    
    driver = None
    try:
        # Bước 1: Kết nối Driver
        chrome_options = Options()
        chrome_options.add_experimental_option("debuggerAddress", profile_data['remote_debugging_address'])
        
        driver_path = profile_data.get('driver_path')
        if driver_path:
            service = Service(executable_path=driver_path)
            driver = webdriver.Chrome(service=service, options=chrome_options)
        else:
            driver = webdriver.Chrome(options=chrome_options)

        print(">>> [OKX] Đã kết nối Driver thành công.")

        # Bước 2: Điều hướng
        # Thử dùng home.html thay vì popup.html để ổn định hơn
        target_url = "chrome-extension://mcohilncbfahbmgdjkbpemcciiolgcge/home.html#/initialize"
        print(f">>> [OKX] Đang điều hướng tới: {target_url}")
        
        # Mở URL trong tab hiện tại
        driver.get(target_url)
        time.sleep(5) # Chờ trang ổn định

        # KIỂM TRA LỖI: Xem trình duyệt còn sống không
        try:
            print(f">>> [OKX] Cửa sổ hiện tại: {driver.current_url}")
        except Exception as conn_err:
            print(f">>> [ERROR] Trình duyệt đã bị đóng ngay sau khi Get URL: {conn_err}")
            return

        wait = WebDriverWait(driver, 20)

        # Bước 2: Click "Import Wallet"
        print(">>> [OKX] Đang tìm nút Import Wallet...")
        try:
            # Kiểm tra xem có cửa sổ mới nào hiện ra không (OKX có thể nhảy cửa sổ)
            all_handles = driver.window_handles
            if len(all_handles) > 1:
                print(">>> [OKX] Phát hiện nhiều cửa sổ, đang tìm cửa sổ OKX...")
                for hh in all_handles:
                    driver.switch_to.window(hh)
                    if "mcohilncbfahbmgdjkbpemcciiolgcge" in driver.current_url:
                        print(f">>> [OKX] Đã chuyển sang cửa sổ: {driver.current_url}")
                        break

            btn_xpath = '//*[@data-testid="onboard-page-import-wallet-button"]'
            import_wallet_btn = wait.until(EC.presence_of_element_located((By.XPATH, btn_xpath)))
            
            # Cuộn tới nút trước khi click
            driver.execute_script("arguments[0].scrollIntoView(true);", import_wallet_btn)
            time.sleep(1)
            
            # Click bằng JS để tránh trigger native event gây crash
            driver.execute_script("arguments[0].click();", import_wallet_btn)
            print(">>> [OKX] Đã click 'Import Wallet'.")
            time.sleep(3)
        except Exception as e:
            print(f">>> [ERROR] Lỗi tại bước Import Wallet: {e}")
            return

        # Bước 3: Click "Import Seed Phrase or Private Key"
        print(">>> [OKX] Đang tìm nút Seed Phrase / Private Key...")
        try:
            type_xpath = '//*[@data-testid="onboard-page-import-seed-phrase-or-private-key"]'
            import_type_btn = wait.until(EC.presence_of_element_located((By.XPATH, type_xpath)))
            driver.execute_script("arguments[0].click();", import_type_btn)
            print(">>> [OKX] Đã click 'Import Seed Phrase or Private Key'.")
        except Exception as e:
            print(f">>> [ERROR] Lỗi tại bước chọn loại Import: {e}")
            return

        print(">>> [OKX] Hoàn thành các bước bạn yêu cầu.")

    except Exception as e:
        print(f">>> [ERROR] Lỗi thực thi script OKX: {e}")
    finally:
        print(">>> [INFO] Kết thúc luồng script OKX.")

if __name__ == "__main__":
    # Fake data để test nếu cần
    pass
