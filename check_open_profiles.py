# -*- coding: utf-8 -*-
"""
Check Open Profiles Tool
Quick tool to check which profiles are currently open in 43GPM
"""
import encoding_fix
from api_client import GPMClient
import time


def check_open_profiles():
    """Check and display currently open profiles"""
    client = GPMClient()
    
    print("=" * 60)
    print("CHECKING OPEN PROFILES")
    print("=" * 60)
    
    # Get all profiles
    profiles_data = client.get_profiles(page=1, per_page=200)
    profiles = profiles_data.get("data", [])
    
    print(f"\nTotal profiles: {len(profiles)}")
    print("\nChecking which profiles are open...\n")
    
    open_count = 0
    
    for profile in profiles:
        profile_id = profile.get("id")
        profile_name = profile.get("name")
        
        # Try to open (if already open, will get error)
        result = client.start_profile(profile_id)
        
        if result.get("success"):
            # Was closed, now opened - close it immediately
            print(f"[CLOSED] {profile_name}")
            client.close_profile(profile_id)
            time.sleep(0.5)
        else:
            # Already open or error
            error_msg = result.get("message", "")
            if "running" in error_msg.lower() or "đang chạy" in error_msg.lower():
                print(f"[OPEN]   {profile_name} (ID: {profile_id[:12]}...)")
                open_count += 1
            else:
                print(f"[ERROR]  {profile_name}: {error_msg}")
    
    print("\n" + "=" * 60)
    print(f"Summary: {open_count} profile(s) currently OPEN")
    print("=" * 60)


def close_all_profiles():
    """Force close all profiles"""
    client = GPMClient()
    
    print("=" * 60)
    print("FORCE CLOSING ALL PROFILES")
    print("=" * 60)
    
    profiles_data = client.get_profiles(page=1, per_page=200)
    profiles = profiles_data.get("data", [])
    
    closed_count = 0
    
    for profile in profiles:
        profile_id = profile.get("id")
        profile_name = profile.get("name")
        
        print(f"Closing: {profile_name}...", end=" ")
        result = client.close_profile(profile_id)
        
        if result.get("success"):
            print("[OK]")
            closed_count += 1
        else:
            print(f"[SKIP] {result.get('message', '')}")
        
        time.sleep(0.3)
    
    print("\n" + "=" * 60)
    print(f"Closed {closed_count} profile(s)")
    print("=" * 60)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--close-all":
        close_all_profiles()
    else:
        check_open_profiles()
        
        print("\nOptions:")
        print("  python check_open_profiles.py           - Check open profiles")
        print("  python check_open_profiles.py --close-all  - Close all profiles")

