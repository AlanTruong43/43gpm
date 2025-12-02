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
    print("=" * 60)
    print(f"[*] Starting Twitter Automation")
    print(f"[*] Profile: {profile_data['profile_name']}")
    print(f"[*] Debug Address: {profile_data['remote_debugging_address']}")
    print("=" * 60)
    
    driver = None
    
    try:
        # Connect to the already opened browser profile
        print("\n[1/3] Connecting to browser...")
        chrome_options = Options()
        chrome_options.add_experimental_option(
            "debuggerAddress", 
            profile_data['remote_debugging_address']
        )
        
        # Initialize driver
        driver = webdriver.Chrome(options=chrome_options)
        print("[OK] Connected to browser successfully!")
        
        # Step 1: Navigate to Twitter home
        print("\n[2/3] Navigating to Twitter...")
        driver.get("https://x.com/home")
        print("[OK] Navigated to https://x.com/home")
        
        # Step 2: Wait for login button or check if already logged in
        print("\n[3/3] Checking login status...")
        
        try:
            # Wait for the login button with text "Đăng nhập vào X"
            login_button = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[text()="Đăng nhập vào X"]'))
            )
            
            print("[!] NOT LOGGED IN - Login button found!")
            print("[*] Found login button element")
            print("\n[INFO] Next steps:")
            print("   1. Click the login button")
            print("   2. Enter credentials")
            print("   3. Handle verification if needed")
            
            # Highlight the login button
            driver.execute_script("arguments[0].style.border='3px solid red'", login_button)
            print("\n[*] Login button has been highlighted in red")
            
        except TimeoutException:
            print("[OK] ALREADY LOGGED IN - No login button found!")
            print("[OK] Account is authenticated and ready to use")
            
            # Check for timeline or other logged-in elements
            try:
                # Try to find the compose tweet button
                compose_button = driver.find_element(By.XPATH, "//a[@aria-label='Post']")
                print("[OK] Found 'Post' button - User is on the timeline")
            except NoSuchElementException:
                print("[!] Logged in but timeline not fully loaded")
        
        print("\n" + "=" * 60)
        print("[OK] Automation Step Completed Successfully!")
        print("[*] Browser will remain open for next actions")
        print("=" * 60)
        
        # Keep browser open for manual inspection or next steps
        time.sleep(2)
        
    except Exception as e:
        print("\n" + "=" * 60)
        print(f"[ERROR] Error during automation: {e}")
        print("=" * 60)
        
        # Take screenshot for debugging
        if driver:
            try:
                screenshot_path = f"error_screenshot_{int(time.time())}.png"
                driver.save_screenshot(screenshot_path)
                print(f"[*] Screenshot saved: {screenshot_path}")
            except:
                pass
        
        raise
    
    finally:
        # DON'T close the driver - let the dashboard handle it
        # driver.quit()
        print("\n[INFO] Browser remains open. Close from dashboard when done.\n")


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

