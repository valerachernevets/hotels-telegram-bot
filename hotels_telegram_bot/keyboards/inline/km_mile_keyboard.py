"""В этом модуле описана функция создания клавиатуры km_mile_keyboard."""
from telebot import types

from telebot.types import Message

from loader import bot, crud

from utils.logger import logger


def create_km_mile_keyboard(user_id: int, chat_id: int) -> None:
    """
    Функция создания клавиатуры history_pages_keyboard, которая отправляет пользователю клавиатуру с
    возможностью выбора единицы измерения расстояния: километры или мили.

    :param user_id: Id пользователя
    :param chat_id: id чата
    :type user_id: int    :type chat_id: int
    """
    logger.debug('user_id - {0}; вызов - функция create_km_mile_keyboard({1}'.
                 format(user_id,
                        chat_id))

    km_mile_keyboard = types.InlineKeyboardMarkup()

    km_mile_keyboard.add(types.InlineKeyboardButton(text='километры',
                                                    callback_data='km'))

    km_mile_keyboard.add(types.InlineKeyboardButton(text='мили',
                                                    callback_data='mile'))

    msg_to_dlt_create_km_mile_keyboard: Message =\
        bot.send_message(chat_id,
                         text='В чем будем измерять расстояние от центра города:',
                         reply_markup=km_mile_keyboard)

    crud.update_message_db(user_id_class=msg_to_dlt_create_km_mile_keyboard.from_user.id,
                           chat_id_class=msg_to_dlt_create_km_mile_keyboard.chat.id,
                           message_id_class=msg_to_dlt_create_km_mile_keyboard.message_id)
