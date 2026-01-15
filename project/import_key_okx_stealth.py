# -*- coding: utf-8 -*-
import json
import time
import requests
import websocket
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("OKX_Stealth")

def run(profile_data):
    """
    Script automation cho ví OKX dùng Raw CDP (Chrome DevTools Protocol)
    KHÔNG DÙNG SELENIUM - Bypass hoàn toàn lỗi tự đóng profile của OKX.
    """
    PROJECT_NAME = "OKX (Stealth Mode)"
    mnemonic_phrase = profile_data.get('mnemonic', "buddy off slide lounge hurry ankle base spoon video coconut surge hover")
    password = profile_data.get('password', "AlanTruong@113")
    debug_address = profile_data.get('remote_debugging_address') # e.g. 127.0.0.1:9222
    
    logger.info(f">>> [{PROJECT_NAME}] Bắt đầu kết nối tới: {debug_address}...")
    
    def send_cdp_command(ws, method, params=None):
        msg_id = int(time.time() * 1000)
        message = {
            "id": msg_id,
            "method": method,
            "params": params or {}
        }
        ws.send(json.dumps(message))
        # Chờ kết quả phản hồi đúng ID
        while True:
            res = json.loads(ws.recv())
            if res.get('id') == msg_id:
                return res
            # Bỏ qua các events notification khác (như console.log)

    def evaluate_js(ws, code):
        """Thực thi mã Javascript và trả về giá trị thực tế"""
        res = send_cdp_command(ws, "Runtime.evaluate", {
            "expression": code,
            "userGesture": True,
            "awaitPromise": True,
            "returnByValue": True
        })
        # Log lỗi nếu có
        if "exceptionDetails" in res.get("result", {}):
            logger.error(f"JS Error: {res['result']['exceptionDetails']}")
            return None
            
        val = res.get('result', {}).get('result', {}).get('value')
        return val

    def wait_for_element_and_click(ws, selector, timeout=12, name="Element"):
        """Đợi element xuất hiện và click, trả về True nếu thành công"""
        logger.info(f"Đang tìm và click {name} ({selector})...")
        start = time.time()
        while time.time() - start < timeout:
            # Script tìm element thông minh (selector hoặc text)
            click_js = f"""
            (function() {{
                const el = document.querySelector('{selector}') || 
                           Array.from(document.querySelectorAll('button, div, span')).find(e => e.textContent.trim().toLowerCase().includes('{selector.lower()}'));
                if (el && el.offsetHeight > 0) {{
                    el.click();
                    return true;
                }}
                return false;
            }})()
            """
            if evaluate_js(ws, click_js) == True:
                return True
            time.sleep(1)
        logger.error(f"Timeout: Không thể click {name}")
        return False

    try:
        # Bước 1: Tìm Tab OKX qua API /json
        json_url = f"http://{debug_address}/json"
        target_ws_url = None
        
        for i in range(15):
            try:
                tabs = requests.get(json_url, timeout=5).json()
                for tab in tabs:
                    if "mcohilncbfahbmgdjkbpemcciiolgcge" in tab.get('url', '') and "background" not in tab.get('url', ''):
                        target_ws_url = tab.get('webSocketDebuggerUrl')
                        break
                if target_ws_url: break
                logger.info(f"Đang quét tab OKX (Lần {i+1})...")
            except: pass
            time.sleep(2)
            
        if not target_ws_url:
            # Cố mở trang initialize nếu không thấy
            logger.info("Mở tab OKX mới...")
            try:
                tabs = requests.get(json_url).json()
                ws_temp = create_ws_connection(tabs[0].get('webSocketDebuggerUrl'))
                evaluate_js(ws_temp, "window.open('chrome-extension://mcohilncbfahbmgdjkbpemcciiolgcge/popup.html#/initialize', '_blank')")
                ws_temp.close()
                time.sleep(3)
                tabs = requests.get(json_url).json()
                target_ws_url = next((t['webSocketDebuggerUrl'] for t in tabs if "mcohilncbfahbmgdjkbpemcciiolgcge" in t['url']), None)
            except: pass

        if not target_ws_url: raise Exception("Không tìm thấy Tab OKX")

        ws = create_ws_connection(target_ws_url)
        logger.info("Kết nối Stealth CDP thành công!")

        # Bước 3 + 4: Điều hướng tới trang nhập Key
        if not wait_for_element_and_click(ws, "import-wallet-button", name="Nút Import"):
            # Thử phương án dự phòng nếu đang ở màn hình khác
            wait_for_element_and_click(ws, "seed-phrase", name="Nút Seed Phrase")

        wait_for_element_and_click(ws, "import-seed-phrase-or-private-key", name="Nút Import Key")
        time.sleep(2)

        # Bước 5: Nhập Mnemonic (PHƯƠNG PHÁP SIÊU BỀN)
        logger.info("Bắt đầu tiêm Mnemonic...")
        # Sử dụng cơ chế mô phỏng Paste sâu vào React state
        inject_js = f"""
        (function() {{
            const phrase = "{mnemonic_phrase}";
            const input = document.querySelector('input') || document.querySelector('.mnemonic-words-inputs__container__input');
            if (!input) return "ERR_NO_INPUT";
            
            input.focus();
            input.value = ""; // Clear cũ
            
            // Tạo sự kiện dán giả lập
            const dataTransfer = new DataTransfer();
            dataTransfer.setData('text/plain', phrase);
            const pasteEvent = new ClipboardEvent('paste', {{
                clipboardData: dataTransfer,
                bubbles: true, cancelable: true
            }});
            input.dispatchEvent(pasteEvent);
            
            // Nếu Paste không kích hoạt tự điền 12 ô (do OKX chặn), ta điền thủ công vào từng ô
            const allInputs = document.querySelectorAll('input.mnemonic-words-inputs__container__input');
            if (allInputs.length > 1) {{
                const words = phrase.split(' ');
                allInputs.forEach((inp, idx) => {{
                    if (words[idx]) {{
                        inp.value = words[idx];
                        inp.dispatchEvent(new Event('input', {{ bubbles: true }}));
                        inp.dispatchEvent(new Event('change', {{ bubbles: true }}));
                    }}
                }});
            }} else {{
                // Chỉ có 1 ô (có thể là trang nhập private key hoặc ô nhập chung)
                input.value = phrase;
                input.dispatchEvent(new Event('input', {{ bubbles: true }}));
            }}
            
            return "DONE_INJECT";
        }})()
        """
        result = evaluate_js(ws, inject_js)
        logger.info(f"Kết quả Injection: {result}")
        time.sleep(1)

        # Bước 6: Xác nhận Verify
        if not wait_for_element_and_click(ws, "confirm-button", name="Xác nhận Key"):
            # Thử click theo text nếu selector test-id thay đổi
            evaluate_js(ws, "Array.from(document.querySelectorAll('button')).find(b => b.textContent.includes('Confirm') || b.textContent.includes('Xác nhận'))?.click()")
        
        time.sleep(2)

        # Bước 7 + 8: Password
        logger.info("Thiết lập Password...")
        # Chọn Password mode (nếu có lựa chọn)
        evaluate_js(ws, "Array.from(document.querySelectorAll('div')).find(e => e.textContent.includes('Password'))?.click()")
        time.sleep(0.5)
        evaluate_js(ws, "Array.from(document.querySelectorAll('button')).find(e => e.textContent.includes('Next') || e.textContent.includes('Tiếp')).click()")
        time.sleep(1)

        # Điền mật khẩu
        set_pass_js = f"""
        (function() {{
            const ps = "{password}";
            const inputs = document.querySelectorAll('input[type="password"]');
            inputs.forEach(i => {{
                i.value = ps;
                i.dispatchEvent(new Event('input', {{ bubbles: true }}));
                i.dispatchEvent(new Event('change', {{ bubbles: true }}));
            }});
            return inputs.length;
        }})()
        """
        num_pass = evaluate_js(ws, set_pass_js)
        logger.info(f"Đã điền mật khẩu vào {num_pass} ô.")
        
        wait_for_element_and_click(ws, "confirm", name="Xác nhận mật khẩu")
        time.sleep(3)

        # Bước 9: Finish
        wait_for_element_and_click(ws, "start", name="Bắt đầu hành trình")
        
        logger.info(f">>> [SUCCESS] Hoàn tất nạp ví OKX cho profile {profile_data.get('profile_id')}!")
        ws.close()

    except Exception as e:
        logger.error(f">>> [ERROR] Lỗi Stealth CDP: {e}")
        raise

if __name__ == "__main__":
    # Test local
    run({"remote_debugging_address": "127.0.0.1:9222", "mnemonic": "test test test", "profile_id": "test"})
