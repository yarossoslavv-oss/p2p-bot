from aiogram.fsm.state import State, StatesGroup


class SurveyStates(StatesGroup):
    """Состояния опроса пользователя."""
    choosing_tariff = State()   # выбор тарифа
    entering_name = State()     # ввод имени
    choosing_experience = State()  # опыт в P2P
    choosing_capital = State()  # размер капитала
    entering_username = State()  # ввод username вручную (если скрыт)
    confirming = State()        # подтверждение данных
