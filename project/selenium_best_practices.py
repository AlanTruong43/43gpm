# -*- coding: utf-8 -*-
"""
SELENIUM BEST PRACTICES GUIDE
Hướng dẫn chuẩn để viết code Selenium cho mọi project

Author: Reference Guide
Date: 2025
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException, 
    NoSuchElementException,
    StaleElementReferenceException,
    ElementClickInterceptedException
)
import time


# ============================================================================
# 1. KHỞI TẠO DRIVER (INITIALIZATION)
# ============================================================================

def init_driver_basic():
    """Cách 1: Khởi tạo driver cơ bản"""
    chrome_options = Options()
    driver = webdriver.Chrome(options=chrome_options)
    return driver


def init_driver_headless():
    """Cách 2: Chạy ở chế độ headless (không hiển thị browser)"""
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(options=chrome_options)
    return driver


def init_driver_with_profile():
    """Cách 3: Khởi tạo với user profile (giữ cookies, login)"""
    chrome_options = Options()
    chrome_options.add_argument(r"user-data-dir=C:\Path\To\Chrome\Profile")
    chrome_options.add_argument("profile-directory=Profile 1")
    driver = webdriver.Chrome(options=chrome_options)
    return driver


def init_driver_remote_debug():
    """Cách 4: Kết nối với browser đang mở (Remote Debugging)"""
    chrome_options = Options()
    chrome_options.add_experimental_option(
        "debuggerAddress", 
        "127.0.0.1:9222"  # Port của remote debugging
    )
    driver = webdriver.Chrome(options=chrome_options)
    return driver


def init_driver_full_options():
    """Cách 5: Khởi tạo với đầy đủ options"""
    chrome_options = Options()
    
    # Tắt thông báo
    chrome_options.add_argument('--disable-notifications')
    
    # Tắt popup "Chrome is being controlled"
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # Giả lập user agent
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
    
    # Tắt GPU (tránh lỗi một số máy)
    chrome_options.add_argument('--disable-gpu')
    
    # Maximize window
    chrome_options.add_argument('--start-maximized')
    
    # Chặn hình ảnh để load nhanh hơn (optional)
    # prefs = {"profile.managed_default_content_settings.images": 2}
    # chrome_options.add_experimental_option("prefs", prefs)
    
    driver = webdriver.Chrome(options=chrome_options)
    return driver


# ============================================================================
# 2. TÌM ELEMENTS (LOCATORS)
# ============================================================================

def find_element_examples(driver):
    """Các cách tìm element chuẩn"""
    
    # ===== LOCATOR TYPES =====
    
    # 1. By ID (Nhanh nhất, ưu tiên số 1)
    element = driver.find_element(By.ID, "username")
    
    # 2. By NAME
    element = driver.find_element(By.NAME, "email")
    
    # 3. By CLASS_NAME (Chú ý: chỉ 1 class, không có space)
    element = driver.find_element(By.CLASS_NAME, "btn-primary")
    
    # 4. By CSS_SELECTOR (Nhanh, linh hoạt)
    element = driver.find_element(By.CSS_SELECTOR, "input[type='email']")
    element = driver.find_element(By.CSS_SELECTOR, ".btn.btn-primary")
    element = driver.find_element(By.CSS_SELECTOR, "#username")
    element = driver.find_element(By.CSS_SELECTOR, "div.container > input")
    
    # 5. By XPATH (Chậm nhất nhưng mạnh nhất)
    # XPath với text
    element = driver.find_element(By.XPATH, "//button[text()='Login']")
    element = driver.find_element(By.XPATH, "//button[contains(text(), 'Login')]")
    
    # XPath với attribute
    element = driver.find_element(By.XPATH, "//input[@placeholder='Email']")
    element = driver.find_element(By.XPATH, "//input[@type='email' and @name='username']")
    
    # XPath với index
    element = driver.find_element(By.XPATH, "(//button[@class='btn'])[1]")
    
    # XPath với parent/child
    element = driver.find_element(By.XPATH, "//div[@id='form']//input[@name='email']")
    element = driver.find_element(By.XPATH, "//input[@name='email']/parent::div")
    
    # 6. By LINK_TEXT (Chỉ dùng cho thẻ <a>)
    element = driver.find_element(By.LINK_TEXT, "Click here")
    
    # 7. By PARTIAL_LINK_TEXT
    element = driver.find_element(By.PARTIAL_LINK_TEXT, "Click")
    
    # 8. By TAG_NAME
    element = driver.find_element(By.TAG_NAME, "h1")


def find_multiple_elements(driver):
    """Tìm nhiều elements"""
    
    # find_elements trả về list (có thể rỗng)
    elements = driver.find_elements(By.CLASS_NAME, "item")
    
    print(f"Found {len(elements)} elements")
    
    # Lặp qua các elements
    for element in elements:
        print(element.text)
    
    # Kiểm tra element có tồn tại không
    if len(driver.find_elements(By.ID, "optional-button")) > 0:
        print("Element exists")
    else:
        print("Element does not exist")


# ============================================================================
# 3. WEBDRIVERWAIT - CHỜ ELEMENT (QUAN TRỌNG NHẤT!)
# ============================================================================

def wait_examples(driver):
    """Các cách chờ element chuẩn - LUÔN DÙNG CÁCH NÀY!"""
    
    # ===== EXPECTED CONDITIONS (EC) =====
    
    # 1. presence_of_element_located
    # Element có trong DOM (có thể invisible)
    element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "username"))
    )
    
    # 2. visibility_of_element_located
    # Element phải visible (display: block, opacity > 0, etc.)
    element = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, "username"))
    )
    
    # 3. element_to_be_clickable
    # Element phải clickable (visible + enabled)
    # ĐÂY LÀ CÁCH TỐT NHẤT TRƯỚC KHI CLICK!
    element = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "submit-button"))
    )
    element.click()
    
    # 4. presence_of_all_elements_located
    # Chờ nhiều elements
    elements = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CLASS_NAME, "item"))
    )
    
    # 5. text_to_be_present_in_element
    # Chờ text xuất hiện trong element
    WebDriverWait(driver, 10).until(
        EC.text_to_be_present_in_element(
            (By.ID, "status"), 
            "Success"
        )
    )
    
    # 6. element_to_be_selected
    # Chờ checkbox/radio được chọn
    WebDriverWait(driver, 10).until(
        EC.element_to_be_selected((By.ID, "terms-checkbox"))
    )
    
    # 7. alert_is_present
    # Chờ alert popup
    WebDriverWait(driver, 10).until(EC.alert_is_present())
    
    # 8. frame_to_be_available_and_switch_to_it
    # Chờ và chuyển sang iframe
    WebDriverWait(driver, 10).until(
        EC.frame_to_be_available_and_switch_to_it((By.ID, "iframe1"))
    )
    
    # 9. invisibility_of_element_located
    # Chờ element biến mất
    WebDriverWait(driver, 10).until(
        EC.invisibility_of_element_located((By.ID, "loading-spinner"))
    )


def wait_with_custom_condition(driver):
    """Tạo custom wait condition"""
    
    def element_has_class(locator, class_name):
        """Wait until element has specific class"""
        def check(driver):
            element = driver.find_element(*locator)
            return class_name in element.get_attribute("class")
        return check
    
    # Sử dụng
    WebDriverWait(driver, 10).until(
        element_has_class((By.ID, "button"), "active")
    )


def wait_best_practices(driver):
    """Best practices khi dùng wait"""
    
    # ❌ KHÔNG NÊN: Dùng time.sleep()
    # time.sleep(5)
    # element = driver.find_element(By.ID, "username")
    
    # ✅ NÊN: Dùng WebDriverWait
    element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "username"))
    )
    
    # ✅ NÊN: Kết hợp với try-except
    try:
        element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "submit"))
        )
        element.click()
    except TimeoutException:
        print("Element not found within 10 seconds")
    
    # ✅ NÊN: Tăng/giảm timeout tùy trường hợp
    # Timeout ngắn cho element nhanh
    WebDriverWait(driver, 3).until(
        EC.presence_of_element_located((By.ID, "fast-element"))
    )
    
    # Timeout dài cho element chậm (API call, loading, etc.)
    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.ID, "slow-element"))
    )


# ============================================================================
# 4. THAO TÁC VỚI ELEMENTS (INTERACTIONS)
# ============================================================================

def interaction_examples(driver):
    """Các thao tác cơ bản với elements"""
    
    # 1. Click
    element = driver.find_element(By.ID, "button")
    element.click()
    
    # 2. Send keys (nhập text)
    input_field = driver.find_element(By.ID, "username")
    input_field.send_keys("myusername")
    
    # 3. Clear text
    input_field.clear()
    
    # 4. Submit form
    form = driver.find_element(By.ID, "login-form")
    form.submit()
    
    # 5. Get text
    text = element.text
    print(f"Element text: {text}")
    
    # 6. Get attribute
    href = element.get_attribute("href")
    class_name = element.get_attribute("class")
    data_id = element.get_attribute("data-id")
    
    # 7. Check if element is displayed
    if element.is_displayed():
        print("Element is visible")
    
    # 8. Check if element is enabled
    if element.is_enabled():
        print("Element is enabled")
    
    # 9. Check if element is selected (checkbox/radio)
    if element.is_selected():
        print("Element is selected")


def advanced_interactions(driver):
    """Thao tác nâng cao"""
    
    # 1. ActionChains - Click phức tạp
    element = driver.find_element(By.ID, "button")
    actions = ActionChains(driver)
    actions.move_to_element(element).click().perform()
    
    # 2. Double click
    actions = ActionChains(driver)
    actions.double_click(element).perform()
    
    # 3. Right click (context menu)
    actions = ActionChains(driver)
    actions.context_click(element).perform()
    
    # 4. Hover (di chuột vào)
    actions = ActionChains(driver)
    actions.move_to_element(element).perform()
    
    # 5. Drag and drop
    source = driver.find_element(By.ID, "draggable")
    target = driver.find_element(By.ID, "droppable")
    actions = ActionChains(driver)
    actions.drag_and_drop(source, target).perform()
    
    # 6. Send keys đặc biệt
    element = driver.find_element(By.ID, "search")
    element.send_keys("Python")
    element.send_keys(Keys.RETURN)  # Enter
    element.send_keys(Keys.TAB)     # Tab
    element.send_keys(Keys.ESCAPE)  # Esc
    element.send_keys(Keys.CONTROL, "a")  # Ctrl+A
    
    # 7. Execute JavaScript
    driver.execute_script("arguments[0].click();", element)
    driver.execute_script("arguments[0].scrollIntoView(true);", element)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    
    # 8. Highlight element (debug)
    driver.execute_script(
        "arguments[0].style.border='3px solid red'", 
        element
    )


def handle_special_cases(driver):
    """Xử lý các trường hợp đặc biệt"""
    
    # 1. Element bị che bởi element khác (ElementClickInterceptedException)
    try:
        element = driver.find_element(By.ID, "button")
        element.click()
    except ElementClickInterceptedException:
        # Dùng JavaScript click
        driver.execute_script("arguments[0].click();", element)
    
    # 2. Element bị stale (StaleElementReferenceException)
    try:
        element = driver.find_element(By.ID, "dynamic-element")
        # Page refresh hoặc element thay đổi
        driver.refresh()
        element.click()  # Sẽ bị lỗi stale
    except StaleElementReferenceException:
        # Tìm lại element
        element = driver.find_element(By.ID, "dynamic-element")
        element.click()
    
    # 3. Scroll đến element
    element = driver.find_element(By.ID, "bottom-button")
    driver.execute_script("arguments[0].scrollIntoView(true);", element)
    time.sleep(0.5)  # Chờ animation scroll
    element.click()
    
    # 4. Wait for element to be stable (không còn di chuyển)
    element = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "animated-button"))
    )
    time.sleep(0.3)  # Đợi animation xong
    element.click()


# ============================================================================
# 5. XỬ LÝ LỖI (ERROR HANDLING)
# ============================================================================

def error_handling_template(driver):
    """Template xử lý lỗi chuẩn"""
    
    try:
        # Main logic
        element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "button"))
        )
        element.click()
        print("[OK] Action successful")
        
    except TimeoutException:
        print("[ERROR] Element not found within timeout")
        # Xử lý khi không tìm thấy element
        
    except NoSuchElementException:
        print("[ERROR] Element does not exist")
        # Xử lý khi element không tồn tại
        
    except ElementClickInterceptedException:
        print("[ERROR] Element is covered by another element")
        # Thử click bằng JavaScript
        driver.execute_script("arguments[0].click();", element)
        
    except StaleElementReferenceException:
        print("[ERROR] Element is stale, retrying...")
        # Tìm lại element
        element = driver.find_element(By.ID, "button")
        element.click()
        
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        # Screenshot để debug
        screenshot_path = f"error_{int(time.time())}.png"
        driver.save_screenshot(screenshot_path)
        print(f"[*] Screenshot saved: {screenshot_path}")
        raise


def retry_mechanism(driver, max_retries=3):
    """Cơ chế retry khi gặp lỗi"""
    
    for attempt in range(max_retries):
        try:
            element = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, "button"))
            )
            element.click()
            print(f"[OK] Success on attempt {attempt + 1}")
            return True
            
        except Exception as e:
            print(f"[!] Attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                print(f"[*] Retrying in 2 seconds...")
                time.sleep(2)
            else:
                print(f"[ERROR] All {max_retries} attempts failed")
                return False


# ============================================================================
# 6. STRATEGIES - THỬ NHIỀU CÁCH TÌM ELEMENT
# ============================================================================

def find_element_multiple_strategies(driver, timeout=10):
    """
    Thử nhiều cách tìm element - nếu cách này không được thì thử cách khác
    ĐÂY LÀ PATTERN RẤT QUAN TRỌNG!
    """
    
    locators = [
        (By.ID, "search-box"),
        (By.NAME, "search"),
        (By.CSS_SELECTOR, "input[placeholder='Search']"),
        (By.XPATH, "//input[@placeholder='Search']"),
        (By.XPATH, "//input[@aria-label='Search']"),
        (By.XPATH, "//input[@data-testid='search-input']"),
    ]
    
    for locator_type, locator_value in locators:
        try:
            element = WebDriverWait(driver, timeout).until(
                EC.element_to_be_clickable((locator_type, locator_value))
            )
            print(f"[OK] Found element using: {locator_value}")
            return element
            
        except TimeoutException:
            print(f"[!] Not found using: {locator_value}")
            continue
    
    # Nếu tất cả đều fail
    raise Exception("Could not find element with any strategy")


# ============================================================================
# 7. NAVIGATION
# ============================================================================

def navigation_examples(driver):
    """Điều hướng trang"""
    
    # 1. Mở URL
    driver.get("https://www.example.com")
    
    # 2. Back
    driver.back()
    
    # 3. Forward
    driver.forward()
    
    # 4. Refresh
    driver.refresh()
    
    # 5. Get current URL
    current_url = driver.current_url
    print(f"Current URL: {current_url}")
    
    # 6. Get page title
    title = driver.title
    print(f"Page title: {title}")
    
    # 7. Get page source
    source = driver.page_source


# ============================================================================
# 8. WINDOWS & TABS
# ============================================================================

def handle_windows_tabs(driver):
    """Xử lý nhiều windows/tabs"""
    
    # 1. Mở tab mới
    driver.execute_script("window.open('');")
    
    # 2. Lấy tất cả window handles
    windows = driver.window_handles
    print(f"Number of windows: {len(windows)}")
    
    # 3. Chuyển sang tab mới
    driver.switch_to.window(windows[1])
    
    # 4. Chuyển về tab đầu
    driver.switch_to.window(windows[0])
    
    # 5. Đóng tab hiện tại
    driver.close()
    
    # 6. Chuyển sang tab cuối cùng
    driver.switch_to.window(driver.window_handles[-1])


# ============================================================================
# 9. IFRAMES
# ============================================================================

def handle_iframes(driver):
    """Xử lý iframes"""
    
    # 1. Switch vào iframe bằng ID
    driver.switch_to.frame("iframe-id")
    
    # 2. Switch vào iframe bằng name
    driver.switch_to.frame("iframe-name")
    
    # 3. Switch vào iframe bằng index
    driver.switch_to.frame(0)
    
    # 4. Switch vào iframe bằng WebElement
    iframe = driver.find_element(By.TAG_NAME, "iframe")
    driver.switch_to.frame(iframe)
    
    # 5. Switch về main content
    driver.switch_to.default_content()
    
    # 6. Switch về parent frame
    driver.switch_to.parent_frame()


# ============================================================================
# 10. ALERTS & POPUPS
# ============================================================================

def handle_alerts(driver):
    """Xử lý alerts và popups"""
    
    # 1. Chờ alert xuất hiện
    WebDriverWait(driver, 10).until(EC.alert_is_present())
    
    # 2. Switch sang alert
    alert = driver.switch_to.alert
    
    # 3. Get alert text
    alert_text = alert.text
    print(f"Alert text: {alert_text}")
    
    # 4. Accept alert (click OK)
    alert.accept()
    
    # 5. Dismiss alert (click Cancel)
    alert.dismiss()
    
    # 6. Nhập text vào prompt
    alert.send_keys("My text")
    alert.accept()


# ============================================================================
# 11. COOKIES & STORAGE
# ============================================================================

def handle_cookies(driver):
    """Xử lý cookies"""
    
    # 1. Get all cookies
    cookies = driver.get_cookies()
    print(f"All cookies: {cookies}")
    
    # 2. Get specific cookie
    cookie = driver.get_cookie("session_id")
    print(f"Session cookie: {cookie}")
    
    # 3. Add cookie
    driver.add_cookie({
        "name": "test_cookie",
        "value": "test_value"
    })
    
    # 4. Delete specific cookie
    driver.delete_cookie("test_cookie")
    
    # 5. Delete all cookies
    driver.delete_all_cookies()


def handle_local_storage(driver):
    """Xử lý localStorage"""
    
    # 1. Set item
    driver.execute_script("window.localStorage.setItem('key', 'value');")
    
    # 2. Get item
    value = driver.execute_script("return window.localStorage.getItem('key');")
    print(f"Value: {value}")
    
    # 3. Remove item
    driver.execute_script("window.localStorage.removeItem('key');")
    
    # 4. Clear all
    driver.execute_script("window.localStorage.clear();")


# ============================================================================
# 12. SCREENSHOTS & DEBUGGING
# ============================================================================

def debugging_tools(driver):
    """Tools để debug"""
    
    # 1. Screenshot toàn trang
    driver.save_screenshot("screenshot.png")
    
    # 2. Screenshot element
    element = driver.find_element(By.ID, "element")
    element.screenshot("element.png")
    
    # 3. Get page source
    html = driver.page_source
    with open("page_source.html", "w", encoding="utf-8") as f:
        f.write(html)
    
    # 4. Highlight element (thêm border đỏ)
    element = driver.find_element(By.ID, "element")
    driver.execute_script(
        "arguments[0].style.border='3px solid red'", 
        element
    )
    
    # 5. Print element info
    print(f"Tag: {element.tag_name}")
    print(f"Text: {element.text}")
    print(f"Location: {element.location}")
    print(f"Size: {element.size}")
    print(f"Attributes: {element.get_attribute('outerHTML')}")


# ============================================================================
# 13. COMPLETE FUNCTION TEMPLATE
# ============================================================================

def complete_action_template(driver, action_name, locator_strategies):
    """
    TEMPLATE HOÀN CHỈNH cho một action bất kỳ
    Copy template này cho mọi thao tác!
    
    Args:
        driver: WebDriver instance
        action_name: Tên hành động (để log)
        locator_strategies: List of tuples (By.TYPE, "locator_value")
    """
    print("\n" + "="*60)
    print(f"[*] Starting: {action_name}")
    print("="*60)
    
    element = None
    
    try:
        # Step 1: Tìm element với nhiều strategies
        print(f"\n[1/3] Looking for element...")
        
        for idx, (locator_type, locator_value) in enumerate(locator_strategies, 1):
            try:
                element = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((locator_type, locator_value))
                )
                print(f"[OK] Found using strategy #{idx}: {locator_value}")
                break
            except TimeoutException:
                print(f"[!] Strategy #{idx} failed: {locator_value}")
                continue
        
        if not element:
            raise Exception("Could not find element with any strategy")
        
        # Step 2: Highlight element (optional - for debugging)
        print(f"\n[2/3] Highlighting element...")
        driver.execute_script(
            "arguments[0].style.border='3px solid green'", 
            element
        )
        time.sleep(0.3)
        
        # Step 3: Perform action
        print(f"\n[3/3] Performing action...")
        
        # Scroll vào view nếu cần
        driver.execute_script(
            "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", 
            element
        )
        time.sleep(0.3)
        
        # Thực hiện action (tùy chỉnh theo nhu cầu)
        element.click()
        # hoặc: element.send_keys("text")
        # hoặc: custom action
        
        print(f"[OK] Action performed successfully")
        
        # Step 4: Verify result (optional)
        time.sleep(1)
        
        print("\n" + "="*60)
        print(f"[SUCCESS] {action_name} completed!")
        print("="*60)
        
        return True
        
    except TimeoutException:
        print(f"\n[ERROR] Timeout - Could not find element")
        driver.save_screenshot(f"error_timeout_{int(time.time())}.png")
        return False
        
    except ElementClickInterceptedException:
        print(f"\n[ERROR] Element is covered, trying JavaScript click...")
        try:
            driver.execute_script("arguments[0].click();", element)
            print(f"[OK] JavaScript click successful")
            return True
        except Exception as e:
            print(f"[ERROR] JavaScript click also failed: {e}")
            return False
        
    except StaleElementReferenceException:
        print(f"\n[ERROR] Element is stale, retrying...")
        # Có thể retry 1 lần nữa
        return False
        
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        
        # Screenshot để debug
        try:
            screenshot_path = f"error_{action_name}_{int(time.time())}.png"
            driver.save_screenshot(screenshot_path)
            print(f"[*] Screenshot saved: {screenshot_path}")
        except:
            pass
        
        return False


# ============================================================================
# 14. REAL EXAMPLE - TWITTER SEARCH
# ============================================================================

def example_twitter_search(driver):
    """
    Ví dụ thực tế: Tìm kiếm trên Twitter
    Áp dụng tất cả best practices
    """
    
    # Định nghĩa các cách tìm search box
    search_locators = [
        (By.XPATH, "//input[@placeholder='Tìm kiếm']"),
        (By.XPATH, "//input[@aria-label='Search query']"),
        (By.XPATH, "//input[@data-testid='SearchBox_Search_Input']"),
        (By.CSS_SELECTOR, "input[placeholder='Tìm kiếm']"),
        (By.CSS_SELECTOR, "input[aria-label='Search query']"),
    ]
    
    # Sử dụng template
    success = complete_action_template(
        driver=driver,
        action_name="Twitter Search",
        locator_strategies=search_locators
    )
    
    if success:
        # Nhập text tìm kiếm
        try:
            search_box = driver.switch_to.active_element
            search_box.send_keys("Python Programming")
            search_box.send_keys(Keys.RETURN)
            print("[OK] Search submitted")
            
            # Đợi kết quả
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//article[@data-testid='tweet']")
                )
            )
            print("[OK] Search results loaded")
            
        except Exception as e:
            print(f"[ERROR] Could not complete search: {e}")


# ============================================================================
# 15. MAIN FUNCTION STRUCTURE
# ============================================================================

def main_automation_structure():
    """
    Cấu trúc chuẩn cho một automation script hoàn chỉnh
    """
    driver = None
    
    try:
        # 1. Initialize
        print("[*] Initializing driver...")
        driver = init_driver_full_options()
        print("[OK] Driver initialized")
        
        # 2. Navigate
        print("\n[*] Navigating to website...")
        driver.get("https://example.com")
        print("[OK] Navigation complete")
        
        # 3. Wait for page load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        # 4. Perform actions
        print("\n[*] Performing actions...")
        
        # Action 1
        # complete_action_template(...)
        
        # Action 2
        # complete_action_template(...)
        
        # Action 3
        # complete_action_template(...)
        
        print("\n[SUCCESS] All actions completed!")
        
    except Exception as e:
        print(f"\n[ERROR] Script failed: {e}")
        
        # Screenshot
        if driver:
            try:
                driver.save_screenshot(f"error_main_{int(time.time())}.png")
            except:
                pass
        
        raise
    
    finally:
        # 5. Cleanup
        if driver:
            print("\n[*] Closing driver...")
            driver.quit()
            print("[OK] Driver closed")


# ============================================================================
# 16. QUICK REFERENCE - CHEAT SHEET
# ============================================================================

"""
===============================================================================
                        SELENIUM QUICK REFERENCE
===============================================================================

1. KHỞI TẠO:
   driver = webdriver.Chrome(options=chrome_options)

2. TÌM ELEMENT (ƯU TIÊN):
   ✅ ID:          driver.find_element(By.ID, "id")
   ✅ CSS:         driver.find_element(By.CSS_SELECTOR, ".class")
   ⚠️  XPath:      driver.find_element(By.XPATH, "//div[@id='id']")

3. WAIT (LUÔN DÙNG!):
   element = WebDriverWait(driver, 10).until(
       EC.element_to_be_clickable((By.ID, "id"))
   )

4. THAO TÁC:
   element.click()
   element.send_keys("text")
   element.clear()
   text = element.text
   attr = element.get_attribute("href")

5. NAVIGATION:
   driver.get("url")
   driver.back()
   driver.forward()
   driver.refresh()

6. WINDOWS:
   driver.switch_to.window(driver.window_handles[1])
   driver.close()

7. IFRAME:
   driver.switch_to.frame("iframe-id")
   driver.switch_to.default_content()

8. ALERT:
   alert = driver.switch_to.alert
   alert.accept()

9. JAVASCRIPT:
   driver.execute_script("arguments[0].click();", element)

10. ERROR HANDLING:
    try:
        element = WebDriverWait(driver, 10).until(...)
        element.click()
    except TimeoutException:
        print("Timeout")
    except Exception as e:
        print(f"Error: {e}")
        driver.save_screenshot("error.png")

===============================================================================
                            GOLDEN RULES
===============================================================================

✅ LUÔN dùng WebDriverWait thay vì time.sleep()
✅ LUÔN dùng try-except
✅ LUÔN chờ element_to_be_clickable trước khi click
✅ LUÔN có nhiều locator strategies backup
✅ LUÔN log từng bước
✅ LUÔN chụp screenshot khi lỗi
✅ LUÔN cleanup (driver.quit())

❌ KHÔNG dùng time.sleep() cho wait logic
❌ KHÔNG quên xử lý lỗi
❌ KHÔNG hard-code timeout (tùy tình huống)
❌ KHÔNG quên switch về default_content sau iframe
❌ KHÔNG find_element mà không check exists trước

===============================================================================
"""


if __name__ == "__main__":
    print(__doc__)
    print("\n" + "="*60)
    print("This is a REFERENCE guide - not meant to be executed")
    print("Copy the patterns you need into your project")
    print("="*60)

