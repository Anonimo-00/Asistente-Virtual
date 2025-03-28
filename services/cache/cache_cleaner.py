import os
import shutil
import time
import logging
from datetime import datetime, timedelta
from typing import Dict

class CacheCleaner:
    def __init__(self, base_dir="data/cache"):
        self.base_dir = base_dir
        self.cache_dirs = ['documents', 'images', 'audio', 'video', 'search']
        self.max_age_days = 7
        self.ensure_cache_dirs()
        
    def ensure_cache_dirs(self):
        """Asegura que existan los directorios de caché"""
        try:
            for subdir in self.cache_dirs:
                dir_path = os.path.join(self.base_dir, subdir)
                os.makedirs(dir_path, exist_ok=True)
        except Exception as e:
            logging.error(f"Error creando directorios de caché: {e}")
            
    def clean_old_files(self):
        """Elimina archivos más antiguos que max_age_days"""
        now = datetime.now()
        for root, _, files in os.walk(self.base_dir):
            for file in files:
                file_path = os.path.join(root, file)
                if self._is_old_file(file_path, now):
                    try:
                        os.remove(file_path)
                        logging.info(f"Archivo eliminado: {file_path}")
                    except Exception as e:
                        logging.error(f"Error eliminando {file_path}: {e}")
                        
    def _is_old_file(self, file_path: str, now: datetime) -> bool:
        """Verifica si un archivo es más antiguo que max_age_days"""
        try:
            mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
            return (now - mtime) > timedelta(days=self.max_age_days)
        except Exception:
            return False
            
    def clear_all(self):
        """Limpia todo el caché"""
        try:
            shutil.rmtree(self.base_dir)
            self.ensure_cache_dirs()
            logging.info("Caché limpiado completamente")
        except Exception as e:
            logging.error(f"Error limpiando caché: {e}")

    def get_cache(self, cache_type: str = None) -> str:
        """Obtiene información sobre los archivos en caché como string formateado"""
        try:
            cache_info = []
            
            if cache_type and cache_type in self.cache_dirs:
                info = self._get_dir_info(os.path.join(self.base_dir, cache_type))
                cache_info.append(f"{cache_type}: {info['files']} archivos ({self._format_size(info['size'])})")
            else:
                for subdir in self.cache_dirs:
                    info = self._get_dir_info(os.path.join(self.base_dir, subdir))
                    cache_info.append(f"{subdir}: {info['files']} archivos ({self._format_size(info['size'])})")
                    
            return "\n".join(cache_info) if cache_info else "Caché vacío"
            
        except Exception as e:
            logging.error(f"Error obteniendo caché: {e}")
            return f"Error obteniendo información del caché: {str(e)}"
            
    def _format_size(self, size: int) -> str:
        """Formatea el tamaño en bytes a una representación legible"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"
            
    def _get_dir_info(self, dir_path: str) -> Dict:
        """Obtiene información de un directorio de caché"""
        if not os.path.exists(dir_path):
            return {"files": 0, "size": 0}
            
        total_size = 0
        file_count = 0
        
        for root, _, files in os.walk(dir_path):
            for file in files:
                file_path = os.path.join(root, file)
                total_size += os.path.getsize(file_path)
                file_count += 1
                
        return {
            "files": file_count,
            "size": total_size,
            "path": dir_path
        }

cache_manager = CacheCleaner()
