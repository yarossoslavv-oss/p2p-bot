# 🤖 P2P Trading Bot

Telegram-бот для продажи обучения по P2P-трейдингу.
Стек: **Python 3.11+ · aiogram 3 · Google Sheets API · FSM**

---

## 📁 Структура проекта

```
p2p_bot/
├── bot.py                  # Точка входа
├── requirements.txt
├── .env                    # Твои секреты (не коммить!)
├── .env.example
├── credentials.json        # Google Service Account (не коммить!)
│
├── config/
│   ├── settings.py         # Переменные окружения
│   └── tariffs.py          # ← ТАРИФЫ РЕДАКТИРУЮТСЯ ЗДЕСЬ
│
├── handlers/
│   ├── start.py            # /start, показ тарифов
│   ├── survey.py           # FSM-опрос, подтверждение
│   └── admin.py            # /admin, /healthcheck, /stats
│
├── keyboards/
│   └── inline.py           # Все inline-клавиатуры
│
├── services/
│   ├── sheets.py           # Google Sheets интеграция
│   ├── notifications.py    # Уведомления администратора
│   └── crm.py              # CRM-заглушка (для расширения)
│
├── middlewares/
│   └── logging_middleware.py
│
└── utils/
    ├── states.py           # FSM состояния
    └── validators.py       # Валидация ввода
```

---

## 🚀 Быстрый старт

### 1. Клонируй и установи зависимости

```bash
git clone <repo>
cd p2p_bot
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Создай `.env` файл

```bash
cp .env.example .env
```

Заполни `.env`:

```env
BOT_TOKEN=1234567890:AABBccDDeeFF...     # от @BotFather
ADMIN_IDS=123456789                       # твой Telegram ID (узнай у @userinfobot)
GOOGLE_CREDENTIALS_FILE=credentials.json
GOOGLE_SHEET_ID=1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgVE2upms
GOOGLE_SHEET_NAME=Заявки
TIMEZONE=Europe/Moscow
```

### 3. Подключи Google Sheets

#### Шаг 1 — Создай проект в Google Cloud
1. Перейди на https://console.cloud.google.com
2. Создай новый проект (например `p2p-bot`)
3. Включи **Google Sheets API** и **Google Drive API**

#### Шаг 2 — Создай сервисный аккаунт
1. IAM и администрирование → Сервисные аккаунты → **Создать**
2. Название: `p2p-bot-sheets`
3. Роль: **Редактор**
4. Ключи → Добавить ключ → JSON → скачать
5. Переименуй файл в `credentials.json` и положи в папку бота

#### Шаг 3 — Дай доступ к таблице
1. Создай новую Google Таблицу
2. Скопируй её ID из URL:
   `https://docs.google.com/spreadsheets/d/`**`ВОТ_ЭТОТ_ID`**`/edit`
3. Нажми «Поделиться» → добавь email сервисного аккаунта
   (он есть в `credentials.json` в поле `client_email`)
4. Дай права **Редактора**

#### Шаг 4 — Вставь ID в `.env`
```env
GOOGLE_SHEET_ID=твой_id_таблицы
```

### 4. Запусти бота

```bash
python bot.py
```

---

## ✏️ Как изменить тарифы

Открой `config/tariffs.py` — всё в одном месте:

```python
TARIFFS: dict[str, Tariff] = {
    "standard": Tariff(
        id="standard",
        name="Стандарт",
        price=49,           # ← цена
        currency="$",
        emoji="🥉",
        features=[
            "Базовый курс (10 уроков)",   # ← список фич
            "Закрытый чат",
        ],
    ),
    # Добавь новый тариф так же 👇
    "vip": Tariff(
        id="vip",
        name="VIP",
        price=200,
        currency="$",
        emoji="💎",
        features=["Всё включено", "Личный куратор"],
        popular=False,
    ),
}
```

**Бот подхватит изменения автоматически** — перезапуск не нужен.

---

## 🔌 Подключение CRM (будущее)

Открой `services/crm.py` и реализуй метод `create_lead()` под свою CRM:

```python
# AmoCRM пример:
async with session.post(
    "https://your-domain.amocrm.ru/api/v4/leads",
    json=[{"name": data["name"], "price": data["tariff_price"]}],
    headers={"Authorization": f"Bearer {self.api_key}"},
)
```

Установи в `.env`:
```env
CRM_API_URL=https://your-domain.amocrm.ru/api/v4
CRM_API_KEY=твой_токен
```

---

## 💳 Подключение оплаты (будущее)

### Stripe
```python
# В handlers/survey.py после confirm:yes:
import stripe
stripe.api_key = settings.STRIPE_SECRET_KEY
session = stripe.checkout.Session.create(
    payment_method_types=["card"],
    line_items=[{"price_data": {...}, "quantity": 1}],
    mode="payment",
    success_url="https://t.me/your_bot?start=paid",
)
await bot.send_message(user_id, f"💳 Оплати здесь: {session.url}")
```

### CryptoPay (Telegram)
```python
# Используй aiocryptopay библиотеку
from aiocryptopay import AioCryptoPay
crypto = AioCryptoPay(token=CRYPTO_PAY_TOKEN)
invoice = await crypto.create_invoice(asset="USDT", amount=tariff.price)
await bot.send_message(user_id, f"₿ Оплата: {invoice.pay_url}")
```

---

## 🏭 Продакшен (деплой)

### Вариант 1 — systemd (Linux VPS)

```ini
# /etc/systemd/system/p2p-bot.service
[Unit]
Description=P2P Trading Bot
After=network.target

[Service]
WorkingDirectory=/home/user/p2p_bot
ExecStart=/home/user/p2p_bot/venv/bin/python bot.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```bash
systemctl enable p2p-bot
systemctl start p2p-bot
systemctl status p2p-bot
```

### Вариант 2 — Docker

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "bot.py"]
```

### Вариант 3 — Redis FSM Storage (для масштабирования)

Замени в `bot.py`:
```python
# Было:
storage = MemoryStorage()

# Стало:
from aiogram.fsm.storage.redis import RedisStorage
storage = RedisStorage.from_url("redis://localhost:6379")
```

---

## 📋 Переменные окружения

| Переменная | Обязательна | Описание |
|---|---|---|
| `BOT_TOKEN` | ✅ | Токен от @BotFather |
| `ADMIN_IDS` | ✅ | ID админов через запятую |
| `GOOGLE_CREDENTIALS_FILE` | ✅ | Путь к credentials.json |
| `GOOGLE_SHEET_ID` | ✅ | ID Google Таблицы |
| `GOOGLE_SHEET_NAME` | ➖ | Название листа (по умолч. «Заявки») |
| `TIMEZONE` | ➖ | Часовой пояс (по умолч. Europe/Moscow) |
| `CRM_API_URL` | ➖ | URL твоей CRM |
| `CRM_API_KEY` | ➖ | API-ключ CRM |
| `STRIPE_SECRET_KEY` | ➖ | Ключ Stripe (для оплаты) |
| `CRYPTO_PAY_TOKEN` | ➖ | Токен CryptoPay |
