"""В этом модуле описана функция создания клавиатуры eponymous_cities_keyboard."""
from typing import Dict

from telebot import types
from telebot.types import Message

from loader import bot, crud

from utils.logger import logger


def create_eponymous_cities_keyboard(user_id: int, chat_id: int, cities: Dict) -> None:
    """
    Функция создания клавиатуры eponymous_cities_keyboard.

    Функция предлагает пользователю уточнить город, в котором он ищет отель.

    :param user_id: Id пользователя
    :param chat_id: id чата
    :param cities: список одноименных и похожих по названию городов
    :type user_id: int
    :param chat_id: int
    :type cities: Dict
    """
    logger.debug('user_id - {0}; вызов - функция create_eponymous_cities_keyboard('
                 '{1}, {2})'.format(user_id, user_id, cities))

    eponymous_cities_keyboard = types.InlineKeyboardMarkup()

    for key in cities:

        eponymous_cities_keyboard.add(types.InlineKeyboardButton(text=cities[key],
                                                                 callback_data='{0}{1}'.format(key, cities[key])))

    msg_to_dlt_create_eponymous_cities_keyboard: Message =\
        bot.send_message(chat_id,
                         text='Уточните Ваш запрос, нажав нужную кнопку:',
                         reply_markup=eponymous_cities_keyboard)

    crud.update_message_db(user_id_class=msg_to_dlt_create_eponymous_cities_keyboard.from_user.id,
                           chat_id_class=msg_to_dlt_create_eponymous_cities_keyboard.chat.id,
                           message_id_class=msg_to_dlt_create_eponymous_cities_keyboard.message_id)
