"""В этом модуле описана функция создания клавиатуры hotels_keyboard."""
from typing import List

from telebot import types

from telebot.types import Message

from loader import bot, crud

from utils.logger import logger


def create_hotels_keyboard(user_id: int, chat_id: int, hotels: List, page=1) -> None:
    """
    Функция создания клавиатуры hotels_keyboard, которая отправляет пользователю первые 10 отелей, удовлетворяющих
    критериям пользователя и страницы с отелями, по 10 отелей на странице и возможность изменить метод сортировки.

    :param user_id: Id пользователя
    :param chat_id: id чата
    :param hotels: отели, удовлетворяющие критериям поиска
    :param page: номер страницы с отелями
    :type user_id: int
    :type chat_id: int
    :type hotels: List
    :type page: int
    """
    logger.debug('user_id - {0}; вызов - функция create_hotels_keyboard(user_id={1}, chat_id={2},'
                 ' hotels={3}, page={4})'.format(user_id, user_id, chat_id, hotels, page))

    hotels_keyboard = types.InlineKeyboardMarkup()

    full_pages = len(hotels) // 10

    rest_hostels = len(hotels) % 10

    if rest_hostels == 0:
        pages = full_pages

    else:
        pages = full_pages + 1

    for i_button in range(1, pages + 1):
        if i_button == page:
            for i_hotel in hotels[(0 + page - 1) * 10: (((0 + page - 1) * 10) + 10)]:
                hotels_keyboard.add(types.InlineKeyboardButton(text='{0}...\n{1}USD; {2}km'.
                                                               format(i_hotel[1][:17], int(i_hotel[2]), i_hotel[3]),
                                                               callback_data=i_hotel[0]))
        else:
            last_number_1 = len(hotels)

            last_number_2 = ((0 + i_button - 1) * 10) + 10

            correct_last_number = last_number_1 if last_number_1 < last_number_2 else last_number_2

            hotels_keyboard.add(types.InlineKeyboardButton(text='{0}-я страница\n{1} - {2}'.
                                                           format(i_button, ((0 + i_button - 1) * 10) + 1,
                                                                  correct_last_number),
                                                           callback_data='page{}'.format(i_button)))

    hotels_keyboard.add(types.InlineKeyboardButton(text='Изменить метод сортировки',
                                                   callback_data='change_sorting_method'))

    msg_to_dlt_create_hotels_keyboard: Message = \
        bot.send_message(chat_id,
                         text='Вот список доступных отелей\n'
                              'Для просмотра дополнительной информации, нажмите кнопку:',
                         reply_markup=hotels_keyboard)

    crud.update_message_db(user_id_class=msg_to_dlt_create_hotels_keyboard.from_user.id,
                           chat_id_class=msg_to_dlt_create_hotels_keyboard.chat.id,
                           message_id_class=msg_to_dlt_create_hotels_keyboard.message_id)
