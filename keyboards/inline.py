from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config.tariffs import TARIFFS, CAPITAL_OPTIONS


def kb_start() -> InlineKeyboardMarkup:
    """Стартовая клавиатура."""
    builder = InlineKeyboardBuilder()
    builder.button(text="🚀 Выбрать тариф", callback_data="show_tariffs")
    return builder.as_markup()


def kb_tariffs() -> InlineKeyboardMarkup:
    """Клавиатура выбора тарифа — генерируется из конфига."""
    builder = InlineKeyboardBuilder()
    for tariff in TARIFFS.values():
        label = tariff.short_label
        if tariff.popular:
            label += " 🔥"
        builder.button(text=label, callback_data=f"tariff:{tariff.id}")
    builder.button(text="◀️ Назад", callback_data="back_to_start")
    builder.adjust(1)
    return builder.as_markup()


def kb_experience() -> InlineKeyboardMarkup:
    """Клавиатура выбора опыта."""
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Да, есть опыт", callback_data="exp:yes")
    builder.button(text="❌ Нет, новичок", callback_data="exp:no")
    builder.button(text="◀️ Назад", callback_data="back_to_tariffs")
    builder.adjust(2, 1)
    return builder.as_markup()


def kb_capital() -> InlineKeyboardMarkup:
    """Клавиатура выбора капитала — генерируется из конфига."""
    builder = InlineKeyboardBuilder()
    for option in CAPITAL_OPTIONS:
        builder.button(text=option, callback_data=f"capital:{option}")
    builder.button(text="◀️ Назад", callback_data="back_to_experience")
    builder.adjust(2, 2, 1)
    return builder.as_markup()


def kb_confirm() -> InlineKeyboardMarkup:
    """Клавиатура подтверждения заявки."""
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Подтвердить заявку", callback_data="confirm:yes")
    builder.button(text="✏️ Изменить данные", callback_data="confirm:edit")
    builder.adjust(1)
    return builder.as_markup()


def kb_back_to_start() -> InlineKeyboardMarkup:
    """Простая кнопка «начать заново»."""
    builder = InlineKeyboardBuilder()
    builder.button(text="🔄 Начать заново", callback_data="back_to_start")
    return builder.as_markup()

