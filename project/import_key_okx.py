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
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("OKX_Auto")

def run(profile_data):
    """
    Script automation cho ví OKX tối ưu tốc độ và độ ổn định.
    """
    PROJECT_NAME = "OKX (v2.1)"
    mnemonic_phrase = profile_data.get('mnemonic', "buddy off slide lounge hurry ankle base spoon video coconut surge hover")
    password = profile_data.get('password', "AlanTruong@113")
    debug_address = profile_data.get('remote_debugging_address')
    
    logger.info(f">>> [{PROJECT_NAME}] Bắt đầu: {debug_address}...")
    
    driver = None
    
    def init_driver(address, path, retries=5):
        """Khởi tạo Driver với cơ chế thử lại nếu port chưa sẵn sàng"""
        for i in range(retries):
            try:
                opts = Options()
                opts.add_experimental_option("debuggerAddress", address)
                # Tăng timeout kết nối
                # opts.add_argument("--proxy-server='direct://'")
                # opts.add_argument("--proxy-bypass-list=*")
                
                service = Service(executable_path=path) if path else Service()
                d = webdriver.Chrome(service=service, options=opts)
                # Test thử kết nối
                d.current_url
                return d
            except Exception as e:
                logger.warning(f"Thử kết nối lần {i+1} thất bại: {str(e)[:100]}")
                time.sleep(2)
        raise Exception(f"Không thể kết nối tới trình duyệt tại {address} sau {retries} lần thử.")

    def find_and_switch_to_ui(silent=False):
        """Tìm tab extension OKX một cách bền bỉ"""
        try:
            handles = driver.window_handles
            if not silent: logger.info(f"[{PROJECT_NAME}] Quét {len(handles)} cửa sổ...")
            
            for h in handles:
                try:
                    driver.switch_to.window(h)
                    url = driver.current_url
                    if "mcohilncbfahbmgdjkbpemcciiolgcge" in url:
                        if any(x in url for x in ["offscreen.html", "background.html", "generated_background"]):
                            continue
                        return True
                except:
                    continue
        except Exception as e:
            if not silent: logger.error(f"Lỗi khi duyệt handles: {e}")
        return False

    def wait_for_element_safe(xpaths, timeout=15, name="Element"):
        """Chờ element với danh sách XPaths dự phòng"""
        if isinstance(xpaths, str):
            xpaths = [xpaths]
            
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                # Đảm bảo handle vẫn sống
                try: driver.current_url
                except: find_and_switch_to_ui(silent=True)

                for xpath in xpaths:
                    elements = driver.find_elements(By.XPATH, xpath)
                    for el in elements:
                        if el.is_displayed():
                            return el
            except:
                find_and_switch_to_ui(silent=True)
            time.sleep(0.5)
        raise TimeoutException(f"Không tìm thấy {name}")

    def inject_mnemonic_js(phrase):
        """Dán mnemonic cực nhanh và trigger sự kiện React"""
        js_code = """
        const phrase = arguments[0];
        // Tìm bất kỳ input nào có vẻ là mnemonic hoặc input đầu tiên
        const inputs = document.querySelectorAll('input') || [];
        const input = Array.from(inputs).find(i => i.placeholder?.includes('word') || i.className?.includes('mnemonic') || true);
        
        if (input) {
            input.focus();
            const dataTransfer = new DataTransfer();
            dataTransfer.setData('text/plain', phrase);
            const event = new ClipboardEvent('paste', {
                clipboardData: dataTransfer,
                bubbles: true,
                cancelable: true
            });
            input.dispatchEvent(event);
            
            // Fallback: Dispatch input event cho từng từ nếu paste bị chặn
            setTimeout(() => {
                if (input.value === '') {
                   input.value = phrase.split(' ')[0];
                   input.dispatchEvent(new Event('input', { bubbles: true }));
                }
            }, 100);
            return true;
        }
        return false;
        """
        try:
            return driver.execute_script(js_code, phrase)
        except Exception as e:
            logger.error(f"Lỗi JS Injection: {e}")
            return False

    try:
        driver = init_driver(debug_address, profile_data.get('driver_path'))

        # Bước 1: Điều hướng tới OKX
        if not find_and_switch_to_ui():
            target_url = "chrome-extension://mcohilncbfahbmgdjkbpemcciiolgcge/popup.html#/initialize"
            driver.execute_script(f"window.open('{target_url}', '_blank');")
            time.sleep(1)
            if not find_and_switch_to_ui():
                raise Exception("Không tìm thấy giao diện OKX")

        # Bước 2: Bấm Import (Xử lý cả trường hợp đã ở màn hình trong)
        try:
            import_btn = wait_for_element_safe([
                '//*[@data-testid="onboard-page-import-wallet-button"]',
                '//*[text()="Import wallet" or text()="Nhập ví"]',
                '//button[contains(., "Import")]'
            ], timeout=7, name="Nút Import")
            driver.execute_script("arguments[0].click();", import_btn)
        except:
            logger.info("Có thể đã qua bước Import, tiếp tục...")

        # Bước 3: Chọn Seed Phrase
        try:
            seed_btn = wait_for_element_safe([
                '//*[@data-testid="onboard-page-import-seed-phrase-or-private-key"]',
                '//*[contains(text(), "Seed phrase") or contains(text(), "Cụm từ")]'
            ], timeout=7, name="Nút Seed Phrase")
            driver.execute_script("arguments[0].click();", seed_btn)
        except:
            logger.info("Có thể đã ở trang nhập Key, tiếp tục...")

        # Bước 4: Nhập Key (JS Injection)
        logger.info(f"[{PROJECT_NAME}] Đang nhập mnemonic...")
        time.sleep(1) # Chờ animation
        wait_for_element_safe('//input', timeout=10, name="Các ô nhập Key")
        
        if inject_mnemonic_js(mnemonic_phrase):
            logger.info("Dã tiêm JS nhập Key thành công.")
        else:
            raise Exception("Không thể thực hiện JS Injection")

        # Bước 5: Xác nhận
        confirm_btn = wait_for_element_safe([
            '//*[@data-testid="import-seed-phrase-or-private-key-page-confirm-button"]',
            '//button[@type="submit"]',
            '//button[contains(., "Confirm") or contains(., "Xác nhận")]'
        ], name="Nút Xác nhận Key")
        driver.execute_script("arguments[0].click();", confirm_btn)

        # Bước 6: Password
        # Chọn "Password" nếu có danh sách lựa chọn
        try:
            pass_type = wait_for_element_safe('//*[contains(@class, "item") and contains(., "Password")]', timeout=5, name="Chọn Password")
            driver.execute_script("arguments[0].click();", pass_type)
            wait_for_element_safe('//button[contains(., "Next") or contains(., "Tiếp tục")]').click()
        except: pass

        # Nhập pass
        pass_inputs = wait_for_element_safe('//input[@type="password"]', timeout=10, name="Ô nhập mật khẩu")
        inputs = driver.find_elements(By.XPATH, '//input[@type="password"]')
        for inp in inputs:
            inp.send_keys(password)
        
        # Click Final
        final_btn = wait_for_element_safe('//button[contains(@class, "btn-fill-highlight") or contains(., "Confirm")]', name="Xác nhận cuối")
        driver.execute_script("arguments[0].click();", final_btn)

        # Bước 7: Bắt đầu
        start_btn = wait_for_element_safe('//*[contains(text(), "Bắt đầu") or contains(text(), "Start")]', timeout=10, name="Bắt đầu hành trình")
        driver.execute_script("arguments[0].click();", start_btn)

        logger.info(f">>> [SUCCESS] Hoàn tất cho profile: {profile_data.get('profile_id')}")

    except Exception as e:
        logger.error(f">>> [ERROR] Thất bại: {str(e)}")
        # Có thể chụp ảnh màn hình lỗi ở đây nếu cần
        raise
    finally:
        if driver:
            try: driver.quit()
            except: pass

if __name__ == "__main__":
    run({"remote_debugging_address": "127.0.0.1:9222", "mnemonic": "test test test", "profile_id": "test"})

if __name__ == "__main__":
    # Test sample
    run({"remote_debugging_address": "127.0.0.1:9222", "mnemonic": "từ_1 từ_2 ...", "profile_id": "test"})
