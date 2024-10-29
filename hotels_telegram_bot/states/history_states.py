"""В этом модуле описывается класс состояний HistoryStates(StatesGroup)."""
from telebot.handler_backends import StatesGroup, State


class HistoryStates(StatesGroup):
    """
    Класс - HistoryStates. Родительский класс - StatesGroup.

    Описывает состояния для корректной работы с историей запросов.

    Attributes:
        history_methods (State): состояние выбора метода работы с историей запроса
        history_pages (State): состояние работы со страницами истории запросов
        history_delete_confirmation (State): состояние подтверждения полного удаления истории
        history_file_methods (State): состояние выбора метода работы с одним запросом пользователя
    """

    history_methods = State()
    history_pages = State()
    history_delete_confirmation = State()
    history_file_methods = State()
