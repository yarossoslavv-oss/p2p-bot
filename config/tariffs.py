"""
╔══════════════════════════════════════════════════════════╗
║           КОНФИГ ТАРИФОВ — РЕДАКТИРУЙ ЗДЕСЬ             ║
║  Добавь/удали тарифы — бот подхватит изменения сам      ║
╚══════════════════════════════════════════════════════════╝
"""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Tariff:
    id: str                   # технический идентификатор
    name: str                 # название для отображения
    price: int                # цена в USD
    currency: str             # валюта
    emoji: str                # эмодзи для UI
    features: list[str]       # список фич
    popular: bool = False     # пометка "популярный"

    @property
    def price_label(self) -> str:
        return f"{self.price}{self.currency}"

    @property
    def full_description(self) -> str:
        features_text = "\n".join(f"  ✅ {f}" for f in self.features)
        popular_badge = " 🔥 <b>Популярный</b>" if self.popular else ""
        return (
            f"{self.emoji} <b>{self.name}</b> — <b>{self.price_label}</b>{popular_badge}\n"
            f"{features_text}"
        )

    @property
    def short_label(self) -> str:
        return f"{self.emoji} {self.name} — {self.price_label}"


# ──────────────────────────────────────────────────────────
#  СПИСОК ТАРИФОВ — добавляй/убирай/редактируй свободно
# ──────────────────────────────────────────────────────────
TARIFFS: dict[str, Tariff] = {
    "standard": Tariff(
        id="standard",
        name="Стандарт",
        price=49,
        currency="$",
        emoji="🥉",
        features=[
            "Базовый курс P2P-трейдинга (10 уроков)",
            "Закрытый Telegram-чат",
            "PDF-инструкции по биржам",
            "Поддержка в течение 30 дней",
        ],
    ),
    "advanced": Tariff(
        id="advanced",
        name="Продвинутый",
        price=75,
        currency="$",
        emoji="🥈",
        popular=True,
        features=[
            "Всё из тарифа Стандарт",
            "Расширенный курс (20 уроков)",
            "Разбор сделок в прямом эфире",
            "Персональный план входа в P2P",
            "Поддержка 60 дней",
        ],
    ),
    "pro": Tariff(
        id="pro",
        name="PRO",
        price=100,
        currency="$",
        emoji="🥇",
        features=[
            "Всё из тарифа Продвинутый",
            "Менторство 1-на-1 (2 сессии)",
            "Готовые стратегии + таблицы расчётов",
            "Приоритетная поддержка 90 дней",
            "Доступ к закрытому P2P-сообществу",
        ],
    ),
}

# ──────────────────────────────────────────────────────────
#  ОПЦИИ КАПИТАЛА — редактируй свободно
# ──────────────────────────────────────────────────────────
CAPITAL_OPTIONS: list[str] = [
    "До $500",
    "$500 – $2 000",
    "$2 000 – $10 000",
    "Свыше $10 000",
]

