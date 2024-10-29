"""В этом модуле описана функция создания клавиатуры delete_history_file_or_back_keyboard."""
from telebot import types

from telebot.types import Message

from loader import bot, crud

from utils.logger import logger


def create_delete_history_file_or_back_keyboard(user_id: int, chat_id: int, hotel_city: str, hotel_name: str,
                                                hotel_address: str,
                                                hotel_photo: str, hotel_id: int) -> None:
    """
    Функция создания клавиатуры delete_history_file_or_back_keyboard, которая предлагает пользователю удалить
    запрос из базы данных или вернуться на шаг назад.

    :param user_id: Id пользователя
    :param chat_id: id чата
    :param hotel_city: город в котором расположен отель
    :param hotel_name: название отеля
    :param hotel_address: адрес отеля
    :param hotel_photo: ссылка на фото отеля
    :param hotel_id: id отеля
    :type user_id: int
    :type chat_id: int
    :type hotel_city: str
    :type hotel_name: str
    :type hotel_address: str
    :type hotel_photo: str
    :type hotel_id: int
    """
    logger.debug('user_id - {0}; вызов - функция create_delete_history_file_or_back_keyboard({1},'
                 ' {2}, {3}, {4}, {5}, {6}, {7})'.
                 format(user_id, user_id, chat_id, hotel_city, hotel_name,
                        hotel_address, hotel_photo, hotel_id))

    delete_history_file_or_back_keyboard = types.InlineKeyboardMarkup()

    delete_history_file_or_back_keyboard.add(types.InlineKeyboardButton(
        text='Удалить запись', callback_data='delete_file_db{}'.format(hotel_id)))

    delete_history_file_or_back_keyboard.add(types.InlineKeyboardButton(
        text='Вернуться назад', callback_data='back'))

    msg_to_dlt_create_delete_history_file_or_back_keyboard: Message = \
        bot.send_message(chat_id, text='Город:\n{0}\nНазвание:\n{1}\nАдрес:\n{2}\nФото:\n{3}'.
                         format(hotel_city, hotel_name,
                                hotel_address,
                                hotel_photo),
                         reply_markup=delete_history_file_or_back_keyboard)

    crud.update_message_db(user_id_class=msg_to_dlt_create_delete_history_file_or_back_keyboard.from_user.id,
                           chat_id_class=msg_to_dlt_create_delete_history_file_or_back_keyboard.chat.id,
                           message_id_class=msg_to_dlt_create_delete_history_file_or_back_keyboard.message_id)
