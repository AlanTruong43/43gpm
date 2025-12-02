# -*- coding: utf-8 -*-
"""
Advanced Automation Runner for 43GPM
Multi-threaded batch automation with individual logging and error handling
"""
import encoding_fix  # Fix Windows console encoding - must be first import

import threading
import queue
import time
from datetime import datetime
from typing import List, Dict, Any, Optional
import traceback
from api_client import GPMClient

# Use safe_str from encoding_fix
safe_str = encoding_fix.safe_str


class ProfileAutomationRunner:
    """
    Advanced automation runner with multi-threading and error handling
    """
    
    def __init__(self, client: GPMClient, max_threads: int = 5):
        self.client = client
        self.max_threads = max_threads
        self.task_queue = queue.Queue()
        self.results = {}
        self.logs = {}
        self.running = False
        self.threads = []
        self.lock = threading.Lock()
        
    def add_task(self, profile_id: str, profile_name: str, project_name: str):
        """Add a profile automation task to queue"""
        task = {
            "profile_id": profile_id,
            "profile_name": profile_name,
            "project_name": project_name,
            "status": "pending",
            "added_at": datetime.now()
        }
        self.task_queue.put(task)
        
        # Initialize result and log
        with self.lock:
            self.results[profile_id] = {
                "status": "pending",
                "message": "",
                "started_at": None,
                "completed_at": None
            }
            self.logs[profile_id] = []
    
    def log_message(self, profile_id: str, message: str, level: str = "info"):
        """Add log message for a profile"""
        with self.lock:
            timestamp = datetime.now().strftime("%H:%M:%S")
            # Safe message handling to avoid encoding errors
            safe_message = safe_str(message)
            log_entry = {
                "timestamp": timestamp,
                "level": level,
                "message": safe_message
            }
            self.logs[profile_id].append(log_entry)
    
    def update_result(self, profile_id: str, status: str, message: str = ""):
        """Update result for a profile"""
        with self.lock:
            self.results[profile_id]["status"] = status
            self.results[profile_id]["message"] = message
            if status == "running" and not self.results[profile_id]["started_at"]:
                self.results[profile_id]["started_at"] = datetime.now()
            elif status in ["completed", "error", "failed"]:
                self.results[profile_id]["completed_at"] = datetime.now()
    
    def run_single_profile(self, task: Dict[str, Any], 
                          auto_close_on_error: bool = True,
                          retry_on_error: int = 0) -> bool:
        """
        Run automation for a single profile
        
        Returns:
            True if successful, False otherwise
        """
        profile_id = task["profile_id"]
        profile_name = task["profile_name"]
        project_name = task["project_name"]
        
        profile_data = None
        attempt = 0
        max_attempts = retry_on_error + 1
        
        while attempt < max_attempts:
            try:
                if attempt > 0:
                    self.log_message(profile_id, f"Retry attempt {attempt}/{retry_on_error}", "warning")
                
                # Step 1: Open profile
                self.log_message(profile_id, f"Opening profile: {profile_name}", "info")
                self.update_result(profile_id, "running", "Opening profile...")
                
                result = self.client.start_profile(profile_id)
                
                if not result.get("success"):
                    error_msg = result.get("message", "Unknown error")
                    self.log_message(profile_id, f"Failed to open profile: {error_msg}", "error")
                    self.update_result(profile_id, "error", f"Cannot open profile: {error_msg}")
                    return False
                
                profile_data = result.get("data")
                self.log_message(profile_id, f"Profile opened successfully", "success")
                self.log_message(profile_id, f"Debug: {profile_data.get('remote_debugging_address')}", "info")
                
                # Wait for browser to stabilize
                time.sleep(2)
                
                # Step 2: Run automation project
                self.log_message(profile_id, f"Running project: {project_name}", "info")
                self.update_result(profile_id, "running", f"Running {project_name}...")
                
                # Import and run the project
                import importlib.util
                from pathlib import Path
                
                project_path = Path(f"project/{project_name}.py")
                
                if not project_path.exists():
                    self.log_message(profile_id, f"Project file not found: {project_path}", "error")
                    self.update_result(profile_id, "error", "Project file not found")
                    
                    if auto_close_on_error:
                        self.client.close_profile(profile_id)
                        self.log_message(profile_id, "Profile closed due to error", "info")
                    
                    return False
                
                # Load project module
                spec = importlib.util.spec_from_file_location(project_name, project_path)
                project_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(project_module)
                
                # Prepare data for project
                project_run_data = {
                    "profile_id": profile_id,
                    "profile_name": profile_name,
                    "remote_debugging_address": profile_data.get('remote_debugging_address'),
                    "browser_location": profile_data.get('browser_location'),
                    "driver_path": profile_data.get('driver_path')
                }
                
                # Run the project
                if hasattr(project_module, 'run'):
                    project_module.run(project_run_data)
                    self.log_message(profile_id, f"Project completed successfully", "success")
                    self.update_result(profile_id, "completed", "Success")
                    
                    # Close profile after success
                    self.log_message(profile_id, "Closing profile...", "info")
                    close_result = self.client.close_profile(profile_id)
                    
                    if close_result.get("success"):
                        self.log_message(profile_id, "Profile closed successfully", "success")
                    else:
                        error_msg = close_result.get("message", "Unknown error")
                        self.log_message(profile_id, f"Failed to close profile: {error_msg}", "warning")
                        # Try force close
                        time.sleep(1)
                        self.log_message(profile_id, "Retrying close...", "info")
                        close_result2 = self.client.close_profile(profile_id)
                        if close_result2.get("success"):
                            self.log_message(profile_id, "Profile closed on retry", "success")
                        else:
                            self.log_message(profile_id, "Failed to close profile (manual close required)", "error")
                    
                    return True
                else:
                    self.log_message(profile_id, "Project has no 'run' function", "error")
                    self.update_result(profile_id, "error", "No run function")
                    
                    if auto_close_on_error:
                        self.log_message(profile_id, "Closing profile due to error...", "warning")
                        close_result = self.client.close_profile(profile_id)
                        
                        if close_result.get("success"):
                            self.log_message(profile_id, "Profile closed due to error", "info")
                        else:
                            self.log_message(profile_id, "Failed to close profile", "error")
                    
                    return False
                    
            except Exception as e:
                error_trace = traceback.format_exc()
                # Safe error logging
                error_msg = safe_str(e)
                self.log_message(profile_id, f"Error: {error_msg}", "error")
                self.log_message(profile_id, f"Traceback: {error_trace}", "error")
                self.update_result(profile_id, "error", error_msg)
                
                attempt += 1
                
                if attempt < max_attempts:
                    self.log_message(profile_id, f"Will retry in 3 seconds...", "warning")
                    time.sleep(3)
                else:
                    # Close profile on final error
                    if auto_close_on_error and profile_data:
                        try:
                            self.log_message(profile_id, "Closing profile due to error...", "warning")
                            close_result = self.client.close_profile(profile_id)
                            
                            if close_result.get("success"):
                                self.log_message(profile_id, "Profile closed due to error", "info")
                            else:
                                self.log_message(profile_id, "Failed to close profile (manual close required)", "error")
                        except Exception as close_error:
                            self.log_message(profile_id, f"Error closing profile: {safe_str(close_error)}", "error")
                    
                    return False
        
        return False
    
    def worker(self, auto_close_on_error: bool = True, retry_on_error: int = 0):
        """Worker thread that processes tasks from queue"""
        while self.running:
            try:
                # Get task with timeout to allow checking self.running
                task = self.task_queue.get(timeout=1)
                
                profile_id = task["profile_id"]
                
                # Run the automation
                success = self.run_single_profile(task, auto_close_on_error, retry_on_error)
                
                # Mark task as done
                self.task_queue.task_done()
                
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Worker error: {e}")
                traceback.print_exc()
    
    def start(self, auto_close_on_error: bool = True, retry_on_error: int = 0):
        """Start the automation runner with worker threads"""
        if self.running:
            return
        
        self.running = True
        
        # Create worker threads
        for i in range(self.max_threads):
            thread = threading.Thread(
                target=self.worker,
                args=(auto_close_on_error, retry_on_error),
                daemon=True,
                name=f"Worker-{i+1}"
            )
            thread.start()
            self.threads.append(thread)
    
    def stop(self):
        """Stop the automation runner"""
        self.running = False
        
        # Wait for threads to finish
        for thread in self.threads:
            thread.join(timeout=2)
        
        self.threads = []
    
    def wait_completion(self):
        """Wait for all tasks to complete"""
        self.task_queue.join()
    
    def get_progress(self) -> Dict[str, Any]:
        """Get current progress statistics"""
        with self.lock:
            total = len(self.results)
            pending = sum(1 for r in self.results.values() if r["status"] == "pending")
            running = sum(1 for r in self.results.values() if r["status"] == "running")
            completed = sum(1 for r in self.results.values() if r["status"] == "completed")
            error = sum(1 for r in self.results.values() if r["status"] in ["error", "failed"])
            
            return {
                "total": total,
                "pending": pending,
                "running": running,
                "completed": completed,
                "error": error,
                "progress_percent": int((completed + error) / total * 100) if total > 0 else 0
            }
    
    def get_profile_logs(self, profile_id: str) -> List[Dict[str, str]]:
        """Get logs for a specific profile"""
        with self.lock:
            return self.logs.get(profile_id, []).copy()
    
    def get_profile_result(self, profile_id: str) -> Dict[str, Any]:
        """Get result for a specific profile"""
        with self.lock:
            return self.results.get(profile_id, {}).copy()
    
    def get_all_results(self) -> Dict[str, Any]:
        """Get all results"""
        with self.lock:
            return self.results.copy()
    
    def clear(self):
        """Clear all results and logs"""
        with self.lock:
            self.results = {}
            self.logs = {}
            # Clear queue
            while not self.task_queue.empty():
                try:
                    self.task_queue.get_nowait()
                    self.task_queue.task_done()
                except queue.Empty:
                    break

