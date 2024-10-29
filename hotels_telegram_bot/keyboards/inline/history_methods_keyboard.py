"""В этом модуле описана функция создания клавиатуры history_methods_keyboard."""
from telebot import types

from telebot.types import Message

from loader import bot, crud

from utils.logger import logger


def create_history_methods_keyboard(user_id: int, chat_id: int) -> None:
    """
    Функция создания клавиатуры history_methods_keyboard, которая предлагает пользователю методы
    взаимодействия со своей историей запросов: показать историю поиска, очистить историю поиска
    или список команд по умолчанию.

    :param user_id: Id пользователя
    :param chat_id: id чата
    :type user_id: int
    :type chat_id: int
    """
    logger.debug('user_id - {0}; вызов - функция create_history_methods_keyboard({1}, {2})'.
                 format(user_id, user_id, chat_id))

    history_keyboard = types.InlineKeyboardMarkup()

    history_keyboard.add(types.InlineKeyboardButton(text='Показать историю поиска',
                                                    callback_data='show_history'))

    history_keyboard.add(types.InlineKeyboardButton(text='Очистить историю поиска',
                                                    callback_data='delete_history'))

    msg_to_dlt_create_history_methods_keyboard: Message = bot.send_message(chat_id, text='Сделайте выбор',
                                                                           reply_markup=history_keyboard)

    crud.update_message_db(user_id_class=msg_to_dlt_create_history_methods_keyboard.from_user.id,
                           chat_id_class=msg_to_dlt_create_history_methods_keyboard.chat.id,
                           message_id_class=msg_to_dlt_create_history_methods_keyboard.message_id)
