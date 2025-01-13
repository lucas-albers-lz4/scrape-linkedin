import json
import os
from src.config import get_chrome_options

def list_chrome_profiles():
    """List all available Chrome profiles and their debugging ports"""
    
    chrome_config = get_chrome_options()
    chrome_dir = chrome_config['user_data_dir']
    local_state_path = os.path.join(chrome_dir, "Local State")
    
    try:
        # Read Chrome's Local State file
        with open(local_state_path, 'r') as f:
            local_state = json.load(f)
            
        # Get profile information
        profiles = local_state.get('profile', {}).get('info_cache', {})
        
        print("\nAvailable Chrome Profiles:")
        print("-" * 50)
        for profile_dir, profile_info in profiles.items():
            print(f"Profile Directory: {profile_dir}")
            print(f"Profile Name: {profile_info.get('name', 'Unknown')}")
            print(f"User Name: {profile_info.get('user_name', 'Unknown')}")
            print("-" * 30)
            
        return profiles
            
    except Exception as e:
        print(f"Error reading Chrome profiles: {e}")
        return None

# Use this before connecting to Chrome
profiles = list_chrome_profiles()
print (profiles)

