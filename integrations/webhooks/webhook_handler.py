from typing import Dict, Any

class WebhookHandler:
    def __init__(self):
        self.routes = {}

    def register_webhook(self, path: str, handler):
        self.routes[path] = handler

    async def handle_webhook(self, path: str, data: Dict[str, Any]) -> Dict[str, Any]:
        if path in self.routes:
            return await self.routes[path](data)
        return {"error": "Webhook no encontrado"}
