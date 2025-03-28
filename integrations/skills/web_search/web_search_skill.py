from typing import Dict, List
import time
from bs4 import BeautifulSoup
import requests
from integrations.skills import SkillBase
import urllib.parse
from functools import lru_cache
import random
from utils.web_cache import WebCache
import yaml

class SearchOperators:
    SITE = "site:"
    FILETYPE = "filetype:"
    INURL = "inurl:"
    INTITLE = "intitle:"
    EXCLUDE = "-"
    OR = " OR "
    EXACT = '"'

class WebSearchSkill(SkillBase):
    def __init__(self):
        super().__init__()
        self._description = "Realiza búsquedas web con operadores avanzados"
        self._load_config()
        self.search_count = 0  # Contador para rotación de user agents
        
    def _load_config(self):
        try:
            with open('config/credentials.yml', 'r') as f:
                config = yaml.safe_load(f)
                search_config = config.get('search', {})
                
                # Configuración del motor de búsqueda
                self.engines = search_config.get('engines', {})
                self.current_engine = self.engines.get('current', 'google')
                
                # Configuración de user agents
                ua_config = search_config.get('user_agents', {})
                self.rotate_agents = ua_config.get('rotate', True)
                self.rotation_interval = ua_config.get('interval', 10)
                self.agents = ua_config.get('agents', {})
                self.current_agent = ua_config.get('current', 'chrome')
                
                # Configuración de headers
                headers_config = search_config.get('headers', {})
                self._update_headers()
                
        except Exception as e:
            print(f"Error cargando configuración: {e}")
            
    def _update_headers(self):
        """Actualiza los headers según la configuración"""
        headers_config = yaml.safe_load(open('config/credentials.yml')).get('search', {}).get('headers', {})
        agents = self.agents.get(self.current_agent, [])
        
        self.headers = {
            'User-Agent': random.choice(agents) if agents else self.agents['chrome'][0],
            **{k: v for k, v in headers_config.items() if v}
        }
        
    def _rotate_user_agent(self):
        """Rota el user agent si corresponde"""
        if self.rotate_agents and self.search_count % self.rotation_interval == 0:
            available_agents = list(self.agents.keys())
            current_index = available_agents.index(self.current_agent)
            self.current_agent = available_agents[(current_index + 1) % len(available_agents)]
            self._update_headers()

    @lru_cache(maxsize=100)
    def _cached_search(self, query: str, num_results: int) -> List[Dict]:
        """Versión cacheada de la búsqueda"""
        return self._google_search(query, num_results)

    def execute(self, params: Dict) -> Dict:
        self.search_count += 1
        self._rotate_user_agent()
        query = params.get("query", "").strip()
        num_results = params.get("num_results", 5)
        operators = params.get("operators", {})

        if not query:
            return {"error": "La consulta de búsqueda no puede estar vacía"}

        try:
            final_query = self._build_query(query, operators)
            search_results = self._cached_search(final_query, num_results)
            if not search_results:
                return {"error": "No se encontraron resultados"}
                
            return {
                "success": True,
                "results": search_results,
                "query": final_query,
                "cached": True
            }
        except Exception as e:
            return {"error": f"Error en la búsqueda: {str(e)}"}

    def _build_query(self, query: str, operators: Dict) -> str:
        """Construye la consulta con operadores de Google"""
        parts = [query]
        
        if "site" in operators:
            parts.append(f"{SearchOperators.SITE}{operators['site']}")
            
        if "filetype" in operators:
            parts.append(f"{SearchOperators.FILETYPE}{operators['filetype']}")
            
        if "inurl" in operators:
            parts.append(f"{SearchOperators.INURL}{operators['inurl']}")
            
        if "intitle" in operators:
            parts.append(f"{SearchOperators.INTITLE}{operators['intitle']}")
            
        if "exclude" in operators:
            for term in operators["exclude"]:
                parts.append(f"{SearchOperators.EXCLUDE}{term}")
                
        if "exact" in operators:
            parts = [f'{SearchOperators.EXACT}{query}{SearchOperators.EXACT}']
            
        return " ".join(parts)

    def _google_search(self, query: str, num_results: int) -> List[Dict]:
        last_error = None
        engine = self.engines.get(self.current_engine, {})
        
        if not engine:
            raise Exception(f"Motor de búsqueda {self.current_engine} no configurado")
            
        for attempt in range(self.max_retries):
            try:
                # Rotar user agent en cada intento
                self.headers['User-Agent'] = random.choice(self.user_agents)
                
                encoded_query = urllib.parse.quote(query)
                url = f"{engine['base_url']}?q={encoded_query}&num={num_results*2}&hl=es"
                
                response = requests.get(url, headers=self.headers, timeout=10)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'html.parser')
                
                selectors = engine['selectors']
                search_results = []
                
                for result in soup.select(selectors['result']):
                    if len(search_results) >= num_results:
                        break
                        
                    try:
                        title_element = result.select_one(selectors['title'])
                        link_element = result.select_one(selectors['link'])
                        snippet_element = result.select_one(selectors['snippet'])
                        
                        if not title_element or not link_element:
                            continue
                            
                        url = link_element['href']
                        if not url.startswith(('http://', 'https://')):
                            continue
                            
                        title = title_element.get_text(strip=True)
                        snippet = snippet_element.get_text(strip=True) if snippet_element else ""
                        
                        # Verificar si coincide con los operadores
                        if self._validate_result(url, title, query):
                            search_results.append({
                                "title": title,
                                "url": url,
                                "snippet": snippet,
                                "content": f"Resultado encontrado en: {url}"
                            })
                            
                    except Exception as e:
                        print(f"Error procesando resultado: {e}")
                        continue
                        
                if search_results:
                    return search_results
                    
            except Exception as e:
                last_error = str(e)
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                continue
                
        raise Exception(f"No se pudieron obtener resultados después de {self.max_retries} intentos. Último error: {last_error}")

    def _validate_result(self, url: str, title: str, query: str) -> bool:
        """Valida si el resultado coincide con los operadores de búsqueda"""
        parts = query.lower().split()
        
        for part in parts:
            if part.startswith(SearchOperators.SITE):
                site = part[len(SearchOperators.SITE):]
                if site not in url.lower():
                    return False
            elif part.startswith(SearchOperators.INURL):
                term = part[len(SearchOperators.INURL):]
                if term not in url.lower():
                    return False
            elif part.startswith(SearchOperators.INTITLE):
                term = part[len(SearchOperators.INTITLE):]
                if term not in title.lower():
                    return False
                    
        return True

    def _is_safe_url(self, url: str) -> bool:
        """Verifica si una URL parece segura para extraer contenido"""
        unsafe_keywords = ['login', 'signin', 'account', 'password']
        return not any(keyword in url.lower() for keyword in unsafe_keywords)
        
    def _extract_page_content(self, url: str) -> str:
        try:
            # Cachear contenido y recursos de la página
            cache_result = self.web_cache.cache_url(url, headers=self.headers)
            
            response = requests.get(url, headers=self.headers, timeout=5)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Eliminar elementos no deseados
            for element in soup(['script', 'style', 'nav', 'header', 'footer', 'iframe']):
                element.decompose()
                
            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            cached_info = ""
            if cache_result and cache_result.get('resources'):
                num_resources = len(cache_result['resources'])
                cached_info = f"\n[{num_resources} recursos descargados en caché]"
            
            return text[:5000] + cached_info
            
        except Exception as e:
            return f"No se pudo extraer el contenido: {str(e)}"
