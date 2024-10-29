"""В этом модуле описаны функции создания календаря и обработки даты введеной пользователем."""
from telebot.types import CallbackQuery, Message

from telegram_bot_calendar import DetailedTelegramCalendar

from keyboards.inline.yes_no_keyboard import create_yes_no_keyboard

from loader import bot, crud

from utils.logger import logger

LSTEP_RU = {'y': 'год', 'm': 'месяц', 'd': 'день'}


def run_calendar(user_id: int, chat_id: int) -> None:
    """
    Функция создает календарь.

    :param user_id: Id пользователя
    :param chat_id: Id чата
    :type user_id: int
    :type chat_id: int
    """
    logger.debug('user_id - {0}; вызов - функция run_calendar({1})'.
                 format(user_id, user_id))

    calendar, step = DetailedTelegramCalendar().build()

    msg_to_dlt_run_calendar_1: Message = bot.send_message(chat_id, text='Выберите {}'.format(LSTEP_RU[step]),
                                                          reply_markup=calendar)

    crud.update_message_db(user_id_class=msg_to_dlt_run_calendar_1.from_user.id,
                           chat_id_class=msg_to_dlt_run_calendar_1.chat.id,
                           message_id_class=msg_to_dlt_run_calendar_1.message_id)


@bot.callback_query_handler(func=DetailedTelegramCalendar.func())
def get_callback(callback: CallbackQuery) -> None:
    """
    Функция обработки даты.

    :param callback: Входящий запрос обратного вызова с кнопки клавиатуры календаря
    :type callback: CallbackQuery
    """
    result, key, step = DetailedTelegramCalendar(locale='ru').process(callback.data)

    if not result and key:
        crud.delete_message_db(user_id_class=callback.from_user.id,
                               chat_id_class=callback.message.chat.id)

        msg_to_dlt_run_calendar_2: Message = bot.send_message(callback.message.chat.id,
                                                              text='Выберите {}'.format(LSTEP_RU[step]),
                                                              reply_markup=key)

        crud.update_message_db(user_id_class=msg_to_dlt_run_calendar_2.from_user.id,
                               chat_id_class=msg_to_dlt_run_calendar_2.chat.id,
                               message_id_class=msg_to_dlt_run_calendar_2.message_id)
    else:
        crud.delete_message_db(user_id_class=callback.from_user.id,
                               chat_id_class=callback.message.chat.id)

        msg_to_dlt_run_calendar_3: Message = \
            bot.send_message(callback.message.chat.id, text='Это верная дата - {}?'.format(result),
                             reply_markup=create_yes_no_keyboard(user_id=None, callback_data_yes=str(result),
                                                                 callback_data_no='no'))

        crud.update_message_db(user_id_class=msg_to_dlt_run_calendar_3.from_user.id,
                               chat_id_class=msg_to_dlt_run_calendar_3.chat.id,
                               message_id_class=msg_to_dlt_run_calendar_3.message_id)
