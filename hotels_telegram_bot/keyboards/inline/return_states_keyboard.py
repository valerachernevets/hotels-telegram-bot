"""В этом модуле описана функция создания клавиатуры return_states_keyboard."""
from telebot import types
from telebot.types import Message

from loader import bot, crud

from utils.logger import logger


def create_return_states_keyboard(user_id: int, chat_id: int,  children=0) -> None:
    """
    Функция создания клавиатуры return_states_keyboard.

    Функция отправляет пользователю клавиатуру с параметрами, которые он хочет изменить.

    :param user_id: Id пользователя
    :param chat_id: id чата
    :param children: количество детей
    :type user_id: int
    :type chat_id: int
    :type children: int
    """
    logger.debug('user_id - {0}; вызов - функция create_return_states_keyboard({1}, {2}, {3})'.
                 format(user_id, user_id, chat_id, children))

    return_states_keyboard = types.InlineKeyboardMarkup()

    return_states_keyboard.add(types.InlineKeyboardButton(text='Ввести новый город',
                                                          callback_data='city'))

    return_states_keyboard.add(types.InlineKeyboardButton(text='Ввести новую дату приезда',
                                                          callback_data='arrival_date'))

    return_states_keyboard.add(types.InlineKeyboardButton(text='Ввести новую дату отъезда',
                                                          callback_data='date_of_departure'))

    return_states_keyboard.add(types.InlineKeyboardButton(text='Ввести новую минимальную цену проживания',
                                                          callback_data='min_price'))

    return_states_keyboard.add(types.InlineKeyboardButton(text='Ввести новую максимальную цену проживания',
                                                          callback_data='max_price'))

    return_states_keyboard.add(types.InlineKeyboardButton(text='Ввести новое количество взрослых',
                                                          callback_data='adults_quantity'))

    return_states_keyboard.add(types.InlineKeyboardButton(text='Ввести новое количество детей',
                                                          callback_data='children_quantity'))

    for i_child in range(1, int(children) + 1):
        return_states_keyboard.add(
            types.InlineKeyboardButton(text='Ввести новый возраст {}-го ребенка'.format(i_child),
                                       callback_data='children_ages_{}'.format(i_child)))

    return_states_keyboard.add(types.InlineKeyboardButton(text='Ввести новое максимальное расстояние',
                                                          callback_data='max_distance_from_center'))

    msg_to_dlt_create_return_states_keyboard: Message =\
        bot.send_message(chat_id,
                         text='Выберите этап к которому Вы хотите вернуться:',
                         reply_markup=return_states_keyboard)

    crud.update_message_db(user_id_class=msg_to_dlt_create_return_states_keyboard.from_user.id,
                           chat_id_class=msg_to_dlt_create_return_states_keyboard.chat.id,
                           message_id_class=msg_to_dlt_create_return_states_keyboard.message_id)
