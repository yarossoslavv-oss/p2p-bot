"""
Google Sheets интеграция.
Документация: https://docs.gspread.org/
"""

import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
from loguru import logger

import pytz

from config.settings import (
    GOOGLE_CREDENTIALS_FILE,
    GOOGLE_SHEET_ID,
    GOOGLE_SHEET_NAME,
    TIMEZONE,
)

# Права доступа для сервисного аккаунта
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

# Заголовки таблицы
SHEET_HEADERS = [
    "Дата/Время",
    "Имя",
    "Telegram ID",
    "Username",
    "Тариф",
    "Цена",
    "Опыт",
    "Капитал",
    "Статус",  # для CRM-расширения (новый/в обработке/оплачен)
]


class GoogleSheetsService:
    def __init__(self):
        self._client: gspread.Client | None = None
        self._sheet: gspread.Worksheet | None = None

    def _get_client(self) -> gspread.Client:
        """Ленивая инициализация клиента."""
        if self._client is None:
            creds = Credentials.from_service_account_file(
                GOOGLE_CREDENTIALS_FILE, scopes=SCOPES
            )
            self._client = gspread.authorize(creds)
            logger.info("Google Sheets клиент инициализирован")
        return self._client

    def _get_sheet(self) -> gspread.Worksheet:
        """Получить лист, создав заголовки при первом запуске."""
        if self._sheet is None:
            client = self._get_client()
            spreadsheet = client.open_by_key(GOOGLE_SHEET_ID)

            try:
                self._sheet = spreadsheet.worksheet(GOOGLE_SHEET_NAME)
                logger.info(f"Открыт лист: {GOOGLE_SHEET_NAME}")
            except gspread.WorksheetNotFound:
                # Создаём лист с заголовками если не существует
                self._sheet = spreadsheet.add_worksheet(
                    title=GOOGLE_SHEET_NAME, rows=1000, cols=20
                )
                self._sheet.append_row(SHEET_HEADERS)
                logger.info(f"Создан новый лист: {GOOGLE_SHEET_NAME}")

        return self._sheet

    async def save_application(self, data: dict) -> bool:
        """
        Сохранить заявку в Google Sheets.

        data = {
            "name": str,
            "telegram_id": int,
            "username": str,
            "tariff_id": str,
            "tariff_name": str,
            "tariff_price": str,
            "experience": str,
            "capital": str,
        }
        """
        try:
            tz = pytz.timezone(TIMEZONE)
            now = datetime.now(tz).strftime("%d.%m.%Y %H:%M")

            row = [
                now,
                data.get("name", ""),
                str(data.get("telegram_id", "")),
                data.get("username", ""),
                data.get("tariff_name", ""),
                data.get("tariff_price", ""),
                data.get("experience", ""),
                data.get("capital", ""),
                "Новый",  # начальный статус
            ]

            sheet = self._get_sheet()
            sheet.append_row(row)
            logger.info(f"Заявка сохранена в Sheets: {data.get('username')} → {data.get('tariff_name')}")
            return True

        except Exception as e:
            logger.error(f"Ошибка сохранения в Google Sheets: {e}")
            return False

    def health_check(self) -> bool:
        """Проверка подключения."""
        try:
            self._get_sheet()
            return True
        except Exception as e:
            logger.error(f"Google Sheets health check failed: {e}")
            return False


# Синглтон сервиса
sheets_service = GoogleSheetsService()
