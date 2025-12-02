"""
43GPM Profile Dashboard
Dashboard for managing antidetect browser profiles and running automation projects
"""
import streamlit as st
import pandas as pd
from api_client import GPMClient
from automation_runner import ProfileAutomationRunner
import time
from datetime import datetime
import os
import importlib.util
from pathlib import Path


# Page config
st.set_page_config(
    page_title="43GPM Profile Dashboard",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .profile-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .status-running {
        color: #28a745;
        font-weight: bold;
    }
    .status-stopped {
        color: #dc3545;
        font-weight: bold;
    }
    .stButton>button {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'gpm_client' not in st.session_state:
    st.session_state.gpm_client = GPMClient()

if 'running_profiles' not in st.session_state:
    st.session_state.running_profiles = {}

if 'selected_profile' not in st.session_state:
    st.session_state.selected_profile = None

if 'project_running' not in st.session_state:
    st.session_state.project_running = False

if 'automation_runner' not in st.session_state:
    st.session_state.automation_runner = None

if 'runner_active' not in st.session_state:
    st.session_state.runner_active = False

# Cleanup function
def cleanup_on_close():
    """Cleanup all temporary data"""
    if st.session_state.automation_runner:
        st.session_state.automation_runner.clear()
        st.session_state.automation_runner = None
    st.session_state.runner_active = False
    st.session_state.running_profiles = {}

# Register cleanup on session end
import atexit
atexit.register(cleanup_on_close)


def load_available_projects():
    """Load all available Python projects from the project folder"""
    project_folder = Path("project")
    if not project_folder.exists():
        return []
    
    projects = []
    for file in project_folder.glob("*.py"):
        if file.name != "__init__.py":
            projects.append(file.stem)
    return projects


def run_project_with_profile(project_name: str, profile_data: dict):
    """
    Run a project with the selected profile
    
    Args:
        project_name: Name of the project file (without .py)
        profile_data: Profile data including remote_debugging_address
    """
    try:
        # Import the project module
        project_path = Path(f"project/{project_name}.py")
        
        if not project_path.exists():
            st.error(f"Project file not found: {project_path}")
            return
        
        spec = importlib.util.spec_from_file_location(project_name, project_path)
        project_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(project_module)
        
        # Check if module has a 'run' function
        if hasattr(project_module, 'run'):
            st.info(f"Starting project: {project_name}")
            project_module.run(profile_data)
            st.success(f"Project {project_name} completed!")
        else:
            st.warning(f"Project {project_name} doesn't have a 'run' function. Please add one.")
            st.code(f"""
# Add this to your {project_name}.py file:

def run(profile_data):
    '''
    Main function to run the automation
    
    Args:
        profile_data: Dict with keys:
            - remote_debugging_address: e.g., "127.0.0.1:53378"
            - browser_location: Path to browser
            - driver_path: Path to driver
            - profile_id: Profile ID
    '''
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    
    # Connect to the opened profile
    chrome_options = Options()
    chrome_options.add_experimental_option(
        "debuggerAddress", 
        profile_data['remote_debugging_address']
    )
    
    driver = webdriver.Chrome(options=chrome_options)
    
    # Your automation code here
    # driver.get("https://twitter.com")
    # ...
    
    # Don't close the driver - let dashboard handle it
    # driver.quit()
            """, language="python")
            
    except Exception as e:
        st.error(f"Error running project: {e}")


# Main App
def main():
    # Header
    st.markdown('<h1 class="main-header">🚀 43GPM Profile Dashboard</h1>', unsafe_allow_html=True)
    
    client = st.session_state.gpm_client
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Settings")
        
        # API Status Check
        st.subheader("API Status")
        try:
            groups = client.get_groups()
            if groups:
                st.success("✅ Connected to 43GPM")
            else:
                st.warning("⚠️ No groups found")
        except:
            st.error("❌ Cannot connect to 43GPM API")
            st.info("Make sure 43GPM is running on port 19995")
        
        st.divider()
        
        # Filters
        st.subheader("🔍 Filters")
        
        # Group filter
        groups = client.get_groups()
        group_options = {"All": None}
        if groups:
            for group in groups:
                group_options[group.get("name", "Unknown")] = group.get("id")
        
        selected_group_name = st.selectbox(
            "Select Group",
            options=list(group_options.keys())
        )
        selected_group_id = group_options[selected_group_name]
        
        # Search
        search_term = st.text_input("🔎 Search Profile Name", "")
        
        # Sort
        sort_options = {
            "Newest First": 0,
            "Oldest First": 1,
            "Name A-Z": 2,
            "Name Z-A": 3
        }
        sort_name = st.selectbox("Sort By", options=list(sort_options.keys()))
        sort_value = sort_options[sort_name]
        
        # Per page
        per_page = st.slider("Profiles Per Page", 10, 200, 50, 10)
        
        # Refresh button
        if st.button("🔄 Refresh Data"):
            st.rerun()
        
        st.divider()
        
        # Cleanup section
        st.subheader("🗑️ Data Management")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🗑️ Clear All", width='stretch', help="Clear all automation data and running profiles"):
                cleanup_on_close()
                st.success("✅ Cleared")
                time.sleep(0.5)
                st.rerun()
        
        with col2:
            running_count = len(st.session_state.running_profiles)
            if st.button(f"⏹️ Stop All ({running_count})", width='stretch', disabled=running_count == 0):
                # Close all running profiles
                for profile_id in list(st.session_state.running_profiles.keys()):
                    try:
                        client.close_profile(profile_id)
                    except:
                        pass
                st.session_state.running_profiles = {}
                st.success("✅ All profiles stopped")
                time.sleep(0.5)
                st.rerun()
    
    # Main content area
    tab1, tab2, tab3 = st.tabs(["📋 Profiles", "🚀 Batch Automation", "📊 Status"])
    
    with tab1:
        st.header("Profile List")
        
        # Get profiles
        profiles_data = client.get_profiles(
            group_id=selected_group_id,
            page=1,
            per_page=per_page,
            sort=sort_value,
            search=search_term if search_term else None
        )
        
        profiles = profiles_data.get("data", [])
        pagination = profiles_data.get("pagination", {})
        
        # Display pagination info
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Profiles", pagination.get("total", 0))
        with col2:
            st.metric("Current Page", pagination.get("page", 0))
        with col3:
            st.metric("Total Pages", pagination.get("total_page", 0))
        
        st.divider()
        
        # Display profiles
        if not profiles:
            st.warning("No profiles found. Check your filters or add profiles in 43GPM.")
        else:
            # Create DataFrame for better display
            df_data = []
            for profile in profiles:
                status = "🟢 Running" if profile.get("id") in st.session_state.running_profiles else "⚫ Stopped"
                df_data.append({
                    "Status": status,
                    "Name": profile.get("name", "Unknown"),
                    "ID": profile.get("id", ""),
                    "Browser": f"{profile.get('browser_type', '')} {profile.get('browser_version', '')}",
                    "Proxy": profile.get("raw_proxy", "No proxy"),
                    "Created": profile.get("created_at", "")[:10] if profile.get("created_at") else ""
                })
            
            df = pd.DataFrame(df_data)
            
            # Display as interactive table
            st.dataframe(
                df,
                width='stretch',
                hide_index=True,
                column_config={
                    "Status": st.column_config.TextColumn("Status", width="small"),
                    "Name": st.column_config.TextColumn("Name", width="medium"),
                    "ID": st.column_config.TextColumn("ID", width="medium"),
                    "Browser": st.column_config.TextColumn("Browser", width="medium"),
                    "Proxy": st.column_config.TextColumn("Proxy", width="medium"),
                    "Created": st.column_config.TextColumn("Created", width="small"),
                }
            )
            
            st.divider()
            
            # Quick actions
            st.subheader("Quick Actions")
            
            # Select profile dropdown
            profile_names = {f"{p.get('name')} ({p.get('id')[:8]}...)": p for p in profiles}
            selected_profile_name = st.selectbox(
                "Select Profile for Actions",
                options=list(profile_names.keys())
            )
            
            if selected_profile_name:
                selected_profile = profile_names[selected_profile_name]
                profile_id = selected_profile.get("id")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button("▶️ Open Profile", width='stretch'):
                        with st.spinner(f"Opening profile: {selected_profile.get('name')}..."):
                            result = client.start_profile(profile_id)
                            
                            if result.get("success"):
                                profile_data = result.get("data")
                                st.session_state.running_profiles[profile_id] = {
                                    "name": selected_profile.get("name"),
                                    "data": profile_data,
                                    "started_at": datetime.now()
                                }
                                st.success(f"✅ Profile opened successfully!")
                                st.info(f"Debug Address: {profile_data.get('remote_debugging_address')}")
                                time.sleep(1)
                                st.rerun()
                            else:
                                error_msg = result.get("message", "Unknown error")
                                st.error(f"❌ Failed to open profile")
                                
                                # Show detailed error message
                                with st.expander("🔍 Chi tiết lỗi", expanded=True):
                                    st.warning(f"**Lỗi:** {error_msg}")
                                    
                                    # Parse common errors and provide solutions
                                    if "Yêu cầu cập" in error_msg or "browser" in error_msg.lower():
                                        st.info("""
                                        **💡 Giải pháp:**
                                        1. Mở 43GPM
                                        2. Vào **Settings** → **Browser Core**
                                        3. Download browser version mà profile yêu cầu
                                        4. Đợi download xong và thử lại
                                        """)
                                    elif "running" in error_msg.lower():
                                        st.info("""
                                        **💡 Giải pháp:**
                                        - Profile đang được mở bởi process khác
                                        - Đóng profile trong 43GPM trước
                                        - Hoặc restart 43GPM
                                        """)
                                    else:
                                        st.info("""
                                        **💡 Các bước kiểm tra:**
                                        - Đảm bảo 43GPM đang chạy
                                        - Kiểm tra profile có tồn tại không
                                        - Restart 43GPM và thử lại
                                        """)
                
                with col2:
                    if st.button("⏹️ Close Profile", width='stretch'):
                        with st.spinner(f"Closing profile: {selected_profile.get('name')}..."):
                            result = client.close_profile(profile_id)
                            
                            if result.get("success"):
                                if profile_id in st.session_state.running_profiles:
                                    del st.session_state.running_profiles[profile_id]
                                st.success("✅ Profile closed successfully!")
                                time.sleep(1)
                                st.rerun()
                            else:
                                error_msg = result.get("message", "Unknown error")
                                st.error(f"❌ Failed to close profile: {error_msg}")
                
                with col3:
                    if st.button("ℹ️ View Details", width='stretch'):
                        profile_info = client.get_profile_info(profile_id)
                        if profile_info:
                            st.json(profile_info)
                        else:
                            st.error("❌ Failed to get profile info")
    
    with tab2:
        st.header("🚀 Batch Automation Runner")
        st.caption("Run automation projects on multiple profiles simultaneously")
        
        # Load available projects
        available_projects = load_available_projects()
        
        if not available_projects:
            st.warning("No projects found in the 'project' folder.")
            return
        
        # Configuration Section
        with st.expander("⚙️ Automation Configuration", expanded=True):
            col1, col2 = st.columns(2)
            
            with col1:
                selected_project = st.selectbox(
                    "📁 Select Project",
                    options=available_projects,
                    help="Choose the automation project to run"
                )
                
                max_threads = st.slider(
                    "🔢 Number of Threads",
                    min_value=1,
                    max_value=10,
                    value=5,
                    help="Number of profiles to run simultaneously"
                )
            
            with col2:
                auto_close_on_error = st.checkbox(
                    "❌ Auto Close on Error",
                    value=True,
                    help="Automatically close profile when encountering errors"
                )
                
                retry_on_error = st.number_input(
                    "🔄 Retry on Error",
                    min_value=0,
                    max_value=5,
                    value=0,
                    help="Number of retry attempts on error"
                )
        
        st.divider()
        
        # Profile Selection
        st.subheader("📋 Select Profiles")
        
        # Get all profiles
        profiles_data = client.get_profiles(page=1, per_page=200)
        profiles = profiles_data.get("data", [])
        
        if not profiles:
            st.warning("No profiles found. Add profiles in 43GPM first.")
            return
        
        # Multi-select profiles
        profile_options = [f"{p.get('name')} (ID: {p.get('id')[:8]}...)" for p in profiles]
        selected_profile_names = st.multiselect(
            "Choose Profiles to Run",
            options=profile_options,
            help="Select multiple profiles - they will be processed in order"
        )
        
        if selected_profile_names:
            st.success(f"✅ Selected {len(selected_profile_names)} profile(s)")
            
            # Show selected profiles with order
            with st.expander("📝 Selected Profiles (in order)", expanded=False):
                for idx, name in enumerate(selected_profile_names, 1):
                    st.write(f"{idx}. {name}")
        
        st.divider()
        
        # Control Buttons
        col_btn1, col_btn2, col_btn3, col_btn4 = st.columns(4)
        
        with col_btn1:
            start_button = st.button(
                "▶️ Start Automation",
                type="primary",
                width='stretch',
                disabled=st.session_state.runner_active or not selected_profile_names
            )
        
        with col_btn2:
            stop_button = st.button(
                "⏹️ Stop",
                width='stretch',
                disabled=not st.session_state.runner_active
            )
        
        with col_btn3:
            clear_button = st.button(
                "🗑️ Clear Results",
                width='stretch',
                disabled=st.session_state.runner_active
            )
        
        with col_btn4:
            refresh_button = st.button(
                "🔄 Refresh",
                width='stretch'
            )
        
        # Handle Start Button
        if start_button and selected_profile_names:
            # Create runner
            runner = ProfileAutomationRunner(client, max_threads=max_threads)
            st.session_state.automation_runner = runner
            
            # Add tasks
            for profile_name_display in selected_profile_names:
                # Extract profile from display name
                for profile in profiles:
                    if profile.get('name') in profile_name_display:
                        runner.add_task(
                            profile_id=profile.get('id'),
                            profile_name=profile.get('name'),
                            project_name=selected_project
                        )
                        break
            
            # Start runner
            runner.start(auto_close_on_error=auto_close_on_error, retry_on_error=retry_on_error)
            st.session_state.runner_active = True
            st.rerun()
        
        # Handle Stop Button
        if stop_button:
            if st.session_state.automation_runner:
                st.session_state.automation_runner.stop()
                st.session_state.runner_active = False
                st.success("Automation stopped")
                time.sleep(1)
                st.rerun()
        
        # Handle Clear Button
        if clear_button:
            cleanup_on_close()
            st.success("✅ All data cleared")
            time.sleep(1)
            st.rerun()
        
        st.divider()
        
        # Progress Display
        if st.session_state.automation_runner:
            runner = st.session_state.automation_runner
            
            # Get progress
            progress = runner.get_progress()
            
            st.subheader("📊 Progress")
            
            # Live status indicator
            if st.session_state.runner_active:
                st.success("🟢 **AUTOMATION RUNNING** - Live updates every 1 second")
            else:
                st.info("⚪ **AUTOMATION IDLE**")
            
            # Progress bar
            progress_bar = st.progress(progress['progress_percent'] / 100)
            st.caption(f"Progress: {progress['progress_percent']}%")
            
            # Metrics
            metric_cols = st.columns(5)
            with metric_cols[0]:
                st.metric("Total", progress['total'])
            with metric_cols[1]:
                st.metric("⏳ Pending", progress['pending'])
            with metric_cols[2]:
                st.metric("▶️ Running", progress['running'])
            with metric_cols[3]:
                st.metric("✅ Completed", progress['completed'])
            with metric_cols[4]:
                st.metric("❌ Error", progress['error'])
            
            st.divider()
            
            # Individual Profile Results
            st.subheader("📑 Profile Results")
            
            all_results = runner.get_all_results()
            
            if all_results:
                for profile_id, result in all_results.items():
                    profile_name = None
                    for profile in profiles:
                        if profile.get('id') == profile_id:
                            profile_name = profile.get('name')
                            break
                    
                    if not profile_name:
                        profile_name = profile_id[:12]
                    
                    # Status badge
                    status = result['status']
                    status_emoji = {
                        'pending': '⏳',
                        'running': '▶️',
                        'completed': '✅',
                        'error': '❌',
                        'failed': '❌'
                    }.get(status, '❓')
                    
                    with st.expander(f"{status_emoji} {profile_name} - {status.upper()}", expanded=(status == 'running')):
                        # Status info
                        st.write(f"**Status:** {status}")
                        if result.get('message'):
                            st.write(f"**Message:** {result['message']}")
                        if result.get('started_at'):
                            st.write(f"**Started:** {result['started_at'].strftime('%H:%M:%S')}")
                        if result.get('completed_at'):
                            duration = (result['completed_at'] - result['started_at']).total_seconds()
                            st.write(f"**Duration:** {duration:.1f}s")
                        
                        # Logs
                        logs = runner.get_profile_logs(profile_id)
                        if logs:
                            st.write(f"**Logs:** ({len(logs)} entries)")
                            
                            # Show all logs in a scrollable container
                            log_text = ""
                            for log in logs:
                                level_emoji = {
                                    'info': 'ℹ️',
                                    'success': '✅',
                                    'warning': '⚠️',
                                    'error': '❌'
                                }.get(log['level'], 'ℹ️')
                                log_text += f"[{log['timestamp']}] {level_emoji} {log['message']}\n"
                            
                            # Display in code block for better scrolling
                            st.code(log_text, language=None)
            
            # Auto-refresh if runner is active
            if st.session_state.runner_active:
                # Show live indicator
                st.info("🔄 Auto-refreshing... (Updates every 1 second)")
                time.sleep(1)
                st.rerun()
    
    with tab3:
        st.header("📊 Running Profiles Status")
        
        if not st.session_state.running_profiles:
            st.info("No profiles are currently running.")
        else:
            for profile_id, profile_data in st.session_state.running_profiles.items():
                with st.expander(f"🟢 {profile_data['name']}", expanded=True):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Profile ID:** `{profile_id}`")
                        st.write(f"**Started At:** {profile_data['started_at'].strftime('%Y-%m-%d %H:%M:%S')}")
                        st.write(f"**Browser:** {profile_data['data'].get('browser_location', 'N/A')}")
                    
                    with col2:
                        st.write(f"**Debug Address:** `{profile_data['data'].get('remote_debugging_address', 'N/A')}`")
                        st.write(f"**Driver Path:** {profile_data['data'].get('driver_path', 'N/A')}")
                    
                    if st.button(f"⏹️ Close {profile_data['name']}", key=f"close_{profile_id}"):
                        result = client.close_profile(profile_id)
                        if result.get("success"):
                            del st.session_state.running_profiles[profile_id]
                            st.success("Profile closed!")
                            st.rerun()
                        else:
                            error_msg = result.get("message", "Unknown error")
                            st.error(f"Failed to close profile: {error_msg}")
        
        st.divider()
        
        # System info
        st.subheader("System Information")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Running Profiles", len(st.session_state.running_profiles))
        with col2:
            st.metric("Available Projects", len(load_available_projects()))
        with col3:
            st.metric("API Status", "🟢 Online" if groups else "🔴 Offline")


if __name__ == "__main__":
    main()

