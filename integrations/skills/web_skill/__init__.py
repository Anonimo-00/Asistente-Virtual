from services.cache import ServiceCache
import aiohttp
import json

class WebSkill:
    def __init__(self):
        self.cache = ServiceCache(
            service_name="web_skill",
            max_age=3600  # 1 hora de caché
        )

    async def fetch_url(self, url: str) -> str:
        # Intentar obtener de caché primero
        cached = self.cache.get(url)
        if cached:
            return cached
            
        # Si no está en caché, hacer la petición
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                content = await response.text()
                # Guardar en caché
                self.cache.set(url, content)
                return content
