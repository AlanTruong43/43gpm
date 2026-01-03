# -*- coding: utf-8 -*-
"""
Twitter Automation Project
Automation cho các tác vụ trên Twitter/X
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
    Main function to run Twitter automation
    
    Args:
        profile_data: Dict containing:
            - profile_id: Profile ID
            - profile_name: Profile name
            - remote_debugging_address: e.g., "127.0.0.1:53378"
            - browser_location: Path to browser executable
            - driver_path: Path to ChromeDriver
    """
    print(f">>> [TWITTER] Connecting to browser at: {profile_data['remote_debugging_address']}...")
    
    driver = None
    
    try:
        # Connect to the already opened browser profile
        chrome_options = Options()
        chrome_options.add_experimental_option(
            "debuggerAddress", 
            profile_data['remote_debugging_address']
        )
        
        print(f">>> [TWITTER] Initializing WebDriver (Connecting to browser)...")
        try:
            from selenium.webdriver.chrome.service import Service
            
            # Using specific driver_path from GPM if available
            driver_path = profile_data.get('driver_path')
            if driver_path:
                print(f">>> [TWITTER] Using specific driver: {driver_path}")
                service = Service(executable_path=driver_path)
                driver = webdriver.Chrome(service=service, options=chrome_options)
            else:
                print(">>> [TWITTER] Using default system driver")
                driver = webdriver.Chrome(options=chrome_options)
                
        except Exception as chrome_err:
            print(f">>> [ERROR] Selenium could not connect to browser: {chrome_err}")
            print(">>> [TIP] Có thể driver_path không đúng hoặc trình duyệt chưa hỗ trợ Remote Debugging.")
            return
            
        print(f">>> [TWITTER] WebDriver initialized successfully!")
        
        # Step 0: Ensure we are using the correct window/tab
        print(f">>> [TWITTER] Scanning for a valid browser tab...")
        all_handles = driver.window_handles
        target_handle = None
        
        for handle in all_handles:
            driver.switch_to.window(handle)
            current_url = driver.current_url
            print(f">>> [TWITTER] Window {handle[:8]}: {current_url}")
            
            # Skip extension background pages and other internal chrome pages
            if not current_url.startswith("chrome-extension://") and not current_url.startswith("chrome://"):
                target_handle = handle
                break
        
        if not target_handle:
            print(">>> [TWITTER] No active web tab found. Creating a new one...")
            driver.execute_script("window.open('about:blank', '_blank');")
            driver.switch_to.window(driver.window_handles[-1])
        else:
            print(f">>> [TWITTER] Selected valid tab: {driver.current_url}")
        
        # Step 1: Navigate to Twitter home
        target_url = "https://x.com/home"
        print(f">>> [TWITTER] Navigating to {target_url}...")
        driver.get(target_url)
        time.sleep(2) # Wait for page start
        print(f">>> [TWITTER] Navigation complete! New URL: {driver.current_url}")
        
        # VISUAL FEEDBACK: Scroll down then up
        print(">>> [TWITTER] Performing visual feedback (Scrolling)...")
        driver.execute_script("window.scrollTo(0, 500);")
        time.sleep(1)
        driver.execute_script("window.scrollTo(0, 0);")
        
        # Step 2: Check login status
        print(">>> [TWITTER] Checking for login button (timeout 10s)...")
        try:
            # Wait for the login button
            login_button = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[text()="Đăng nhập vào X"]'))
            )
            print(">>> [TWITTER] RESULT: Not logged in. Highlighting button.")
            driver.execute_script("arguments[0].style.border='5px solid red'; arguments[0].style.backgroundColor='yellow';", login_button)
            
        except TimeoutException:
            print("[OK] ALREADY LOGGED IN")
            # Draw a visual box to confirm connection
            confirm_js = """
            var div = document.createElement('div');
            div.style.position = 'fixed';
            div.style.top = '10px';
            div.style.right = '10px';
            div.style.padding = '10px';
            div.style.background = 'green';
            div.style.color = 'white';
            div.style.zIndex = '9999';
            div.style.fontSize = '20px';
            div.innerHTML = 'BOT CONNECTED SUCCESSFULLY';
            document.body.appendChild(div);
            setTimeout(function() { div.remove(); }, 5000);
            """
            driver.execute_script(confirm_js)
            
            try:
                driver.find_element(By.XPATH, "//a[@aria-label='Post']")
                print("[OK] Timeline loaded")
            except:
                pass
        
    except Exception as e:
        print(f"[ERROR] Twitter Automation: {e}")
        raise
    finally:
        print("[INFO] Tasks finished. Browser left open.")


# Example usage if run directly
if __name__ == "__main__":
    # This is just for testing
    # In production, this will be called by the dashboard
    test_profile_data = {
        "profile_id": "test_id",
        "profile_name": "Test Profile",
        "remote_debugging_address": "127.0.0.1:53378",
        "browser_location": "",
        "driver_path": ""
    }
    
    print("This is a test run. Use the dashboard to run this project properly.")
    # run(test_profile_data)

