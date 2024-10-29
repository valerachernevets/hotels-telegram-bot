"""В этом модуле описана функция создания клавиатуры yes_no_keyboard."""
from typing import Any

from telebot import types

from telebot.types import InlineKeyboardMarkup

from utils.logger import logger


def create_yes_no_keyboard(user_id: int | None, callback_data_yes: Any = 'yes',
                           callback_data_no: Any = 'no') -> InlineKeyboardMarkup:
    """
    Функция создания клавиатуры yes_no_keyboard, отправляет пользователю клавиатуру с кнопками
    "Да" и "Нет" для подтверждения выбора.

    :param user_id: Id пользователя
    :param callback_data_yes: Значение, которое возвращает кнопка "Да"
    :param callback_data_no: значение, которое возвращает кнопка "Нет"
    :type user_id: int | None
    :type callback_data_yes: Any
    :type callback_data_no: Any
    :return: клавиатуру yes_no_keyboard
    :rtype: types. InlineKeyboardMarkup
    """
    logger.debug('user_id - {0};'
                 ' вызов - функция create_yes_no_keyboard(callback_data_yes={1},'
                 ' callback_data_no={2})'.
                 format(user_id, callback_data_yes, callback_data_no))

    yes_no_keyboard = types.InlineKeyboardMarkup()

    yes_no_keyboard.add(types.InlineKeyboardButton(text='да',
                                                   callback_data=callback_data_yes))

    yes_no_keyboard.add(types.InlineKeyboardButton(text='нет',
                                                   callback_data=callback_data_no))

    return yes_no_keyboard
