import os
from dotenv import load_dotenv

load_dotenv()

# ── Telegram ──────────────────────────────────────────────────────────────────
BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
ADMIN_IDS: list[int] = [
    int(x.strip()) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip()
]

# ── Google Sheets ─────────────────────────────────────────────────────────────
GOOGLE_CREDENTIALS_FILE: str = os.getenv("GOOGLE_CREDENTIALS_FILE", "credentials.json")
GOOGLE_SHEET_ID: str = os.getenv("GOOGLE_SHEET_ID", "")
GOOGLE_SHEET_NAME: str = os.getenv("GOOGLE_SHEET_NAME", "Заявки")

# ── CRM (future) ──────────────────────────────────────────────────────────────
CRM_API_URL: str = os.getenv("CRM_API_URL", "")
CRM_API_KEY: str = os.getenv("CRM_API_KEY", "")

# ── Payments (future) ─────────────────────────────────────────────────────────
STRIPE_SECRET_KEY: str = os.getenv("STRIPE_SECRET_KEY", "")
CRYPTO_PAY_TOKEN: str = os.getenv("CRYPTO_PAY_TOKEN", "")

# ── App ───────────────────────────────────────────────────────────────────────
LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
TIMEZONE: str = os.getenv("TIMEZONE", "Europe/Moscow")

# ── Validation ────────────────────────────────────────────────────────────────
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is not set in .env file")
if not ADMIN_IDS:
    raise ValueError("ADMIN_IDS is not set in .env file")
