# -*- coding: utf-8 -*-
"""
FastAPI Server for 43GPM External Automation
Supports:
1. Manual Port: /execute/{project}?port=9222
2. Auto Port (via Profile ID): /execute/{project}?profile_id=xxx
"""
import encoding_fix
from fastapi import FastAPI, HTTPException, BackgroundTasks, Query, Request
from pydantic import BaseModel
import importlib.util
from pathlib import Path
import logging
import uvicorn
import socket
from api_client import GPMClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("API_Server")

app = FastAPI(title="43GPM External Automation API")
gpm_client = GPMClient() # Default to 127.0.0.1:19995

class AutomationRequest(BaseModel):
    remote_debugging_address: str
    profile_name: str = "External Profile"
    profile_id: str = "external_id"
    driver_path: str = ""

def check_port(host: str, port: int) -> bool:
    """Verify if a port is listening"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    result = sock.connect_ex((host, port))
    sock.close()
    return result == 0

def run_automation_task(project_name: str, data: AutomationRequest, extra_params: dict = None):
    """Function to run automation in background"""
    try:
        project_path = Path(f"project/{project_name}.py")
        if not project_path.exists():
            print(f">>> [ERROR] Project {project_name} not found")
            return

        # Double check port before passing to Selenium
        host, port = data.remote_debugging_address.split(':')
        if not check_port(host, int(port)):
            print(f">>> [ERROR] Connection lost to port {port}")
            return

        # Load project module
        spec = importlib.util.spec_from_file_location(project_name, project_path)
        project_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(project_module)

        if hasattr(project_module, 'run'):
            print(f">>> [DEBUG] Executing {project_name} on {data.remote_debugging_address}")
            profile_data = {
                "profile_id": data.profile_id,
                "profile_name": data.profile_name,
                "remote_debugging_address": data.remote_debugging_address,
                "browser_location": "",
                "driver_path": data.driver_path
            }
            # Merge extra parameters
            if extra_params:
                profile_data.update(extra_params)
                
            project_module.run(profile_data)
        else:
            print(f">>> [ERROR] No run() function in {project_name}")
    except Exception as e:
        print(f">>> [ERROR] Background task failed: {str(e)}")

@app.get("/")
async def root():
    return {
        "status": "online",
        "usage": {
            "auto_port": "GET /execute/twitter?profile_id=ID_CUA_BAN",
            "manual_port": "GET /execute/twitter?port=9222"
        }
    }

@app.get("/execute/{project_name}")
async def execute_get(
    project_name: str, 
    background_tasks: BackgroundTasks,
    request: Request,
    profile_id: str = Query(None, description="Profile ID (Auto detect port)"),
    port: str = Query(None, description="Manual port"),
    host: str = "127.0.0.1"
):
    """
    GET Method: Supports both manual port and auto detection via profile_id
    """
    # Capture all query parameters
    extra_params = dict(request.query_params)
    # Remove standard params from extra_params
    for key in ["profile_id", "port", "host"]:
        extra_params.pop(key, None)
    debug_address = None
    driver_path = ""
    
    # Priority 1: Use Profile ID to auto-detect port
    if profile_id:
        print(f">>> [DEBUG] Auto-detecting port for Profile ID: {profile_id}")
        result = gpm_client.start_profile(profile_id)
        if result.get("success") and result.get("data"):
            debug_address = result["data"].get("remote_debugging_address")
            driver_path = result["data"].get("driver_path", "")
            print(f">>> [DEBUG] Found running port: {debug_address}")
            print(f">>> [DEBUG] Driver Path: {driver_path}")
        else:
            error_msg = result.get("message", "Unknown error")
            raise HTTPException(status_code=400, detail=f"Cannot find port for profile: {error_msg}")
    
    # Priority 2: Use manual port
    elif port:
        debug_address = f"{host}:{port}"
        print(f">>> [DEBUG] Using manual port: {debug_address}")
    
    else:
        raise HTTPException(status_code=400, detail="Missing parameter: 'profile_id' or 'port' is required")

    # Final check before queueing
    h, p = debug_address.split(':')
    if not check_port(h, int(p)):
        raise HTTPException(status_code=502, detail=f"Port {p} is not responding. Is the browser open?")

    data = AutomationRequest(
        remote_debugging_address=debug_address,
        profile_id=profile_id if profile_id else "external_id",
        driver_path=driver_path
    )
    
    background_tasks.add_task(run_automation_task, project_name, data, extra_params)
    return {"status": "queued", "project": project_name, "address": debug_address, "extra_params": extra_params}

@app.post("/execute/{project_name}")
async def execute_post(project_name: str, data: AutomationRequest, background_tasks: BackgroundTasks):
    background_tasks.add_task(run_automation_task, project_name, data)
    return {"status": "queued", "project": project_name}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
