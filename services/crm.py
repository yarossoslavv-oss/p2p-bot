"""
CRM-интеграция (заглушка для будущего подключения).
Реализуй под свою CRM: AmoCRM, Bitrix24, HubSpot, Notion, etc.

Чтобы подключить CRM:
1. Задай CRM_API_URL и CRM_API_KEY в .env
2. Реализуй метод create_lead() под API своей CRM
3. Вызови crm_service.create_lead(data) из handlers/survey.py
"""

import aiohttp
from loguru import logger
from config.settings import CRM_API_URL, CRM_API_KEY


class CRMService:
    def __init__(self):
        self.api_url = CRM_API_URL
        self.api_key = CRM_API_KEY
        self.enabled = bool(CRM_API_URL and CRM_API_KEY)

    async def create_lead(self, data: dict) -> bool:
        """
        Создать лид в CRM.
        Замени тело метода под API своей CRM.
        """
        if not self.enabled:
            logger.debug("CRM не настроена — пропускаем")
            return False

        payload = {
            "name": data.get("name"),
            "phone": "",
            "telegram": data.get("username"),
            "telegram_id": data.get("telegram_id"),
            "product": data.get("tariff_name"),
            "price": data.get("tariff_price"),
            "capital": data.get("capital"),
            "experience": data.get("experience"),
            "source": "telegram_bot",
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.api_url}/leads",
                    json=payload,
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    timeout=aiohttp.ClientTimeout(total=10),
                ) as resp:
                    if resp.status in (200, 201):
                        logger.info(f"Лид создан в CRM: {data.get('username')}")
                        return True
                    else:
                        body = await resp.text()
                        logger.error(f"CRM ответил {resp.status}: {body}")
                        return False
        except Exception as e:
            logger.error(f"Ошибка CRM: {e}")
            return False


crm_service = CRMService()
