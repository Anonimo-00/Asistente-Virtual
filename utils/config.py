import os
from typing import Dict, Any
from utils.helpers import load_config, safe_get

class Config:
    def __init__(self, config_path: str = None):
        self.config_data: Dict[str, Any] = load_config(config_path)
        self.credentials_data: Dict[str,Any] = load_config(os.path.join("config", "credentials.yml"))
        
    def get_config(self, path: str, default: Any = None) -> Any:
        return safe_get(self.config_data, path, default)
    
    def get_credentials(self, path: str, default: Any = None) -> Any:
        return safe_get(self.credentials_data, path, default)

    def get_all_config(self) -> Dict[str, Any]:
        return self.config_data

    def get_all_credentials(self) -> Dict[str, Any]:
        return self.credentials_data
