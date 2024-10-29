"""В этом модуле описана функция создания клавиатуры history_pages_keyboard."""
from typing import List

from telebot import types

from telebot.types import Message

from loader import bot, crud

from utils.logger import logger


def create_history_pages_keyboard(user_id: int, chat_id: int, user_history: List[List], page=1) -> None:
    """
    Функция создания клавиатуры history_pages_keyboard, которая отправляет пользователю клавиатуру
    с его последними пятью запросами и страницами с остальными запросами, по пять запросов на одной странице.

    :param user_id: Id пользователя
    :param chat_id: id чата
    :param user_history: история запросов
    :param page: номер страницы
    :type user_id: int
    :type chat_id: int
    :type user_history: List[List]
    :type page: int
    """
    logger.debug('user_id - {0}; вызов - функция create_history_pages_keyboard({1}, {2}, {3}, {4})'.
                 format(user_id, user_id, chat_id, user_history, page))

    if len(user_history) == 0:
        mgl_to_dlt_create_history_pages_keyboard_1: Message = \
            bot.send_message(chat_id, text='Ваша история пуста.\nНажмите меню для выбора дальнейших действий.')

        crud.update_message_db(user_id_class=mgl_to_dlt_create_history_pages_keyboard_1.from_user.id,
                               chat_id_class=mgl_to_dlt_create_history_pages_keyboard_1.chat.id,
                               message_id_class=mgl_to_dlt_create_history_pages_keyboard_1.message_id)
    else:
        history_pages_keyboard = types.InlineKeyboardMarkup()

        full_pages = len(user_history) // 5

        rest_history = len(user_history) % 5

        if rest_history == 0:
            pages = full_pages

        else:
            pages = full_pages + 1

        for i_button in range(1, pages + 1):
            if i_button == page:
                for i_history in user_history[(0 + page - 1) * 5: (((0 + page - 1) * 5) + 5)]:
                    history_pages_keyboard.add(types.InlineKeyboardButton(
                        text='{}\n{}'.format(i_history[1], i_history[2]),
                        callback_data=i_history[0]))

            else:
                last_number_1 = len(user_history)

                last_number_2 = ((0 + i_button - 1) * 5) + 5

                correct_last_number = last_number_1 if last_number_1 < last_number_2 else last_number_2

                history_pages_keyboard.add(types.InlineKeyboardButton(text='{0}-я страница\n{1} - {2}'.
                                                                      format(i_button, ((0 + i_button - 1) * 5) + 1,
                                                                             correct_last_number),
                                                                      callback_data='page{}'.format(i_button)))

        history_pages_keyboard.add(types.InlineKeyboardButton(text='Вернуться назад',
                                                              callback_data='return'))

        mgl_to_dlt_create_history_pages_keyboard_2: Message =\
            bot.send_message(chat_id, text='Вот список Ваших запросов.'
                                           '\nДля просмотра дополнительной информации, нажмите кнопку:',
                                           reply_markup=history_pages_keyboard)

        crud.update_message_db(user_id_class=mgl_to_dlt_create_history_pages_keyboard_2.from_user.id,
                               chat_id_class=mgl_to_dlt_create_history_pages_keyboard_2.chat.id,
                               message_id_class=mgl_to_dlt_create_history_pages_keyboard_2.message_id)
