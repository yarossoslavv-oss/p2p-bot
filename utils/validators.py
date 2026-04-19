import re


def validate_name(text: str) -> tuple[bool, str]:
    """
    Проверяет имя пользователя.
    Возвращает (is_valid, error_message).
    """
    text = text.strip()
    if len(text) < 2:
        return False, "❌ Имя слишком короткое. Введи хотя бы 2 символа."
    if len(text) > 64:
        return False, "❌ Имя слишком длинное. Максимум 64 символа."
    if re.search(r"[0-9@#$%^&*()_+=\[\]{};:\"\\|<>/?]", text):
        return False, "❌ Имя не должно содержать цифры или спецсимволы."
    return True, ""


def validate_username(text: str) -> tuple[bool, str]:
    """
    Проверяет Telegram username.
    Возвращает (is_valid, cleaned_username).
    """
    text = text.strip().lstrip("@")
    if len(text) < 5:
        return False, "❌ Username слишком короткий (минимум 5 символов)."
    if len(text) > 32:
        return False, "❌ Username слишком длинный (максимум 32 символа)."
    if not re.match(r"^[a-zA-Z0-9_]+$", text):
        return False, "❌ Username может содержать только латинские буквы, цифры и _."
    return True, f"@{text}"


def sanitize_text(text: str) -> str:
    """Очищает текст от HTML-тегов для безопасного вывода."""
    return text.replace("<", "&lt;").replace(">", "&gt;").replace("&", "&amp;")

