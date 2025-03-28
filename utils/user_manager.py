import json
import os
from typing import Dict, Any, List
from pathlib import Path

class UserManager:
    _instance = None
    _profile_path = Path("data/user/profile.json")

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(UserManager, cls).__new__(cls)
            cls._instance._load_profile()
        return cls._instance

    def _load_profile(self):
        """Carga el perfil del usuario"""
        if self._profile_path.exists():
            with open(self._profile_path, 'r', encoding='utf-8') as f:
                self._profile = json.load(f)
        else:
            self._profile_path.parent.mkdir(parents=True, exist_ok=True)
            self._profile = {
                "nombre": "Usuario",
                "preferencias": {"tema": "dark", "idioma": "es"},
                "datos_personales": {},
                "intereses": [],
                "historial": {"conversaciones": [], "comandos": []}
            }
            self._save_profile()

    def _save_profile(self):
        """Guarda el perfil en disco"""
        with open(self._profile_path, 'w', encoding='utf-8') as f:
            json.dump(self._profile, f, indent=4, ensure_ascii=False)

    def actualizar_dato(self, categoria: str, clave: str, valor: Any):
        """Actualiza un dato del perfil"""
        if categoria not in self._profile:
            self._profile[categoria] = {}
        self._profile[categoria][clave] = valor
        self._save_profile()

    def obtener_dato(self, categoria: str, clave: str) -> Any:
        """Obtiene un dato del perfil"""
        return self._profile.get(categoria, {}).get(clave)

    def agregar_historial(self, tipo: str, dato: Dict):
        """Agrega una entrada al historial"""
        if tipo not in self._profile["historial"]:
            self._profile["historial"][tipo] = []
        self._profile["historial"][tipo].append(dato)
        self._save_profile()
