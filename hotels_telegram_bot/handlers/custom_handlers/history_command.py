"""В этом модуле описывается работа с историей поиска пользователя после введения команды /history."""
from typing import List
from requests import ReadTimeout
from telebot.apihelper import ApiTelegramException
from telebot.types import Message, CallbackQuery
from keyboards.inline.delete_history_file_or_back_keyboard import create_delete_history_file_or_back_keyboard
from keyboards.inline.history_methods_keyboard import create_history_methods_keyboard
from keyboards.inline.history_pages_keyboard import create_history_pages_keyboard
from keyboards.inline.yes_no_keyboard import create_yes_no_keyboard
from loader import bot, crud
from states.history_states import HistoryStates
from utils.logger import logger
from peewee import OperationalError


@bot.callback_query_handler(func=None, state=HistoryStates.history_delete_confirmation)
def confirm_delete_history(callback_history_delete_confirmation: CallbackQuery) -> None:
    """
    Функция обрабатывает результат работы клавиатуры yes_no_keyboard,
    позволяет полностью очистить историю запросов или вернуться на шаг назад.

    :param callback_history_delete_confirmation: Входящий запрос обратного вызова с кнопки
    клавиатуры yes_no_keyboard
    :type callback_history_delete_confirmation: CallbackQuery
    """
    try:
        logger.info('user_id - {0}; callback.data - {1}'.
                    format(callback_history_delete_confirmation.from_user.id,
                           callback_history_delete_confirmation.data))

        logger.debug('user_id - {0}; вызов - функция confirm_delete_history({1})'.
                     format(callback_history_delete_confirmation.from_user.id,
                            callback_history_delete_confirmation.from_user.id))

        crud.delete_message_db(user_id_class=callback_history_delete_confirmation.from_user.id,
                               chat_id_class=callback_history_delete_confirmation.message.chat.id)

        if callback_history_delete_confirmation.data == 'yes':

            crud.delete_db(callback_history_delete_confirmation.from_user.id)

            msg_to_dlt_confirm_delete_history_1: Message = \
                bot.send_message(callback_history_delete_confirmation.message.chat.id,
                                 text='Ваша история пуста.\nНажмите меню для выбора дальнейших действий.')

            crud.update_message_db(user_id_class=msg_to_dlt_confirm_delete_history_1.from_user.id,
                                   chat_id_class=msg_to_dlt_confirm_delete_history_1.chat.id,
                                   message_id_class=msg_to_dlt_confirm_delete_history_1.message_id)

        elif callback_history_delete_confirmation.data == 'no':

            bot.set_state(callback_history_delete_confirmation.from_user.id,
                          HistoryStates.history_methods,
                          callback_history_delete_confirmation.message.chat.id)

            create_history_methods_keyboard(callback_history_delete_confirmation.from_user.id,
                                            callback_history_delete_confirmation.message.chat.id)

    except ApiTelegramException as exception:
        logger.exception(
            'user_id - {0}; тип ошибки - {1}'.format(callback_history_delete_confirmation.from_user.id, exception))

        msg_to_dlt_mistake_1: Message = \
            bot.send_message(callback_history_delete_confirmation.message.chat.id,
                             text='Ошибка связи с Телеграм.\nНажмите меню для выбора дальнейших действий.')

        crud.update_message_db(user_id_class=msg_to_dlt_mistake_1.from_user.id,
                               chat_id_class=msg_to_dlt_mistake_1.chat.id,
                               message_id_class=msg_to_dlt_mistake_1.message_id)

    except (ReadTimeout, TimeoutError) as exception:
        logger.exception(
            'user_id - {0}; тип ошибки - {1}'.format(callback_history_delete_confirmation.from_user.id, exception))

        msg_to_dlt_mistake_2: Message = \
            bot.send_message(callback_history_delete_confirmation.message.chat.id,
                             text='Ошибка. Время ожидания истекло.\nНажмите меню для выбора дальнейших действий.')

        crud.update_message_db(user_id_class=msg_to_dlt_mistake_2.from_user.id,
                               chat_id_class=msg_to_dlt_mistake_2.chat.id,
                               message_id_class=msg_to_dlt_mistake_2.message_id)

    except (OperationalError, ValueError, KeyError, NameError) as exception:
        logger.exception(
            'user_id - {0}; тип ошибки - {1}'.format(callback_history_delete_confirmation.from_user.id, exception))

        msg_to_dlt_mistake_3: Message = \
            bot.send_message(callback_history_delete_confirmation.message.chat.id,
                             text='Ошибка доступа к Вашей базе запросов.\nНажмите меню для выбора дальнейших действий.')

        crud.update_message_db(user_id_class=msg_to_dlt_mistake_3.from_user.id,
                               chat_id_class=msg_to_dlt_mistake_3.chat.id,
                               message_id_class=msg_to_dlt_mistake_3.message_id)


@bot.callback_query_handler(func=None, state=HistoryStates.history_file_methods)
def process_history_file_methods(callback_history_file_methods: CallbackQuery) -> None:
    """
    Функция обработывает результат работы клавиатуры delete_history_file_or_back_keyboard,
    полностью удаляет запись из истории поиска или позволяет вернуться к истории запросов.

    :param callback_history_file_methods: входящий запрос обратного вызова с кнопки
    клавиатуры delete_history_file_or_back_keyboard
    :type callback_history_file_methods: CallbackQuery
    """
    try:
        logger.info('user_id - {0}; callback.data - {1}'.
                    format(callback_history_file_methods.from_user.id,
                           callback_history_file_methods.data))

        logger.debug('user_id - {0}; вызов - функция process_history_file_methods({1})'.
                     format(callback_history_file_methods.from_user.id,
                            callback_history_file_methods.from_user.id))

        crud.delete_message_db(user_id_class=callback_history_file_methods.from_user.id,
                               chat_id_class=callback_history_file_methods.message.chat.id)

        if callback_history_file_methods.data.startswith('delete_file_db'):

            bot.set_state(callback_history_file_methods.from_user.id, HistoryStates.history_pages,
                          callback_history_file_methods.message.chat.id)

            crud.delete_file_db(callback_history_file_methods.from_user.id,
                                callback_history_file_methods.data[14:])

            user_history_update: List = crud.retrieve_db(
                user_id_class=callback_history_file_methods.from_user.id)

            create_history_pages_keyboard(callback_history_file_methods.from_user.id,
                                          callback_history_file_methods.message.chat.id,
                                          user_history_update)

        elif callback_history_file_methods.data.startswith('back'):

            bot.set_state(callback_history_file_methods.from_user.id, HistoryStates.history_pages,
                          callback_history_file_methods.message.chat.id)

            user_history_update_2: List = crud.retrieve_db(
                user_id_class=callback_history_file_methods.from_user.id)

            create_history_pages_keyboard(callback_history_file_methods.from_user.id,
                                          callback_history_file_methods.message.chat.id,
                                          user_history_update_2)

    except ApiTelegramException as exception:
        logger.exception(
            'user_id - {0}; тип ошибки - {1}'.format(callback_history_file_methods.from_user.id, exception))

        msg_to_dlt_mistake_1: Message = \
            bot.send_message(callback_history_file_methods.message.chat.id,
                             text='Ошибка связи с Телеграм.\nНажмите меню для выбора дальнейших действий.')

        crud.update_message_db(user_id_class=msg_to_dlt_mistake_1.from_user.id,
                               chat_id_class=msg_to_dlt_mistake_1.chat.id,
                               message_id_class=msg_to_dlt_mistake_1.message_id)

    except (ReadTimeout, TimeoutError) as exception:
        logger.exception(
            'user_id - {0}; тип ошибки - {1}'.format(callback_history_file_methods.from_user.id, exception))

        msg_to_dlt_mistake_2: Message = \
            bot.send_message(callback_history_file_methods.message.chat.id,
                             text='Ошибка. Время ожидания истекло.\nНажмите меню для выбора дальнейших действий.')

        crud.update_message_db(user_id_class=msg_to_dlt_mistake_2.from_user.id,
                               chat_id_class=msg_to_dlt_mistake_2.chat.id,
                               message_id_class=msg_to_dlt_mistake_2.message_id)

    except (OperationalError, ValueError, KeyError, NameError) as exception:
        logger.exception(
            'user_id - {0}; тип ошибки - {1}'.format(callback_history_file_methods.from_user.id, exception))

        msg_to_dlt_mistake_3: Message = \
            bot.send_message(callback_history_file_methods.message.chat.id,
                             text='Ошибка доступа к Вашей базе запросов.\nНажмите меню для выбора дальнейших действий.')

        crud.update_message_db(user_id_class=msg_to_dlt_mistake_3.from_user.id,
                               chat_id_class=msg_to_dlt_mistake_3.chat.id,
                               message_id_class=msg_to_dlt_mistake_3.message_id)


@bot.callback_query_handler(func=None, state=HistoryStates.history_pages)
def give_user_history(callback_history_pages_keyboard: CallbackQuery) -> None:
    """
    Функция обрабатывает результат работы клавиатуры history_pages_keyboard,
    предоставляет историю запросов пользователю или возможность вернуться к
    методам обработки истории запросов.

    :param callback_history_pages_keyboard: Входящий запрос обратного вызова
    с кнопки клавиатуры history_pages_keyboard
    :type callback_history_pages_keyboard: CallbackQuery
    """
    try:
        logger.info('user_id - {0}; callback.data - {1}'.
                    format(callback_history_pages_keyboard.from_user.id,
                           callback_history_pages_keyboard.data))

        logger.debug('user_id - {0}; вызов - функция give_user_history({1})'.
                     format(callback_history_pages_keyboard.from_user.id,
                            callback_history_pages_keyboard.from_user.id))

        crud.delete_message_db(user_id_class=callback_history_pages_keyboard.from_user.id,
                               chat_id_class=callback_history_pages_keyboard.message.chat.id)

        if callback_history_pages_keyboard.data == 'return':

            bot.set_state(callback_history_pages_keyboard.from_user.id, HistoryStates.history_methods,
                          callback_history_pages_keyboard.message.chat.id)

            create_history_methods_keyboard(callback_history_pages_keyboard.from_user.id,
                                            callback_history_pages_keyboard.message.chat.id)

        elif not callback_history_pages_keyboard.data.startswith('page'):

            bot.set_state(callback_history_pages_keyboard.from_user.id, HistoryStates.history_file_methods,
                          callback_history_pages_keyboard.message.chat.id)

            user_history_1: List = crud.retrieve_db(
                user_id_class=callback_history_pages_keyboard.from_user.id)

            hotel_id: int = [i_history[0] for i_history in user_history_1
                             if i_history[0] == int(callback_history_pages_keyboard.data)][0]

            hotel_city: str = [i_history[1] for i_history in user_history_1
                               if i_history[0] == int(callback_history_pages_keyboard.data)][0]

            hotel_name: str = [i_history[2] for i_history in user_history_1
                               if i_history[0] == int(callback_history_pages_keyboard.data)][0]

            hotel_address: str = [i_history[3] for i_history in user_history_1
                                  if i_history[0] == int(callback_history_pages_keyboard.data)][0]

            hotel_photo: str = [i_history[4] for i_history in user_history_1
                                if i_history[0] == int(callback_history_pages_keyboard.data)][0]

            create_delete_history_file_or_back_keyboard(callback_history_pages_keyboard.from_user.id,
                                                        callback_history_pages_keyboard.message.chat.id,
                                                        hotel_city, hotel_name,
                                                        hotel_address, hotel_photo, hotel_id)

        else:

            user_history_2: List = crud.retrieve_db(
                user_id_class=callback_history_pages_keyboard.from_user.id)

            for i_page in range(1, len(user_history_2) + 1):
                if str(i_page) == callback_history_pages_keyboard.data[4:]:
                    create_history_pages_keyboard(callback_history_pages_keyboard.from_user.id,
                                                  callback_history_pages_keyboard.message.chat.id,
                                                  user_history_2, page=i_page)

    except ApiTelegramException as exception:
        logger.exception(
            'user_id - {0}; тип ошибки - {1}'.format(callback_history_pages_keyboard.from_user.id, exception))

        msg_to_dlt_mistake_1: Message = \
            bot.send_message(callback_history_pages_keyboard.message.chat.id,
                             text='Ошибка связи с Телеграм.\nНажмите меню для выбора дальнейших действий.')

        crud.update_message_db(user_id_class=msg_to_dlt_mistake_1.from_user.id,
                               chat_id_class=msg_to_dlt_mistake_1.chat.id,
                               message_id_class=msg_to_dlt_mistake_1.message_id)

    except (ReadTimeout, TimeoutError) as exception:
        logger.exception(
            'user_id - {0}; тип ошибки - {1}'.format(callback_history_pages_keyboard.from_user.id, exception))

        msg_to_dlt_mistake_2: Message = \
            bot.send_message(callback_history_pages_keyboard.message.chat.id,
                             text='Ошибка. Время ожидания истекло.\nНажмите меню для выбора дальнейших действий.')

        crud.update_message_db(user_id_class=msg_to_dlt_mistake_2.from_user.id,
                               chat_id_class=msg_to_dlt_mistake_2.chat.id,
                               message_id_class=msg_to_dlt_mistake_2.message_id)

    except (OperationalError, ValueError, KeyError, NameError) as exception:
        logger.exception(
            'user_id - {0}; тип ошибки - {1}'.format(callback_history_pages_keyboard.from_user.id, exception))

        msg_to_dlt_mistake_3: Message = \
            bot.send_message(callback_history_pages_keyboard.message.chat.id,
                             text='Ошибка доступа к Вашей базе запросов.\nНажмите меню для выбора дальнейших действий.')

        crud.update_message_db(user_id_class=msg_to_dlt_mistake_3.from_user.id,
                               chat_id_class=msg_to_dlt_mistake_3.chat.id,
                               message_id_class=msg_to_dlt_mistake_3.message_id)


@bot.callback_query_handler(func=None, state=HistoryStates.history_methods)
def process_history_methods(callback_history_methods_keyboard: CallbackQuery) -> None:
    """
    Функция обрабатывает результат работы клавиатуры history_methods_keyboard,
    пользволяет пользователю посмотреть историю запросов, удалить историю запросов или выбрать одну из
    команд по умолчанию.

    :param callback_history_methods_keyboard: Входящий запрос обратного вызова с кнопки клавиатуры
    history_methods_keyboard
    :type callback_history_methods_keyboard: CallbackQuery
    """
    try:
        logger.info('user_id - {0}; callback.data - {1}'.
                    format(callback_history_methods_keyboard.from_user.id, callback_history_methods_keyboard.data))

        logger.debug('user_id - {0}; вызов - функция process_history_methods({1})'.
                     format(callback_history_methods_keyboard.from_user.id, callback_history_methods_keyboard))

        crud.delete_message_db(user_id_class=callback_history_methods_keyboard.from_user.id,
                               chat_id_class=callback_history_methods_keyboard.message.chat.id)

        if callback_history_methods_keyboard.data == 'show_history':

            bot.set_state(callback_history_methods_keyboard.from_user.id,
                          HistoryStates.history_pages, callback_history_methods_keyboard.message.chat.id)

            user_history: List = crud.retrieve_db(user_id_class=callback_history_methods_keyboard.from_user.id)

            create_history_pages_keyboard(callback_history_methods_keyboard.from_user.id,
                                          callback_history_methods_keyboard.message.chat.id, user_history)

        elif callback_history_methods_keyboard.data == 'delete_history':

            bot.set_state(callback_history_methods_keyboard.from_user.id,
                          HistoryStates.history_delete_confirmation,
                          callback_history_methods_keyboard.message.chat.id)

            msg_to_dlt_process_history_methods: Message = \
                bot.send_message(callback_history_methods_keyboard.message.chat.id,
                                 text='Восстановить историю запросов будет невозможно!'
                                      '\nВы действительно хотите удалить историю запросов?',
                                 reply_markup=create_yes_no_keyboard(
                                     user_id=callback_history_methods_keyboard.from_user.id,
                                     callback_data_yes='yes',
                                     callback_data_no='no'))

            crud.update_message_db(user_id_class=msg_to_dlt_process_history_methods.from_user.id,
                                   chat_id_class=msg_to_dlt_process_history_methods.chat.id,
                                   message_id_class=msg_to_dlt_process_history_methods.message_id)

    except ApiTelegramException as exception:
        logger.exception(
            'user_id - {0}; тип ошибки - {1}'.format(callback_history_methods_keyboard.from_user.id, exception))

        msg_to_dlt_mistake_1: Message = \
            bot.send_message(callback_history_methods_keyboard.message.chat.id,
                             text='Ошибка связи с Телеграм.\nНажмите меню для выбора дальнейших действий.')

        crud.update_message_db(user_id_class=msg_to_dlt_mistake_1.from_user.id,
                               chat_id_class=msg_to_dlt_mistake_1.chat.id,
                               message_id_class=msg_to_dlt_mistake_1.message_id)

    except (ReadTimeout, TimeoutError) as exception:
        logger.exception(
            'user_id - {0}; тип ошибки - {1}'.format(callback_history_methods_keyboard.from_user.id, exception))

        msg_to_dlt_mistake_2: Message = \
            bot.send_message(callback_history_methods_keyboard.message.chat.id,
                             text='Ошибка. Время ожидания истекло.\nНажмите меню для выбора дальнейших действий.')

        crud.update_message_db(user_id_class=msg_to_dlt_mistake_2.from_user.id,
                               chat_id_class=msg_to_dlt_mistake_2.chat.id,
                               message_id_class=msg_to_dlt_mistake_2.message_id)

    except (OperationalError, ValueError, KeyError, NameError) as exception:
        logger.exception(
            'user_id - {0}; тип ошибки - {1}'.format(callback_history_methods_keyboard.from_user.id, exception))

        msg_to_dlt_mistake_3: Message = \
            bot.send_message(callback_history_methods_keyboard.message.chat.id,
                             text='Ошибка доступа к Вашей базе запросов.\nНажмите меню для выбора дальнейших действий.')

        crud.update_message_db(user_id_class=msg_to_dlt_mistake_3.from_user.id,
                               chat_id_class=msg_to_dlt_mistake_3.chat.id,
                               message_id_class=msg_to_dlt_mistake_3.message_id)


@bot.message_handler(commands=['history'])
def start_history(start_message: Message) -> None:
    """
    Функция обрабатывает команду /history, анализирует историю запросов пользователя, если история пуста,
    то выводит соответствующее сообщение, если нет,
    то выводит клавиатуру history_methods_keyboard с возможными действиями с историей запросов.

    :param start_message: Сообщение от пользователя
    :type start_message: Message
    """
    try:
        logger.info('user_id - {}; команда - /history'.format(start_message.from_user.id))

        logger.debug('user_id - {0}; вызов - функция start_history({1})'.
                     format(start_message.from_user.id, start_message))

        crud.update_message_db(user_id_class=start_message.from_user.id,
                               chat_id_class=start_message.chat.id,
                               message_id_class=start_message.message_id)

        crud.delete_message_db(user_id_class=start_message.from_user.id,
                               chat_id_class=start_message.chat.id)

        crud.update_user_db(user_id_class=start_message.from_user.id)

        user_history_start: List = crud.retrieve_db(user_id_class=start_message.from_user.id)

        if len(user_history_start) == 0:
            logger.warning('user_id - {}; история запросов пуста'.format(start_message.from_user.id))

            msg_to_dlt_start_history: Message = bot.send_message(
                start_message.chat.id, text='Ваша история пуста.'
                                            '\nНажмите меню для выбора дальнейших действий.')

            crud.update_message_db(user_id_class=msg_to_dlt_start_history.from_user.id,
                                   chat_id_class=msg_to_dlt_start_history.chat.id,
                                   message_id_class=msg_to_dlt_start_history.message_id)
        else:
            bot.set_state(start_message.from_user.id, HistoryStates.history_methods, start_message.chat.id)

            create_history_methods_keyboard(start_message.from_user.id, start_message.chat.id)

    except ApiTelegramException as exception:
        logger.exception(
            'user_id - {0}; тип ошибки - {1}'.format(start_message.from_user.id, exception))

        msg_to_dlt_mistake_1: Message = \
            bot.send_message(start_message.chat.id,
                             text='Ошибка связи с Телеграм.\nНажмите меню для выбора дальнейших действий.')

        crud.update_message_db(user_id_class=msg_to_dlt_mistake_1.from_user.id,
                               chat_id_class=msg_to_dlt_mistake_1.chat.id,
                               message_id_class=msg_to_dlt_mistake_1.message_id)

    except (ReadTimeout, TimeoutError) as exception:
        logger.exception(
            'user_id - {0}; тип ошибки - {1}'.format(start_message.from_user.id, exception))

        msg_to_dlt_mistake_2: Message = \
            bot.send_message(start_message.chat.id,
                             text='Ошибка. Время ожидания истекло.\nНажмите меню для выбора дальнейших действий.')

        crud.update_message_db(user_id_class=msg_to_dlt_mistake_2.from_user.id,
                               chat_id_class=msg_to_dlt_mistake_2.chat.id,
                               message_id_class=msg_to_dlt_mistake_2.message_id)

    except (OperationalError, ValueError, KeyError, NameError) as exception:
        logger.exception(
            'user_id - {0}; тип ошибки - {1}'.format(start_message.from_user.id, exception))

        msg_to_dlt_mistake_3: Message = \
            bot.send_message(start_message.chat.id,
                             text='Ошибка доступа к Вашей базе запросов.\nНажмите меню для выбора дальнейших действий.')

        crud.update_message_db(user_id_class=msg_to_dlt_mistake_3.from_user.id,
                               chat_id_class=msg_to_dlt_mistake_3.chat.id,
                               message_id_class=msg_to_dlt_mistake_3.message_id)
