"""
API Client for 43GPM Antidetect Browser
"""
import requests
from typing import Optional, Dict, List, Any


class GPMClient:
    """Client for interacting with GPM Login API"""
    
    def __init__(self, base_url: str = "http://127.0.0.1:19995"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def get_groups(self) -> List[Dict[str, Any]]:
        """
        Get list of profile groups
        
        Returns:
            List of groups with id, name, etc.
        """
        try:
            response = self.session.get(f"{self.base_url}/api/v3/groups")
            response.raise_for_status()
            result = response.json()
            if result.get("success"):
                return result.get("data", [])
            return []
        except Exception as e:
            print(f"Error getting groups: {e}")
            return []
    
    def get_profiles(
        self,
        group_id: Optional[str] = None,
        page: int = 1,
        per_page: int = 100,
        sort: int = 0,
        search: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get list of profiles
        
        Args:
            group_id: Filter by group ID
            page: Page number (default 1)
            per_page: Number of profiles per page (default 100)
            sort: 0-Newest, 1-Old to new, 2-Name A-Z, 3-Name Z-A
            search: Search keyword for profile name
            
        Returns:
            Dict with 'data' (profiles list) and 'pagination' info
        """
        params = {
            "page": page,
            "per_page": per_page,
            "sort": sort
        }
        
        if group_id:
            params["group_id"] = group_id
        if search:
            params["search"] = search
            
        try:
            response = self.session.get(
                f"{self.base_url}/api/v3/profiles",
                params=params
            )
            response.raise_for_status()
            result = response.json()
            
            if result.get("success"):
                return {
                    "data": result.get("data", []),
                    "pagination": result.get("pagination", {})
                }
            return {"data": [], "pagination": {}}
        except Exception as e:
            print(f"Error getting profiles: {e}")
            return {"data": [], "pagination": {}}
    
    def get_profile_info(self, profile_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information of a specific profile
        
        Args:
            profile_id: Profile ID
            
        Returns:
            Profile information dict or None if error
        """
        try:
            response = self.session.get(
                f"{self.base_url}/api/v3/profiles/{profile_id}"
            )
            response.raise_for_status()
            result = response.json()
            
            if result.get("success"):
                return result.get("data")
            return None
        except Exception as e:
            print(f"Error getting profile info: {e}")
            return None
    
    def start_profile(
        self,
        profile_id: str,
        win_scale: Optional[float] = None,
        win_pos: Optional[str] = None,
        win_size: Optional[str] = None,
        additional_args: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Start/Open a profile browser
        
        Args:
            profile_id: Profile ID
            win_scale: Window scale (0 to 1.0)
            win_pos: Window position (x,y)
            win_size: Window size (width,height)
            additional_args: Additional browser startup arguments
            
        Returns:
            Dict with:
                - success: bool
                - data: Dict with browser info (if success)
                - message: Error message (if failed)
        """
        params = {}
        if win_scale is not None:
            params["win_scale"] = win_scale
        if win_pos:
            params["win_pos"] = win_pos
        if win_size:
            params["win_size"] = win_size
        if additional_args:
            params["additional_args"] = additional_args
            
        try:
            response = self.session.get(
                f"{self.base_url}/api/v3/profiles/start/{profile_id}",
                params=params
            )
            response.raise_for_status()
            result = response.json()
            
            return {
                "success": result.get("success", False),
                "data": result.get("data"),
                "message": result.get("message", "Unknown error")
            }
        except Exception as e:
            print(f"Error starting profile: {e}")
            return {
                "success": False,
                "data": None,
                "message": f"Connection error: {str(e)}"
            }
    
    def close_profile(self, profile_id: str) -> Dict[str, Any]:
        """
        Close a profile browser
        
        Args:
            profile_id: Profile ID
            
        Returns:
            Dict with:
                - success: bool
                - message: Success or error message
        """
        try:
            response = self.session.get(
                f"{self.base_url}/api/v3/profiles/close/{profile_id}"
            )
            response.raise_for_status()
            result = response.json()
            
            return {
                "success": result.get("success", False),
                "message": result.get("message", "Unknown error")
            }
        except Exception as e:
            print(f"Error closing profile: {e}")
            return {
                "success": False,
                "message": f"Connection error: {str(e)}"
            }

