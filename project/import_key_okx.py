# -*- coding: utf-8 -*-
import encoding_fix  # BẮT BUỘC: Fix lỗi font chữ trên Windows
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
import time

def run(profile_data):
    """
    Script automation cho ví OKX với cơ chế xác thực cửa sổ cực kỳ mạnh mẽ.
    """
    PROJECT_NAME = "OKX"
    print(f">>> [{PROJECT_NAME}] Bắt đầu kết nối tới: {profile_data['remote_debugging_address']}...")
    
    driver = None
    
    def get_all_windows_info():
        info = []
        try:
            handles = driver.window_handles
            for h in handles:
                try:
                    driver.switch_to.window(h)
                    info.append({"handle": h, "url": driver.current_url, "title": driver.title})
                except:
                    info.append({"handle": h, "url": "ERROR", "title": "ERROR"})
        except:
            pass
        return info

    def find_and_switch_to_ui(silent=False):
        """Tìm tab extension OKX có giao diện người dùng thực sự"""
        try:
            handles = driver.window_handles
            if not silent: print(f">>> [{PROJECT_NAME}] Đang kiểm tra {len(handles)} cửa sổ...")
            
            for h in handles:
                try:
                    driver.switch_to.window(h)
                    url = driver.current_url
                    if not silent: print(f">>> [{PROJECT_NAME}] - Cửa sổ {h[:8]}: {url}")
                    
                    if "mcohilncbfahbmgdjkbpemcciiolgcge" in url:
                        # Loại trừ các trang chạy ngầm
                        if any(x in url for x in ["offscreen.html", "background.html", "generated_background"]):
                            continue
                        # Chấp nhận nếu là popup, initialize hoặc trang chính của extension
                        if any(x in url for x in ["popup.html", "initialize", "home.html", "notification.html", "index.html"]):
                            if not silent: print(f">>> [{PROJECT_NAME}] ==> Đã xác định tab UI OKX: {h[:8]}")
                            return True
                except:
                    continue
        except Exception as e:
            if not silent: print(f">>> [{PROJECT_NAME}] Lỗi khi duyệt handles: {e}")
        return False

    def wait_for_element_safe(xpath, timeout=20, name="Element"):
        """Chờ element xuất hiện một cách an toàn, tự động khôi phục handle nếu mất"""
        print(f">>> [{PROJECT_NAME}] Đang tìm {name}...")
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                # Kiểm tra xem còn ở đúng tab không
                try:
                    curr_url = driver.current_url
                    if "mcohilncbfahbmgdjkbpemcciiolgcge" not in curr_url:
                        find_and_switch_to_ui(silent=True)
                except:
                    find_and_switch_to_ui(silent=True)
                
                # Tìm element
                elements = driver.find_elements(By.XPATH, xpath)
                if elements and len(elements) > 0:
                    el = elements[0]
                    if el.is_displayed() and el.is_enabled():
                        return el
            except Exception as e:
                # Nếu mất kết nối hoàn toàn, thử tìm lại UI
                find_and_switch_to_ui(silent=True)
            
            time.sleep(1)
        
        raise TimeoutException(f"Không tìm thấy {name} sau {timeout}s (XPath: {xpath})")

    try:
        # Bước 1: Khởi tạo Driver
        chrome_options = Options()
        chrome_options.add_experimental_option("debuggerAddress", profile_data['remote_debugging_address'])
        driver_path = profile_data.get('driver_path')
        
        if driver_path:
            service = Service(executable_path=driver_path)
            driver = webdriver.Chrome(service=service, options=chrome_options)
        else:
            driver = webdriver.Chrome(options=chrome_options)

        print(f">>> [{PROJECT_NAME}] WebDriver kết nối thành công!")

        # Bước 2: Tìm tab extension
        if not find_and_switch_to_ui():
            print(f">>> [{PROJECT_NAME}] Chưa có tab OKX UI. Đang mở mới...")
            target_url = "chrome-extension://mcohilncbfahbmgdjkbpemcciiolgcge/popup.html#/initialize"
            driver.execute_script(f"window.open('{target_url}', '_blank');")
            time.sleep(2)
            if not find_and_switch_to_ui():
                print(f">>> [{PROJECT_NAME}] [ERROR] Không thể tìm thấy tab extension sau khi mở!")
                return

        # Bước 3: Thao tác Import Wallet
        import_wallet_xpath = '//*[@data-testid="onboard-page-import-wallet-button"]'
        btn = wait_for_element_safe(import_wallet_xpath, name="Nút Import Wallet")
        driver.execute_script("arguments[0].click();", btn)
        print(f">>> [{PROJECT_NAME}] Đã click 'Import Wallet'.")
        time.sleep(1)

        # Bước 4: Thao tác Seed Phrase
        import_type_xpath = '//*[@data-testid="onboard-page-import-seed-phrase-or-private-key"]'
        btn = wait_for_element_safe(import_type_xpath, name="Nút Seed Phrase")
        driver.execute_script("arguments[0].click();", btn)
        print(f">>> [{PROJECT_NAME}] Đã click 'Import Seed Phrase'.")
        time.sleep(1)

        # Bước 5: Nhập 12 từ Mnemonic
        print(f">>> [{PROJECT_NAME}] Đang chuẩn bị nhập 12 từ mnemonic...")
        mnemonic_phrase = "buddy off slide lounge hurry ankle base spoon video coconut surge hover"
        words = mnemonic_phrase.split()
        
        input_xpath = '//*[@class="mnemonic-words-inputs__container__input"]'
        # Chờ ô đầu tiên xuất hiện
        wait_for_element_safe(input_xpath, name="Ô nhập mnemonic")
        
        for i, word in enumerate(words):
            # Lấy list inputs mới để tránh stale
            inputs = driver.find_elements(By.XPATH, input_xpath)
            if i < len(inputs):
                inputs[i].send_keys(word)
                print(f">>> [{PROJECT_NAME}] Đã nhập từ #{i+1}: {word}")
            else:
                print(f">>> [{PROJECT_NAME}] [WARNING] Không tìm thấy ô nhập thứ {i+1}")
        
        # Bước 6: Click Xác nhận
        confirm_btn_xpath = '//*[@data-testid="import-seed-phrase-or-private-key-page-confirm-button"]'
        btn = wait_for_element_safe(confirm_btn_xpath, name="Nút Xác nhận Key")
        driver.execute_script("arguments[0].click();", btn)
        print(f">>> [{PROJECT_NAME}] Đã click 'Xác nhận'.")

        # Bước 7: Bảo mật (Password)
        security_xpath = '//*[@class="_item_16nvb_22 _item-select_16nvb_39"]'
        btn = wait_for_element_safe(security_xpath, name="Chọn bảo mật Password")
        driver.execute_script("arguments[0].click();", btn)
        
        next_btn_xpath = '//*[@class="okui-button-var okui-btn btn-lg btn-fill-highlight block mobile"]'
        btn = wait_for_element_safe(next_btn_xpath, name="Nút Tiếp theo (Bảo mật)")
        driver.execute_script("arguments[0].click();", btn)
        print(f">>> [{PROJECT_NAME}] Đã chọn Password và Tiếp theo.")

        # Bước 8: Nhập mật khẩu
        password = "AlanTruong@113"
        pass_input_xpath = '//input[@type="password"]'
        wait_for_element_safe(pass_input_xpath, name="Ô nhập mật khẩu")
        inputs = driver.find_elements(By.XPATH, pass_input_xpath)
        if len(inputs) < 2:
            inputs = driver.find_elements(By.XPATH, '//input')
            
        for i in range(min(2, len(inputs))):
            inputs[i].send_keys(password)
        print(f">>> [{PROJECT_NAME}] Đã nhập mật khẩu.")

        # Click Xác nhận mật khẩu
        btn = wait_for_element_safe(next_btn_xpath, name="Nút Xác nhận mật khẩu")
        driver.execute_script("arguments[0].click();", btn)

        # Bước 9: Bắt đầu hành trình
        start_xpath = '//*[text()="Bắt đầu hành trình Web3 của bạn"]'
        btn = wait_for_element_safe(start_xpath, name="Nút Bắt đầu hành trình")
        driver.execute_script("arguments[0].click();", btn)

        # Bước 10: Kiểm tra hoàn tất
        finish_xpath = '//*[text()="Tài khoản 01"]'
        wait_for_element_safe(finish_xpath, timeout=10, name="Chỉ báo hoàn thành (Tài khoản 01)")
        print(f">>> [SUCCESS] Hoàn tất setup OKX!")
        
        time.sleep(5)

    except Exception as e:
        print(f">>> [ERROR] Lỗi thực thi: {e}")
        try:
            driver.save_screenshot(f"error_okx_{int(time.time())}.png")
        except:
            pass
        raise
    finally:
        if driver:
            print(f">>> [{PROJECT_NAME}] Đang dọn dẹp và đóng trình duyệt...")
            try:
                # Cố gắng đóng tất cả các cửa sổ trước khi quit
                handles = driver.window_handles
                for h in handles:
                    try:
                        driver.switch_to.window(h)
                        driver.close()
                    except:
                        pass
                driver.quit()
            except:
                pass

if __name__ == "__main__":
    test_data = {"remote_debugging_address": "127.0.0.1:9222"}
    # run(test_data)
