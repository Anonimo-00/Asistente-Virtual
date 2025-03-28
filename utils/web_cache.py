import os
import hashlib
import mimetypes
from urllib.parse import urlparse, unquote
import requests
from bs4 import BeautifulSoup
import re
import logging

class WebCache:
    def __init__(self, cache_dir="cache"):
        self.cache_dir = cache_dir
        self.base_dir = os.path.join("data", cache_dir)
        self._setup_cache_dirs()
        
    def _setup_cache_dirs(self):
        """Crear estructura de directorios para caché"""
        subdirs = ['documents', 'images', 'audio', 'video']
        for subdir in subdirs:
            dir_path = os.path.join(self.base_dir, subdir)
            os.makedirs(dir_path, exist_ok=True)

    def _get_file_type(self, url, content_type=None):
        """Determinar tipo de archivo"""
        if content_type:
            if 'image' in content_type: return 'images'
            if 'audio' in content_type: return 'audio'
            if 'video' in content_type: return 'video'
            if 'pdf' in content_type or 'document' in content_type: return 'documents'
        
        ext = os.path.splitext(urlparse(url).path)[1].lower()
        if ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']: return 'images'
        if ext in ['.mp3', '.wav', '.ogg']: return 'audio'
        if ext in ['.mp4', '.webm', '.avi']: return 'video'
        if ext in ['.pdf', '.doc', '.docx', '.txt']: return 'documents'
        return None

    def _get_cache_path(self, url, file_type):
        """Generar ruta de archivo en caché"""
        url_hash = hashlib.md5(url.encode()).hexdigest()
        filename = unquote(os.path.basename(urlparse(url).path))
        if not filename:
            filename = url_hash
        return os.path.join(self.base_dir, file_type, f"{url_hash}_{filename}")

    def cache_url(self, url, headers=None):
        """Cachear contenido y archivos de una URL"""
        try:
            response = requests.get(url, headers=headers, stream=True)
            response.raise_for_status()
            
            # Si es un archivo descargable directamente
            content_type = response.headers.get('content-type', '')
            file_type = self._get_file_type(url, content_type)
            
            if file_type:
                cache_path = self._get_cache_path(url, file_type)
                with open(cache_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                return {'type': file_type, 'path': cache_path}
            
            # Si es una página HTML, buscar recursos
            if 'text/html' in content_type:
                soup = BeautifulSoup(response.text, 'html.parser')
                cached_resources = []
                
                # Buscar imágenes
                for img in soup.find_all('img', src=True):
                    img_url = img['src']
                    if not img_url.startswith(('http://', 'https://')):
                        img_url = f"{url.rstrip('/')}/{img_url.lstrip('/')}"
                    cached_resources.append(self.cache_url(img_url, headers))
                
                # Buscar documentos
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    if self._get_file_type(href):
                        if not href.startswith(('http://', 'https://')):
                            href = f"{url.rstrip('/')}/{href.lstrip('/')}"
                        cached_resources.append(self.cache_url(href, headers))
                
                return {'type': 'html', 'resources': cached_resources}
                
        except Exception as e:
            logging.error(f"Error cacheando {url}: {str(e)}")
            return None
