import os
import shutil
import json
import logging
from datetime import datetime
from typing import List, Dict
from pathlib import Path

logger = logging.getLogger(__name__)

class BackupManager:
    def __init__(self, config_path: str = "config/settings.json"):
        self.config = self._load_config(config_path)
        self.backup_path = Path(self.config.get("backup", {}).get("backup_path", "backup/"))
        
        # Crear estructura de carpetas
        self._create_backup_structure()

    def _load_config(self, config_path: str) -> Dict:
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error cargando configuración: {e}")
            return {}

    def _create_backup_structure(self):
        """Crea la estructura de carpetas necesaria para backups"""
        directories = [
            self.backup_path / "daily",
            self.backup_path / "weekly",
            self.backup_path / "monthly",
            self.backup_path / "manual"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

    def create_backup(self, backup_type: str = "manual") -> bool:
        """
        Crea un nuevo backup
        backup_type: "daily", "weekly", "monthly" o "manual"
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir = self.backup_path / backup_type / f"backup_{timestamp}"
            
            # Crear directorio de backup
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            # Copiar directorios configurados
            dirs_to_backup = self.config.get("backup", {}).get("directories_to_backup", [])
            for dir_name in dirs_to_backup:
                src_path = Path(dir_name)
                if src_path.exists():
                    dst_path = backup_dir / dir_name
                    shutil.copytree(src_path, dst_path)
            
            self._cleanup_old_backups(backup_type)
            logger.info(f"Backup creado exitosamente en {backup_dir}")
            return True
            
        except Exception as e:
            logger.error(f"Error creando backup: {e}")
            return False

    def _cleanup_old_backups(self, backup_type: str):
        """Elimina backups antiguos según configuración"""
        try:
            max_backups = self.config.get("backup", {}).get("max_backups", 5)
            backup_dir = self.backup_path / backup_type
            
            backups = sorted(
                [d for d in backup_dir.iterdir() if d.is_dir()],
                key=lambda x: x.stat().st_mtime
            )
            
            while len(backups) > max_backups:
                shutil.rmtree(backups[0])
                backups.pop(0)
                
        except Exception as e:
            logger.error(f"Error limpiando backups antiguos: {e}")

    def restore_backup(self, backup_path: str) -> bool:
        """Restaura un backup específico"""
        try:
            backup_dir = Path(backup_path)
            if not backup_dir.exists():
                logger.error(f"Directorio de backup no encontrado: {backup_path}")
                return False
                
            # Restaurar cada directorio
            dirs_to_backup = self.config.get("backup", {}).get("directories_to_backup", [])
            for dir_name in dirs_to_backup:
                src_path = backup_dir / dir_name
                if src_path.exists():
                    dst_path = Path(dir_name)
                    if dst_path.exists():
                        shutil.rmtree(dst_path)
                    shutil.copytree(src_path, dst_path)
                    
            logger.info(f"Backup restaurado desde {backup_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error restaurando backup: {e}")
            return False
