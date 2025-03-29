import json
import os
import hashlib
import time
from pathlib import Path
from typing import Any, Optional

class ServiceCache:
    """Gestor centralizado de caché para servicios"""
    
    def __init__(self, service_name: str, max_age: int = 3600):
        self.cache_dir = Path("services/cache") / service_name
        self.max_age = max_age
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def get(self, key: str) -> Optional[Any]:
        cache_file = self.cache_dir / self._hash_key(key)
        if not cache_file.exists():
            return None
            
        try:
            data = json.loads(cache_file.read_text())
            if time.time() - data['timestamp'] > self.max_age:
                cache_file.unlink()
                return None
            return data['value']
        except Exception:
            return None

    def set(self, key: str, value: Any) -> None:
        try:
            cache_file = self.cache_dir / self._hash_key(key)
            data = {
                'timestamp': time.time(),
                'value': value
            }
            cache_file.write_text(json.dumps(data))
        except Exception:
            pass

    def _hash_key(self, key: str) -> str:
        return hashlib.md5(key.encode()).hexdigest()

    def clear(self) -> None:
        """Limpia todo el caché del servicio"""
        for file in self.cache_dir.glob('*'):
            try:
                file.unlink()
            except Exception:
                pass

    def cleanup(self) -> None:
        """Limpia solo el caché expirado"""
        current_time = time.time()
        for file in self.cache_dir.glob('*'):
            try:
                data = json.loads(file.read_text())
                if current_time - data['timestamp'] > self.max_age:
                    file.unlink()
            except Exception:
                file.unlink()
