"""
Google Sheets интеграция.
Документация: https://docs.gspread.org/
"""

import os
import json
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
    "Статус",
]


class GoogleSheetsService:
    def __init__(self):
        self._client: gspread.Client | None = None
        self._sheet: gspread.Worksheet | None = None

    def _get_client(self) -> gspread.Client:
        """
        Ленивая инициализация клиента.
        Сначала пробует прочитать credentials из переменной окружения
        GOOGLE_CREDENTIALS_JSON (для Railway), если нет — читает из файла.
        """
        if self._client is None:
            credentials_json = os.getenv("GOOGLE_CREDENTIALS_JSON")
            if credentials_json:
                # Railway: читаем из переменной окружения
                info = json.loads(credentials_json)
                creds = Credentials.from_service_account_info(info, scopes=SCOPES)
                logger.info("Google Sheets: credentials загружены из переменной окружения")
            else:
                # Локально: читаем из файла credentials.json
                creds = Credentials.from_service_account_file(
                    GOOGLE_CREDENTIALS_FILE, scopes=SCOPES
                )
                logger.info("Google Sheets: credentials загружены из файла")
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
                self._sheet = spreadsheet.add_worksheet(
                    title=GOOGLE_SHEET_NAME, rows=1000, cols=20
                )
                self._sheet.append_row(SHEET_HEADERS)
                logger.info(f"Создан новый лист: {GOOGLE_SHEET_NAME}")

        return self._sheet

    async def save_application(self, data: dict) -> bool:
        """Сохранить заявку в Google Sheets."""
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
                "Новый",
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
