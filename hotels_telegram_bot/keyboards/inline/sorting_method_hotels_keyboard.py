"""В этом модуле описана функция создания клавиатуры sorting_method_hotels_keyboard."""
from telebot import types
from telebot.types import Message

from loader import bot, crud

from utils.logger import logger


def create_sorting_method_hotels_keyboard(user_id: int, chat_id: int) -> None:
    """
    Функция создания клавиатуры sorting_method_hotels_keyboard, которая отправляет пользователю методы
    сортировки отелей по цене или по расстоянию отеля от центра города.

    :param user_id: Id пользователя
    :param chat_id: id чата
    :type user_id: int
    :type chat_id: int
    """
    logger.debug('user_id - {0};'
                 ' вызов - функция create_sorting_method_hotels_keyboard({1}, {2})'.
                 format(user_id, user_id, chat_id))

    sorting_method_hotels_keyboard = types.InlineKeyboardMarkup()

    sorting_method_hotels_keyboard.add(types.InlineKeyboardButton(text='Сначала самые дешевые отели:',
                                                                  callback_data='low_price'))

    sorting_method_hotels_keyboard.add(types.InlineKeyboardButton(text='Сначала самые дорогие отели:',
                                                                  callback_data='high_price'))

    sorting_method_hotels_keyboard.add(types.InlineKeyboardButton(text='Сначала самые близкие отели:',
                                                                  callback_data='nearby_hotels'))

    sorting_method_hotels_keyboard.add(types.InlineKeyboardButton(text='Сначала самые дальние отели:',
                                                                  callback_data='distant_hotels'))

    msg_to_dlt_create_sorting_method_hotels_keyboard: Message =\
        bot.send_message(chat_id,
                         text='Выберите способ сортировки отелей:',
                         reply_markup=sorting_method_hotels_keyboard)

    crud.update_message_db(user_id_class=msg_to_dlt_create_sorting_method_hotels_keyboard.from_user.id,
                           chat_id_class=msg_to_dlt_create_sorting_method_hotels_keyboard.chat.id,
                           message_id_class=msg_to_dlt_create_sorting_method_hotels_keyboard.message_id)
