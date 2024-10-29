"""
В этом модуле описывается поиск отелей по предоставленным пользователем данным после
введения команды /search.
"""
from typing import Dict, List

from peewee import OperationalError

from requests import ReadTimeout

from telebot.apihelper import ApiTelegramException

from telebot.types import Message, CallbackQuery

from keyboards.inline.hotels_keyboard import create_hotels_keyboard

from keyboards.inline.return_states_keyboard import create_return_states_keyboard

from keyboards.inline.sorting_method_hotels_keyboard import create_sorting_method_hotels_keyboard

from keyboards.inline.yes_no_keyboard import create_yes_no_keyboard

from loader import bot, crud

from states.search_states import SearchStates

from utils.logger import logger

from utils.misc.calendar_loader import run_calendar

from utils.misc.find_eponymous_cities import find_eponymous_cities

from keyboards.inline.eponymous_cities_keyboard import create_eponymous_cities_keyboard

import datetime

from keyboards.inline.km_mile_keyboard import create_km_mile_keyboard

from utils.misc.find_hotel_details import find_hotel_details

from utils.misc.find_hotels import find_hotels


@bot.callback_query_handler(func=None, state=SearchStates.hotel_details)
def get_hotel_details(callback: CallbackQuery) -> None:
    """
    Функция обрабатывает результат работы клавиатуры hotels_keyboard,
    позволяет изменить метод сортировки отелей,
    записывает в базу данных запрос пользователя, выдает пользователю город, название отеля, адрес отеля,
    фото отеля.

    :param callback: Входящий запрос обратного вызова с кнопки клавиатуры sorting_method_hotels_keyboard
    :type callback: CallbackQuery
    """
    try:

        logger.info('user_id - {0}; callback.data - {1}'.format(callback.from_user.id, callback.data))

        logger.debug('user_id - {0}; вызов - функция get_hotel_details({1})'.
                     format(callback.from_user.id, callback))

        crud.delete_message_db(user_id_class=callback.from_user.id,
                               chat_id_class=callback.message.chat.id)

        with bot.retrieve_data(callback.from_user.id, callback.message.chat.id) as data:

            if callback.data == 'change_sorting_method':

                bot.set_state(callback.from_user.id, SearchStates.sorting_method_hotels,
                              callback.message.chat.id)

                msg_to_dlt_get_hotel_details_1: Message = bot.send_message(
                    callback.message.chat.id,
                    text=''.join(
                        i_element for i_element in data['main_text'].values()))

                crud.update_message_db(user_id_class=msg_to_dlt_get_hotel_details_1.from_user.id,
                                       chat_id_class=msg_to_dlt_get_hotel_details_1.chat.id,
                                       message_id_class=msg_to_dlt_get_hotel_details_1.message_id)

                create_sorting_method_hotels_keyboard(callback.from_user.id, callback.message.chat.id)

            elif not callback.data.startswith('page'):

                msg_to_dlt_get_hotel_details_2: Message = bot.send_message(
                    callback.message.chat.id,
                    text=''.join(
                        i_element for i_element in data['main_text'].values()))

                crud.update_message_db(user_id_class=msg_to_dlt_get_hotel_details_2.from_user.id,
                                       chat_id_class=msg_to_dlt_get_hotel_details_2.chat.id,
                                       message_id_class=msg_to_dlt_get_hotel_details_2.message_id)

                data['hotel_id'] = callback.data

                logger.info('user_id - {0}; id отеля - {1}'.format(callback.from_user.id, data['hotel_id']))

                data['hotel_name'] = [i_hotel[1] for i_hotel in data['hotels'] if i_hotel[0] == callback.data][0]

                logger.info('user_id - {0}; название отеля - {1}'.format(callback.from_user.id, data['hotel_name']))

                try:
                    hotel_details: List | int = find_hotel_details(user_id=callback.from_user.id,
                                                                   method_endswith='properties/v2/detail',
                                                                   method_type='POST', hotel_id=data['hotel_id'])

                    if type(hotel_details) == int:
                        raise ConnectionError

                    else:
                        data['hotel_address'] = hotel_details[0]

                        logger.info('user_id - {0}; адрес отеля - {1}'.
                                    format(callback.from_user.id, data['hotel_address']))

                        data['hotel_photo_url'] = hotel_details[1]

                        logger.info('user_id - {0}; фото отеля - {1}'.
                                    format(callback.from_user.id, data['hotel_photo_url']))

                        msg_to_dlt_get_hotel_details_3: Message = \
                            bot.send_message(
                                callback.message.chat.id,
                                text='Город:\n{0}\nНазвание:\n{1}\nАдрес:\n{2}\nФото:\n{3}'.
                                format(data['refined_city'][1], data['hotel_name'],
                                       data['hotel_address'], data['hotel_photo_url']))

                        crud.update_message_db(user_id_class=msg_to_dlt_get_hotel_details_3.from_user.id,
                                               chat_id_class=msg_to_dlt_get_hotel_details_3.chat.id,
                                               message_id_class=msg_to_dlt_get_hotel_details_3.message_id)

                        msg_to_dlt_get_hotel_details_4: Message = \
                            bot.send_message(callback.message.chat.id,
                                             text='Нажмите меню для выбора дальнейших действий.')

                        crud.update_message_db(user_id_class=msg_to_dlt_get_hotel_details_4.from_user.id,
                                               chat_id_class=msg_to_dlt_get_hotel_details_4.chat.id,
                                               message_id_class=msg_to_dlt_get_hotel_details_4.message_id)

                        data_db_request = [
                            {'created_at': datetime.datetime.now(), 'user': callback.from_user.id,
                             'city': data['city'],
                             'refined_city': data['refined_city'][1], 'arrival_date': data['arrival_date'],
                             'date_of_departure': data['date_of_departure'], 'min_price': data['min_price'],
                             'max_price': data['max_price'],
                             'max_distance_from_center': data['max_distance_from_center'],
                             'sorting_method_hotels': data['sorting_method_hotels'],
                             'adults_quantity': data['adults_quantity'],
                             'children_quantity': data['children_quantity'],
                             'children_ages': str(data['children_ages']),
                             'hotels': data['hotels'],
                             'hotel_id': data['hotel_id'],
                             'hotel_name': data['hotel_name'],
                             'hotel_address': data['hotel_address'],
                             'hotel_photo_url': data['hotel_photo_url']}]

                        crud.update_request_db(callback.from_user.id, data_db_request)

                except (AttributeError, KeyError) as exc:
                    logger.exception('user_id - {0}; тип ошибки - {1}'.format(callback.from_user.id, exc))

                    sg_to_dlt_mistake_13: Message = \
                        bot.send_message(callback.message.chat.id,
                                         text='Ошибка связи с сайтом.'
                                              '\nНажмите меню для выбора дальнейших действий.')

                    crud.update_message_db(user_id_class=sg_to_dlt_mistake_13.from_user.id,
                                           chat_id_class=sg_to_dlt_mistake_13.chat.id,
                                           message_id_class=sg_to_dlt_mistake_13.message_id)

                except (ReadTimeout, TimeoutError) as exc:
                    logger.exception('user_id - {0}; тип ошибки - {1}'.format(callback.from_user.id, exc))

                    msg_to_dlt_mistake_14: Message = \
                        bot.send_message(callback.message.chat.id,
                                         text='Ошибка. Время ожидания истекло.'
                                              '\nНажмите меню для выбора дальнейших действий.')

                    crud.update_message_db(user_id_class=msg_to_dlt_mistake_14.from_user.id,
                                           chat_id_class=msg_to_dlt_mistake_14.chat.id,
                                           message_id_class=msg_to_dlt_mistake_14.message_id)

                except ApiTelegramException as exc:
                    logger.exception('user_id - {0}; тип ошибки - {1}'.format(callback.from_user.id, exc))

                    msg_to_dlt_mistake_15: Message = \
                        bot.send_message(callback.message.chat.id,
                                         text='Ошибка связи с Телеграм.'
                                              '\nНажмите меню для выбора дальнейших действий.')

                    crud.update_message_db(user_id_class=msg_to_dlt_mistake_15.from_user.id,
                                           chat_id_class=msg_to_dlt_mistake_15.chat.id,
                                           message_id_class=msg_to_dlt_mistake_15.message_id)

                except ConnectionError as exc:
                    logger.exception('user_id - {0}; тип ошибки - {1}'.format(callback.from_user.id, exc))

                    msg_to_dlt_mistake_16: Message = \
                        bot.send_message(callback.message.chat.id,
                                         text='Ошибка связи с сайтом.'
                                              '\nНажмите меню для выбора дальнейших действий.')

                    crud.update_message_db(user_id_class=msg_to_dlt_mistake_16.from_user.id,
                                           chat_id_class=msg_to_dlt_mistake_16.chat.id,
                                           message_id_class=msg_to_dlt_mistake_16.message_id)

                except OperationalError as exc:
                    logger.exception('user_id - {0}; тип ошибки - {1}'.format(callback.from_user.id, exc))

                    msg_to_dlt_mistake_17: Message = \
                        bot.send_message(callback.message.chat.id,
                                         text='Ошибка доступа к Вашей базе запросов.'
                                              '\nНажмите меню для выбора дальнейших действий.')

                    crud.update_message_db(user_id_class=msg_to_dlt_mistake_17.from_user.id,
                                           chat_id_class=msg_to_dlt_mistake_17.chat.id,
                                           message_id_class=msg_to_dlt_mistake_17.message_id)
            else:

                msg_to_dlt_get_hotel_details_5: Message = bot.send_message(
                    callback.message.chat.id,
                    text=''.join(
                        i_element for i_element in data['main_text'].values()))

                crud.update_message_db(user_id_class=msg_to_dlt_get_hotel_details_5.from_user.id,
                                       chat_id_class=msg_to_dlt_get_hotel_details_5.chat.id,
                                       message_id_class=msg_to_dlt_get_hotel_details_5.message_id)

                for i_page in range(1, len(data['hotels']) + 1):
                    if str(i_page) == callback.data[4:]:
                        logger.debug('user_id - {0}; вызов - функция create_hotels_keyboard({1}, {2}, {3}'.
                                     format(callback.from_user.id, callback.message.chat.id,
                                            data['hotels'], i_page))

                        create_hotels_keyboard(callback.from_user.id, callback.message.chat.id, data['hotels'],
                                               page=i_page)

    except ApiTelegramException as exception:
        logger.exception(
            'user_id - {0}; тип ошибки - {1}'.format(callback.from_user.id, exception))

        msg_to_dlt_mistake_1: Message = \
            bot.send_message(callback.message.chat.id,
                             text='Ошибка связи с Телеграм.\nНажмите меню для выбора дальнейших действий.')

        crud.update_message_db(user_id_class=msg_to_dlt_mistake_1.from_user.id,
                               chat_id_class=msg_to_dlt_mistake_1.chat.id,
                               message_id_class=msg_to_dlt_mistake_1.message_id)

    except (ReadTimeout, TimeoutError) as exception:
        logger.exception(
            'user_id - {0}; тип ошибки - {1}'.format(callback.from_user.id, exception))

        msg_to_dlt_mistake_2: Message = \
            bot.send_message(callback.message.chat.id,
                             text='Ошибка. Время ожидания истекло.\nНажмите меню для выбора дальнейших действий.')

        crud.update_message_db(user_id_class=msg_to_dlt_mistake_2.from_user.id,
                               chat_id_class=msg_to_dlt_mistake_2.chat.id,
                               message_id_class=msg_to_dlt_mistake_2.message_id)

    except (OperationalError, ValueError, KeyError, NameError) as exception:
        logger.exception(
            'user_id - {0}; тип ошибки - {1}'.format(callback.from_user.id, exception))

        msg_to_dlt_mistake_3: Message = \
            bot.send_message(callback.message.chat.id,
                             text='Ошибка доступа к Вашей базе запросов.\nНажмите меню для выбора дальнейших действий.')

        crud.update_message_db(user_id_class=msg_to_dlt_mistake_3.from_user.id,
                               chat_id_class=msg_to_dlt_mistake_3.chat.id,
                               message_id_class=msg_to_dlt_mistake_3.message_id)


@bot.callback_query_handler(func=None, state=SearchStates.sorting_method_hotels)
def get_sorting_method_hotels(callback: CallbackQuery) -> None:
    """
    Функция обрабатывает результат работы клавиатуры sorting_method_hotels_keyboard и создает клавиатуру
    с методами сортировки отелей: по цене за сутки или по расстоянию от отеля до центра города.

    :param callback: Входящий запрос обратного вызова с кнопки клавиатуры sorting_method_hotels_keyboard
    :type callback: CallbackQuery
    """
    try:
        logger.info('user_id - {0}; callback.data - {1}'.format(callback.from_user.id, callback.data))

        logger.debug('user_id - {0}; вызов - функция get_sorting_method_hotels({1})'.
                     format(callback.from_user.id, callback))

        crud.delete_message_db(user_id_class=callback.from_user.id,
                               chat_id_class=callback.message.chat.id)

        with bot.retrieve_data(callback.from_user.id, callback.message.chat.id) as data:

            if callback.data == 'low_price':

                bot.set_state(callback.from_user.id, SearchStates.hotel_details,
                              callback.message.chat.id)

                msg_to_dlt_get_sorting_method_hotels_1: Message = bot.send_message(
                    callback.message.chat.id,
                    text=''.join(
                        i_element for i_element in data['main_text'].values()))

                crud.update_message_db(user_id_class=msg_to_dlt_get_sorting_method_hotels_1.from_user.id,
                                       chat_id_class=msg_to_dlt_get_sorting_method_hotels_1.chat.id,
                                       message_id_class=msg_to_dlt_get_sorting_method_hotels_1.message_id)

                data['sorting_method_hotels'] = callback.data

                logger.info('user_id - {0}; метод сортировки отелей - {1}'.
                            format(callback.from_user.id, data['sorting_method_hotels']))

                hotels_low_price = sorted(data['hotels'], key=lambda x: x[2])

                create_hotels_keyboard(callback.from_user.id, callback.message.chat.id, hotels_low_price)

            elif callback.data == 'high_price':

                bot.set_state(callback.from_user.id, SearchStates.hotel_details,
                              callback.message.chat.id)

                msg_to_dlt_get_sorting_method_hotels_2: Message = bot.send_message(
                    callback.message.chat.id,
                    text=''.join(
                        i_element for i_element in data['main_text'].values()))

                crud.update_message_db(user_id_class=msg_to_dlt_get_sorting_method_hotels_2.from_user.id,
                                       chat_id_class=msg_to_dlt_get_sorting_method_hotels_2.chat.id,
                                       message_id_class=msg_to_dlt_get_sorting_method_hotels_2.message_id)

                data['sorting_method_hotels'] = callback.data

                logger.info('user_id - {0}; метод сортировки отелей - {1}'.
                            format(callback.from_user.id, data['sorting_method_hotels']))

                hotels_high_price = sorted(data['hotels'], reverse=True, key=lambda x: x[2])

                data['hotels'] = hotels_high_price

                logger.info('user_id - {0}; отели - {1}'.format(callback.from_user.id, data['hotels']))

                create_hotels_keyboard(callback.from_user.id, callback.message.chat.id, hotels_high_price)

            elif callback.data == 'nearby_hotels':

                bot.set_state(callback.from_user.id, SearchStates.hotel_details,
                              callback.message.chat.id)

                msg_to_dlt_get_sorting_method_hotels_3: Message = bot.send_message(
                    callback.message.chat.id,
                    text=''.join(
                        i_element for i_element in data['main_text'].values()))

                crud.update_message_db(user_id_class=msg_to_dlt_get_sorting_method_hotels_3.from_user.id,
                                       chat_id_class=msg_to_dlt_get_sorting_method_hotels_3.chat.id,
                                       message_id_class=msg_to_dlt_get_sorting_method_hotels_3.message_id)

                data['sorting_method_hotels'] = callback.data

                logger.info('user_id - {0}; метод сортировки отелей - {1}'.
                            format(callback.from_user.id, data['sorting_method_hotels']))

                nearby_hotels = sorted(data['hotels'], key=lambda x: x[3])

                data['hotels'] = nearby_hotels

                logger.info('user_id - {0}; отели - {1}'.format(callback.from_user.id, data['hotels']))

                create_hotels_keyboard(callback.from_user.id, callback.message.chat.id, nearby_hotels)

            elif callback.data == 'distant_hotels':

                bot.set_state(callback.from_user.id, SearchStates.hotel_details,
                              callback.message.chat.id)

                msg_to_dlt_get_sorting_method_hotels_4: Message = bot.send_message(
                    callback.message.chat.id,
                    text=''.join(
                        i_element for i_element in data['main_text'].values()))

                crud.update_message_db(user_id_class=msg_to_dlt_get_sorting_method_hotels_4.from_user.id,
                                       chat_id_class=msg_to_dlt_get_sorting_method_hotels_4.chat.id,
                                       message_id_class=msg_to_dlt_get_sorting_method_hotels_4.message_id)

                data['sorting_method_hotels'] = callback.data

                logger.info('user_id - {0}; метод сортировки отелей - {1}'.
                            format(callback.from_user.id, data['sorting_method_hotels']))

                distant_hotels = sorted(data['hotels'], reverse=True, key=lambda x: x[3])

                data['hotels'] = distant_hotels

                logger.info('user_id - {0}; отели - {1}'.format(callback.from_user.id, data['hotels']))

                create_hotels_keyboard(callback.from_user.id, callback.message.chat.id, distant_hotels)

    except ApiTelegramException as exception:
        logger.exception(
            'user_id - {0}; тип ошибки - {1}'.format(callback.from_user.id, exception))

        msg_to_dlt_mistake_1: Message = \
            bot.send_message(callback.message.chat.id,
                             text='Ошибка связи с Телеграм.\nНажмите меню для выбора дальнейших действий.')

        crud.update_message_db(user_id_class=msg_to_dlt_mistake_1.from_user.id,
                               chat_id_class=msg_to_dlt_mistake_1.chat.id,
                               message_id_class=msg_to_dlt_mistake_1.message_id)

    except (ReadTimeout, TimeoutError) as exception:
        logger.exception(
            'user_id - {0}; тип ошибки - {1}'.format(callback.from_user.id, exception))

        msg_to_dlt_mistake_2: Message = \
            bot.send_message(callback.message.chat.id,
                             text='Ошибка. Время ожидания истекло.\nНажмите меню для выбора дальнейших действий.')

        crud.update_message_db(user_id_class=msg_to_dlt_mistake_2.from_user.id,
                               chat_id_class=msg_to_dlt_mistake_2.chat.id,
                               message_id_class=msg_to_dlt_mistake_2.message_id)

    except (OperationalError, ValueError, KeyError, NameError) as exception:
        logger.exception(
            'user_id - {0}; тип ошибки - {1}'.format(callback.from_user.id, exception))

        msg_to_dlt_mistake_3: Message = \
            bot.send_message(callback.message.chat.id,
                             text='Ошибка доступа к Вашей базе запросов.\nНажмите меню для выбора дальнейших действий.')

        crud.update_message_db(user_id_class=msg_to_dlt_mistake_3.from_user.id,
                               chat_id_class=msg_to_dlt_mistake_3.chat.id,
                               message_id_class=msg_to_dlt_mistake_3.message_id)


@bot.callback_query_handler(func=None, state=SearchStates.hotels)
def get_hotels(callback: CallbackQuery) -> None:
    """
    Функция обрабатывает результат работы клавиатуры yes_no_keyboard, в зависимости от ответа пользователя,
    предлагает изменить данные пользователя или выдает список отелей соответствующих запросам пользователя.

    :param callback: Входящий запрос обратного вызова с кнопки клавиатуры yes_no_keyboard
    :type callback: CallbackQuery
    """
    try:
        logger.info('user_id - {0}; callback.data - {1}'.format(callback.from_user.id, callback.data))

        logger.debug('user_id - {0}; вызов - функция get_hotels({1})'.
                     format(callback.from_user.id, callback))

        crud.delete_message_db(user_id_class=callback.from_user.id,
                               chat_id_class=callback.message.chat.id)

        with bot.retrieve_data(callback.from_user.id, callback.message.chat.id) as data:
            if callback.data == 'no':
                logger.warning('user_id - {0}; данные введены неверно: город - {1}; уточненный город - {2};'
                               ' дата приезда - {3}; дата отъезда - {4}; минимальная цена за сутки - {5};'
                               ' максимальная цена за сутки - {6}; максимальное расстояние до центра города - {7}.'.
                               format(callback.from_user.id, data['city'], data['refined_city'],
                                      data['arrival_date'], data['date_of_departure'],
                                      data['min_price'], data['max_price'],
                                      data['max_distance_from_center']))

                msg_to_dlt_get_hotels_1: Message = bot.send_message(
                    callback.message.chat.id,
                    text=''.join(
                        i_element for i_element in data['main_text'].values()))

                crud.update_message_db(user_id_class=msg_to_dlt_get_hotels_1.from_user.id,
                                       chat_id_class=msg_to_dlt_get_hotels_1.chat.id,
                                       message_id_class=msg_to_dlt_get_hotels_1.message_id)

                bot.set_state(callback.from_user.id, SearchStates.check_data,
                              callback.message.chat.id)

                create_return_states_keyboard(callback.from_user.id, callback.message.chat.id,
                                              data['children_quantity'])

            elif callback.data == 'yes':

                bot.set_state(callback.from_user.id, SearchStates.sorting_method_hotels,
                              callback.message.chat.id)

                try:
                    hotels: List | int | str = find_hotels(user_id=callback.from_user.id,
                                                           method_endswith='properties/v2/list', method_type='POST',
                                                           refine_city_id=data['refined_city'][0],
                                                           arrival_date=data['arrival_date'],
                                                           date_of_departure=data['date_of_departure'],
                                                           min_price=data['min_price'], max_price=data['max_price'],
                                                           adults_quantity=data['adults_quantity'],
                                                           children_ages=data['children_ages'],
                                                           max_distance_from_center=data[
                                                               'max_distance_from_center'])

                    if type(hotels) == int:
                        raise ConnectionError

                    else:
                        if hotels == 'not found':
                            logger.warning('user_id - {}; отелей не найдено'.format(callback.from_user.id))

                            msg_to_dlt_get_hotels_2: Message = bot.send_message(
                                callback.message.chat.id,
                                text=''.join(
                                    i_element for i_element in data['main_text'].values()))

                            crud.update_message_db(user_id_class=msg_to_dlt_get_hotels_2.from_user.id,
                                                   chat_id_class=msg_to_dlt_get_hotels_2.chat.id,
                                                   message_id_class=msg_to_dlt_get_hotels_2.message_id)

                            msg_to_dlt_get_hotels_3: Message = \
                                bot.send_message(
                                    callback.message.chat.id,
                                    text='По Вашему запросу ничего не найдено.'
                                         '\nНачните поиск заново или измените один из параметров.')

                            crud.update_message_db(user_id_class=msg_to_dlt_get_hotels_3.from_user.id,
                                                   chat_id_class=msg_to_dlt_get_hotels_3.chat.id,
                                                   message_id_class=msg_to_dlt_get_hotels_3.message_id)

                            bot.set_state(callback.from_user.id, SearchStates.check_data,
                                          callback.message.chat.id)

                            create_return_states_keyboard(callback.from_user.id, callback.message.chat.id,
                                                          data['children_quantity'])

                        else:
                            msg_to_dlt_get_hotels_4: Message = bot.send_message(
                                callback.message.chat.id,
                                text=''.join(
                                    i_element for i_element in data['main_text'].values()))

                            crud.update_message_db(user_id_class=msg_to_dlt_get_hotels_4.from_user.id,
                                                   chat_id_class=msg_to_dlt_get_hotels_4.chat.id,
                                                   message_id_class=msg_to_dlt_get_hotels_4.message_id)

                            data['hotels'] = hotels

                            logger.info('user_id - {0}; отели - {1}'.format(callback.from_user.id, data['hotels']))

                            create_sorting_method_hotels_keyboard(callback.from_user.id, callback.message.chat.id)

                except (AttributeError, KeyError) as exc:
                    logger.exception('user_id - {0}; тип ошибки - {1}'.format(callback.from_user.id, exc))

                    msg_to_dlt_mistake_9: Message = \
                        bot.send_message(callback.message.chat.id,
                                         text='Ошибка связи с сайтом.'
                                              '\nНажмите меню для выбора дальнейших действий.')

                    crud.update_message_db(user_id_class=msg_to_dlt_mistake_9.from_user.id,
                                           chat_id_class=msg_to_dlt_mistake_9.chat.id,
                                           message_id_class=msg_to_dlt_mistake_9.message_id)

                except (ReadTimeout, TimeoutError) as exc:
                    logger.exception('user_id - {0}; тип ошибки - {1}'.format(callback.from_user.id, exc))

                    msg_to_dlt_mistake_10: Message = \
                        bot.send_message(callback.message.chat.id,
                                         text='Ошибка. Время ожидания истекло.'
                                              '\nНажмите меню для выбора дальнейших действий.')

                    crud.update_message_db(user_id_class=msg_to_dlt_mistake_10.from_user.id,
                                           chat_id_class=msg_to_dlt_mistake_10.chat.id,
                                           message_id_class=msg_to_dlt_mistake_10.message_id)

                except ApiTelegramException as exc:
                    logger.exception('user_id - {0}; тип ошибки - {1}'.format(callback.from_user.id, exc))

                    msg_to_dlt_mistake_11: Message = \
                        bot.send_message(callback.message.chat.id,
                                         text='Ошибка связи с Телеграм.'
                                              '\nНажмите меню для выбора дальнейших действий.')

                    crud.update_message_db(user_id_class=msg_to_dlt_mistake_11.from_user.id,
                                           chat_id_class=msg_to_dlt_mistake_11.chat.id,
                                           message_id_class=msg_to_dlt_mistake_11.message_id)

                except ConnectionError as exc:
                    logger.exception('user_id - {0}; тип ошибки - {1}'.format(callback.from_user.id, exc))

                    msg_to_dlt_mistake_12: Message = \
                        bot.send_message(callback.message.chat.id,
                                         text='Ошибка связи с сайтом.'
                                              '\nНажмите меню для выбора дальнейших действий.')

                    crud.update_message_db(user_id_class=msg_to_dlt_mistake_12.from_user.id,
                                           chat_id_class=msg_to_dlt_mistake_12.chat.id,
                                           message_id_class=msg_to_dlt_mistake_12.message_id)

    except ApiTelegramException as exception:
        logger.exception(
            'user_id - {0}; тип ошибки - {1}'.format(callback.from_user.id, exception))

        msg_to_dlt_mistake_1: Message = \
            bot.send_message(callback.message.chat.id,
                             text='Ошибка связи с Телеграм.\nНажмите меню для выбора дальнейших действий.')

        crud.update_message_db(user_id_class=msg_to_dlt_mistake_1.from_user.id,
                               chat_id_class=msg_to_dlt_mistake_1.chat.id,
                               message_id_class=msg_to_dlt_mistake_1.message_id)

    except (ReadTimeout, TimeoutError) as exception:
        logger.exception(
            'user_id - {0}; тип ошибки - {1}'.format(callback.from_user.id, exception))

        msg_to_dlt_mistake_2: Message = \
            bot.send_message(callback.message.chat.id,
                             text='Ошибка. Время ожидания истекло.\nНажмите меню для выбора дальнейших действий.')

        crud.update_message_db(user_id_class=msg_to_dlt_mistake_2.from_user.id,
                               chat_id_class=msg_to_dlt_mistake_2.chat.id,
                               message_id_class=msg_to_dlt_mistake_2.message_id)

    except (OperationalError, ValueError, KeyError, NameError) as exception:
        logger.exception(
            'user_id - {0}; тип ошибки - {1}'.format(callback.from_user.id, exception))

        msg_to_dlt_mistake_3: Message = \
            bot.send_message(callback.message.chat.id,
                             text='Ошибка доступа к Вашей базе запросов.\nНажмите меню для выбора дальнейших действий.')

        crud.update_message_db(user_id_class=msg_to_dlt_mistake_3.from_user.id,
                               chat_id_class=msg_to_dlt_mistake_3.chat.id,
                               message_id_class=msg_to_dlt_mistake_3.message_id)


@bot.callback_query_handler(func=None, state=SearchStates.check_data)
def change_states(callback: CallbackQuery) -> None:
    """
    Функция обрабатывает результат работы клавиатуры return_states_keyboard и позволяет изменить
    данные пользователя введенные ранее.

    :param callback: Входящий запрос обратного вызова с кнопки
    клавиатуры return_states_keyboard
    :type callback: CallbackQuery
    """
    try:
        logger.info('user_id - {0}; callback.data - {1}'.
                    format(callback.from_user.id,
                           callback.data))

        logger.debug('user_id - {0}; вызов - функция change_states({1})'.
                     format(callback.from_user.id, callback))

        crud.delete_message_db(user_id_class=callback.from_user.id,
                               chat_id_class=callback.message.chat.id)

        with bot.retrieve_data(callback.from_user.id,
                               callback.message.chat.id) as data_change_states:

            if callback.data == 'city':
                logger.warning('user_id - {0}; город {1} введен неверно'.
                               format(callback.from_user.id,
                                      data_change_states['city']))

                bot.set_state(callback.from_user.id, SearchStates.city_rewrite,
                              callback.message.chat.id)

                msg_to_dlt_change_states_1: Message = bot.send_message(
                    callback.message.chat.id,
                    text=''.join(
                        i_element for i_element in data_change_states['main_text'].values()))

                crud.update_message_db(user_id_class=msg_to_dlt_change_states_1.from_user.id,
                                       chat_id_class=msg_to_dlt_change_states_1.chat.id,
                                       message_id_class=msg_to_dlt_change_states_1.message_id)

                msg_to_dlt_change_states_2: Message = bot.send_message(callback.message.chat.id,
                                                                       text='Введите другой город:')

                crud.update_message_db(user_id_class=msg_to_dlt_change_states_2.from_user.id,
                                       chat_id_class=msg_to_dlt_change_states_2.chat.id,
                                       message_id_class=msg_to_dlt_change_states_2.message_id)

            elif callback.data == 'arrival_date':
                logger.warning('user_id - {0}; дата приезда {1} введена неверно'.
                               format(callback.from_user.id,
                                      data_change_states['arrival_date']))

                bot.set_state(callback.from_user.id,
                              SearchStates.arrival_date_rewrite,
                              callback.message.chat.id)

                msg_to_dlt_change_states_3: Message = bot.send_message(
                    callback.message.chat.id,
                    text=''.join(
                        i_element for i_element in data_change_states['main_text'].values()))

                crud.update_message_db(user_id_class=msg_to_dlt_change_states_3.from_user.id,
                                       chat_id_class=msg_to_dlt_change_states_3.chat.id,
                                       message_id_class=msg_to_dlt_change_states_3.message_id)

                msg_to_dlt_change_states_4: Message = bot.send_message(callback.message.chat.id,
                                                                       text='Введите другую дату приезда:')

                crud.update_message_db(user_id_class=msg_to_dlt_change_states_4.from_user.id,
                                       chat_id_class=msg_to_dlt_change_states_4.chat.id,
                                       message_id_class=msg_to_dlt_change_states_4.message_id)

                run_calendar(callback.from_user.id, callback.message.chat.id)

            elif callback.data == 'date_of_departure':
                logger.warning('user_id - {0}; дата отъезда {1} введена неверно'.
                               format(callback.from_user.id,
                                      data_change_states['date_of_departure']))

                bot.set_state(callback.from_user.id,
                              SearchStates.date_of_departure_rewrite,
                              callback.message.chat.id)

                msg_to_dlt_change_states_5: Message = bot.send_message(
                    callback.message.chat.id,
                    text=''.join(
                        i_element for i_element in data_change_states['main_text'].values()))

                crud.update_message_db(user_id_class=msg_to_dlt_change_states_5.from_user.id,
                                       chat_id_class=msg_to_dlt_change_states_5.chat.id,
                                       message_id_class=msg_to_dlt_change_states_5.message_id)

                msg_to_dlt_change_states_17: Message = bot.send_message(callback.message.chat.id,
                                                                        text='Введите другую дату отъезда:')

                crud.update_message_db(user_id_class=msg_to_dlt_change_states_17.from_user.id,
                                       chat_id_class=msg_to_dlt_change_states_17.chat.id,
                                       message_id_class=msg_to_dlt_change_states_17.message_id)

                run_calendar(callback.from_user.id, callback.message.chat.id)

            elif callback.data == 'min_price':
                logger.warning('user_id - {0}; минимальная цена {1}$ введена неверно'.
                               format(callback.from_user.id,
                                      data_change_states['min_price']))

                bot.set_state(callback.from_user.id, SearchStates.min_price_rewrite,
                              callback.message.chat.id)

                msg_to_dlt_change_states_6: Message = bot.send_message(
                    callback.message.chat.id,
                    text=''.join(
                        i_element for i_element in data_change_states['main_text'].values()))

                crud.update_message_db(user_id_class=msg_to_dlt_change_states_6.from_user.id,
                                       chat_id_class=msg_to_dlt_change_states_6.chat.id,
                                       message_id_class=msg_to_dlt_change_states_6.message_id)

                msg_to_dlt_change_states_7: Message = \
                    bot.send_message(callback.message.chat.id,
                                     text='Введите другую минимальную цену проживания за сутки в $:')

                crud.update_message_db(user_id_class=msg_to_dlt_change_states_7.from_user.id,
                                       chat_id_class=msg_to_dlt_change_states_7.chat.id,
                                       message_id_class=msg_to_dlt_change_states_7.message_id)

            elif callback.data == 'max_price':
                logger.warning('user_id - {0}; максимальная цена {1}$ введена неверно'.
                               format(callback.from_user.id,
                                      data_change_states['max_price']))

                bot.set_state(callback.from_user.id, SearchStates.max_price_rewrite,
                              callback.message.chat.id)

                msg_to_dlt_change_states_8: Message = bot.send_message(
                    callback.message.chat.id,
                    text=''.join(
                        i_element for i_element in data_change_states['main_text'].values()))

                crud.update_message_db(user_id_class=msg_to_dlt_change_states_8.from_user.id,
                                       chat_id_class=msg_to_dlt_change_states_8.chat.id,
                                       message_id_class=msg_to_dlt_change_states_8.message_id)

                msg_to_dlt_change_states_9: Message = \
                    bot.send_message(callback.message.chat.id,
                                     text='Введите другую максимальную цену проживания за сутки в $:')

                crud.update_message_db(user_id_class=msg_to_dlt_change_states_9.from_user.id,
                                       chat_id_class=msg_to_dlt_change_states_9.chat.id,
                                       message_id_class=msg_to_dlt_change_states_9.message_id)

            elif callback.data == 'adults_quantity':
                logger.warning('user_id - {0}; количество взрослых {1} введено неверно'.
                               format(callback.from_user.id,
                                      data_change_states['adults_quantity']))

                bot.set_state(callback.from_user.id, SearchStates.adults_quantity_rewrite,
                              callback.message.chat.id)

                msg_to_dlt_change_states_10: Message = bot.send_message(
                    callback.message.chat.id,
                    text=''.join(
                        i_element for i_element in data_change_states['main_text'].values()))

                crud.update_message_db(user_id_class=msg_to_dlt_change_states_10.from_user.id,
                                       chat_id_class=msg_to_dlt_change_states_10.chat.id,
                                       message_id_class=msg_to_dlt_change_states_10.message_id)

                msg_to_dlt_change_states_11: Message = bot.send_message(callback.message.chat.id,
                                                                        text='Введите другое количество взрослых:')

                crud.update_message_db(user_id_class=msg_to_dlt_change_states_11.from_user.id,
                                       chat_id_class=msg_to_dlt_change_states_11.chat.id,
                                       message_id_class=msg_to_dlt_change_states_11.message_id)

            elif callback.data == 'children_quantity':
                logger.warning('user_id - {0}; количество детей {1} введено неверно'.
                               format(callback.from_user.id,
                                      data_change_states['children_quantity']))

                bot.set_state(callback.from_user.id, SearchStates.children_quantity_rewrite,
                              callback.message.chat.id)

                msg_to_dlt_change_states_12: Message = bot.send_message(
                    callback.message.chat.id,
                    text=''.join(
                        i_element for i_element in data_change_states['main_text'].values()))

                crud.update_message_db(user_id_class=msg_to_dlt_change_states_12.from_user.id,
                                       chat_id_class=msg_to_dlt_change_states_12.chat.id,
                                       message_id_class=msg_to_dlt_change_states_12.message_id)

                msg_to_dlt_change_states_13: Message = bot.send_message(callback.message.chat.id,
                                                                        text='Введите другое количество детей:')

                crud.update_message_db(user_id_class=msg_to_dlt_change_states_13.from_user.id,
                                       chat_id_class=msg_to_dlt_change_states_13.chat.id,
                                       message_id_class=msg_to_dlt_change_states_13.message_id)

            elif callback.data.startswith('children_ages'):
                data_change_states['child_number'] = callback.data[14:]

                logger.warning(
                    'user_id - {0}; возраст {1}-го ребенка {2} введен неверно'.
                    format(callback.from_user.id,
                           data_change_states['child_number'],
                           data_change_states['children_ages'][int(
                               data_change_states['child_number']) - 1]['age']))

                bot.set_state(callback.from_user.id, SearchStates.single_child_age_rewrite,
                              callback.message.chat.id)

                msg_to_dlt_change_states_14: Message = bot.send_message(
                    callback.message.chat.id,
                    text=''.join(
                        i_element for i_element in data_change_states['main_text'].values()))

                crud.update_message_db(user_id_class=msg_to_dlt_change_states_14.from_user.id,
                                       chat_id_class=msg_to_dlt_change_states_14.chat.id,
                                       message_id_class=msg_to_dlt_change_states_14.message_id)

                msg_to_dlt_change_states_15: Message = bot.send_message(callback.message.chat.id,
                                                                        text='Введите другой возраст {}-го ребенка:'.
                                                                        format(callback.data[14:]))

                crud.update_message_db(user_id_class=msg_to_dlt_change_states_15.from_user.id,
                                       chat_id_class=msg_to_dlt_change_states_15.chat.id,
                                       message_id_class=msg_to_dlt_change_states_15.message_id)

            elif callback.data == 'max_distance_from_center':
                logger.warning('user_id - {0}; расстояние до центра города {1}км введено неверно'.
                               format(callback.from_user.id,
                                      data_change_states['max_distance_from_center']))

                bot.set_state(callback.from_user.id,
                              SearchStates.max_distance_from_center_rewrite,
                              callback.message.chat.id)

                msg_to_dlt_change_states_16: Message = bot.send_message(
                    callback.message.chat.id,
                    text=''.join(
                        i_element for i_element in data_change_states['main_text'].values()))

                crud.update_message_db(user_id_class=msg_to_dlt_change_states_16.from_user.id,
                                       chat_id_class=msg_to_dlt_change_states_16.chat.id,
                                       message_id_class=msg_to_dlt_change_states_16.message_id)

                create_km_mile_keyboard(callback.from_user.id, callback.message.chat.id)

    except ApiTelegramException as exception:
        logger.exception(
            'user_id - {0}; тип ошибки - {1}'.format(callback.from_user.id, exception))

        msg_to_dlt_mistake_1: Message = \
            bot.send_message(callback.message.chat.id,
                             text='Ошибка связи с Телеграм.\nНажмите меню для выбора дальнейших действий.')

        crud.update_message_db(user_id_class=msg_to_dlt_mistake_1.from_user.id,
                               chat_id_class=msg_to_dlt_mistake_1.chat.id,
                               message_id_class=msg_to_dlt_mistake_1.message_id)

    except (ReadTimeout, TimeoutError) as exception:
        logger.exception(
            'user_id - {0}; тип ошибки - {1}'.format(callback.from_user.id, exception))

        msg_to_dlt_mistake_2: Message = \
            bot.send_message(callback.message.chat.id,
                             text='Ошибка. Время ожидания истекло.\nНажмите меню для выбора дальнейших действий.')

        crud.update_message_db(user_id_class=msg_to_dlt_mistake_2.from_user.id,
                               chat_id_class=msg_to_dlt_mistake_2.chat.id,
                               message_id_class=msg_to_dlt_mistake_2.message_id)

    except (OperationalError, ValueError, KeyError, NameError) as exception:
        logger.exception(
            'user_id - {0}; тип ошибки - {1}'.format(callback.from_user.id, exception))

        msg_to_dlt_mistake_3: Message = \
            bot.send_message(callback.message.chat.id,
                             text='Ошибка доступа к Вашей базе запросов.\nНажмите меню для выбора дальнейших действий.')

        crud.update_message_db(user_id_class=msg_to_dlt_mistake_3.from_user.id,
                               chat_id_class=msg_to_dlt_mistake_3.chat.id,
                               message_id_class=msg_to_dlt_mistake_3.message_id)


@bot.message_handler(state=SearchStates.max_distance_from_center_rewrite_mile)
def get_rewrite_max_distance_from_center_mile(message_rewrite_max_distance_mile: Message) -> None:
    """
    Функция принимает от пользователя расстояние в милях от отеля до центра города, проверяет чтобы это
    значение было числом и не было отрицательным, переводит это значение в километры,
    сохраняет это значение.

    :param message_rewrite_max_distance_mile: Значение полученное от пользователя
    :type message_rewrite_max_distance_mile: Message
    """
    try:
        logger.debug('user_id - {0}; вызов - функция get_rewrite_max_distance_from_center_mile({1})'.
                     format(message_rewrite_max_distance_mile.from_user.id,
                            message_rewrite_max_distance_mile))

        crud.update_message_db(user_id_class=message_rewrite_max_distance_mile.from_user.id,
                               chat_id_class=message_rewrite_max_distance_mile.chat.id,
                               message_id_class=message_rewrite_max_distance_mile.message_id)

        crud.delete_message_db(user_id_class=message_rewrite_max_distance_mile.from_user.id,
                               chat_id_class=message_rewrite_max_distance_mile.chat.id)

        with bot.retrieve_data(message_rewrite_max_distance_mile.from_user.id,
                               message_rewrite_max_distance_mile.chat.id) as \
                data_rewrite_max_distance_mile:

            if not message_rewrite_max_distance_mile.text.isdigit():
                logger.warning('user_id - {0}; расстояние {1} в милях  не является числом или'
                               ' отрицательное число'.
                               format(message_rewrite_max_distance_mile.from_user.id,
                                      message_rewrite_max_distance_mile.text))

                msg_to_dlt_get_rewrite_max_distance_mil_1: Message = bot.send_message(
                    message_rewrite_max_distance_mile.chat.id,
                    text=''.join(
                        i_element for i_element in
                        data_rewrite_max_distance_mile['main_text'].values()))

                crud.update_message_db(
                    user_id_class=msg_to_dlt_get_rewrite_max_distance_mil_1.from_user.id,
                    chat_id_class=msg_to_dlt_get_rewrite_max_distance_mil_1.chat.id,
                    message_id_class=msg_to_dlt_get_rewrite_max_distance_mil_1.message_id)

                msg_to_dlt_get_rewrite_max_distance_mil_2: Message = bot.send_message(
                    message_rewrite_max_distance_mile.chat.id,
                    text='Расстояние {} в милях должно быть числом и'
                         ' не может быть отрицательным!!!!'
                         '\nВведите  другое максимальное расстояние от центра города:'.
                    format(message_rewrite_max_distance_mile.text))

                crud.update_message_db(
                    user_id_class=msg_to_dlt_get_rewrite_max_distance_mil_2.from_user.id,
                    chat_id_class=msg_to_dlt_get_rewrite_max_distance_mil_2.chat.id,
                    message_id_class=msg_to_dlt_get_rewrite_max_distance_mil_2.message_id)

                bot.set_state(message_rewrite_max_distance_mile.from_user.id,
                              SearchStates.max_distance_from_center_rewrite_mile,
                              message_rewrite_max_distance_mile.chat.id)

            else:
                bot.set_state(message_rewrite_max_distance_mile.from_user.id, SearchStates.hotels,
                              message_rewrite_max_distance_mile.chat.id)

                result_distance = int(message_rewrite_max_distance_mile.text) * 1.609344

                data_rewrite_max_distance_mile['max_distance_from_center'] = str(result_distance)
                data_rewrite_max_distance_mile['main_text']['max_distance_from_center'] = \
                    '\nМаксимальное расстояние до центра города - {}км.'. \
                    format(data_rewrite_max_distance_mile['max_distance_from_center'])

                logger.info('user_id - {0}; максимальное расстояние от центра города - {1}км'.
                            format(message_rewrite_max_distance_mile.from_user.id,
                                   data_rewrite_max_distance_mile['max_distance_from_center']))

                msg_to_dlt_get_rewrite_max_distance_mil_3: Message = bot.send_message(
                    message_rewrite_max_distance_mile.chat.id,
                    text=''.join(
                        i_element for i_element in
                        data_rewrite_max_distance_mile['main_text'].values()))

                crud.update_message_db(
                    user_id_class=msg_to_dlt_get_rewrite_max_distance_mil_3.from_user.id,
                    chat_id_class=msg_to_dlt_get_rewrite_max_distance_mil_3.chat.id,
                    message_id_class=msg_to_dlt_get_rewrite_max_distance_mil_3.message_id)

                msg_to_dlt_get_rewrite_max_distance_mil_4: Message = bot.send_message(
                    message_rewrite_max_distance_mile.chat.id,
                    text='Проверьте Ваш запрос.\nВсе верно?',
                    reply_markup=create_yes_no_keyboard(
                        user_id=message_rewrite_max_distance_mile.from_user.id,
                        callback_data_yes='yes', callback_data_no='no'))

                crud.update_message_db(
                    user_id_class=msg_to_dlt_get_rewrite_max_distance_mil_4.from_user.id,
                    chat_id_class=msg_to_dlt_get_rewrite_max_distance_mil_4.chat.id,
                    message_id_class=msg_to_dlt_get_rewrite_max_distance_mil_4.message_id)

    except ApiTelegramException as exception:
        logger.exception(
            'user_id - {0}; тип ошибки - {1}'.format(message_rewrite_max_distance_mile.from_user.id, exception))

        msg_to_dlt_mistake_1: Message = \
            bot.send_message(message_rewrite_max_distance_mile.chat.id,
                             text='Ошибка связи с Телеграм.\nНажмите меню для выбора дальнейших действий.')

        crud.update_message_db(user_id_class=msg_to_dlt_mistake_1.from_user.id,
                               chat_id_class=msg_to_dlt_mistake_1.chat.id,
                               message_id_class=msg_to_dlt_mistake_1.message_id)

    except (ReadTimeout, TimeoutError) as exception:
        logger.exception(
            'user_id - {0}; тип ошибки - {1}'.format(message_rewrite_max_distance_mile.from_user.id, exception))

        msg_to_dlt_mistake_2: Message = \
            bot.send_message(message_rewrite_max_distance_mile.chat.id,
                             text='Ошибка. Время ожидания истекло.\nНажмите меню для выбора дальнейших действий.')

        crud.update_message_db(user_id_class=msg_to_dlt_mistake_2.from_user.id,
                               chat_id_class=msg_to_dlt_mistake_2.chat.id,
                               message_id_class=msg_to_dlt_mistake_2.message_id)

    except (OperationalError, ValueError, KeyError, NameError) as exception:
        logger.exception(
            'user_id - {0}; тип ошибки - {1}'.format(message_rewrite_max_distance_mile.from_user.id, exception))

        msg_to_dlt_mistake_3: Message = \
            bot.send_message(message_rewrite_max_distance_mile.chat.id,
                             text='Ошибка доступа к Вашей базе запросов.\nНажмите меню для выбора дальнейших действий.')

        crud.update_message_db(user_id_class=msg_to_dlt_mistake_3.from_user.id,
                               chat_id_class=msg_to_dlt_mistake_3.chat.id,
                               message_id_class=msg_to_dlt_mistake_3.message_id)


@bot.message_handler(state=SearchStates.max_distance_from_center_rewrite_km)
def get_rewrite_max_distance_from_center_km(message_rewrite_max_distance_km: Message) -> None:
    """
    Функция принимает от пользователя расстояние в километрах от отеля до центра города,
    проверяет чтобы это значение было числом и не было отрицательным, сохраняет это значение.

    :param message_rewrite_max_distance_km: Значение полученное от пользователя
    :type message_rewrite_max_distance_km: Message
    """
    try:
        logger.debug('user_id - {0}; вызов - функция get_rewrite_max_distance_from_center_km({1})'.
                     format(message_rewrite_max_distance_km.from_user.id,
                            message_rewrite_max_distance_km))

        crud.update_message_db(user_id_class=message_rewrite_max_distance_km.from_user.id,
                               chat_id_class=message_rewrite_max_distance_km.chat.id,
                               message_id_class=message_rewrite_max_distance_km.message_id)

        crud.delete_message_db(user_id_class=message_rewrite_max_distance_km.from_user.id,
                               chat_id_class=message_rewrite_max_distance_km.chat.id)

        with bot.retrieve_data(message_rewrite_max_distance_km.from_user.id,
                               message_rewrite_max_distance_km.chat.id) as \
                data_rewrite_max_distance_km:

            if not message_rewrite_max_distance_km.text.isdigit():
                logger.warning(
                    'user_id - {0}; расстояние {1}км не является числом или отрицательное число'.
                    format(message_rewrite_max_distance_km.from_user.id,
                           message_rewrite_max_distance_km.text))

                msg_to_dlt_get_rewrite_max_distance_km_1: Message = bot.send_message(
                    message_rewrite_max_distance_km.chat.id,
                    text=''.join(
                        i_element for i_element in data_rewrite_max_distance_km['main_text'].values()))

                crud.update_message_db(
                    user_id_class=msg_to_dlt_get_rewrite_max_distance_km_1.from_user.id,
                    chat_id_class=msg_to_dlt_get_rewrite_max_distance_km_1.chat.id,
                    message_id_class=msg_to_dlt_get_rewrite_max_distance_km_1.message_id)

                msg_to_dlt_get_rewrite_max_distance_km_2: Message = bot.send_message(
                    message_rewrite_max_distance_km.chat.id,
                    text='Расстояние {}км должно быть числом и не может быть отрицательным!!!!'
                         '\nВведите другое максимальное расстояние от центра города:'.
                    format(message_rewrite_max_distance_km.text))

                crud.update_message_db(
                    user_id_class=msg_to_dlt_get_rewrite_max_distance_km_2.from_user.id,
                    chat_id_class=msg_to_dlt_get_rewrite_max_distance_km_2.chat.id,
                    message_id_class=msg_to_dlt_get_rewrite_max_distance_km_2.message_id)

                bot.set_state(message_rewrite_max_distance_km.from_user.id,
                              SearchStates.max_distance_from_center_rewrite_km,
                              message_rewrite_max_distance_km.chat.id)

            else:
                bot.set_state(message_rewrite_max_distance_km.from_user.id, SearchStates.hotels,
                              message_rewrite_max_distance_km.chat.id)

                data_rewrite_max_distance_km[
                    'max_distance_from_center'] = message_rewrite_max_distance_km.text
                data_rewrite_max_distance_km['main_text']['max_distance_from_center'] = \
                    '\nМаксимальное расстояние до центра города - {}км.'. \
                    format(data_rewrite_max_distance_km['max_distance_from_center'])

                logger.info('user_id - {0}; максимальное расстояние от центра города - {1}км'.
                            format(message_rewrite_max_distance_km.from_user.id,
                                   data_rewrite_max_distance_km['max_distance_from_center']))

                msg_to_dlt_get_rewrite_max_distance_km_3: Message = bot.send_message(
                    message_rewrite_max_distance_km.chat.id,
                    text=''.join(
                        i_element for i_element in data_rewrite_max_distance_km['main_text'].values()))

                crud.update_message_db(
                    user_id_class=msg_to_dlt_get_rewrite_max_distance_km_3.from_user.id,
                    chat_id_class=msg_to_dlt_get_rewrite_max_distance_km_3.chat.id,
                    message_id_class=msg_to_dlt_get_rewrite_max_distance_km_3.message_id)

                msg_to_dlt_get_rewrite_max_distance_km_4: Message = bot.send_message(
                    message_rewrite_max_distance_km.chat.id,
                    text='Проверьте Ваш запрос.\nВсе верно?',
                    reply_markup=create_yes_no_keyboard(
                        user_id=message_rewrite_max_distance_km.from_user.id,
                        callback_data_yes='yes',
                        callback_data_no='no'))

                crud.update_message_db(
                    user_id_class=msg_to_dlt_get_rewrite_max_distance_km_4.from_user.id,
                    chat_id_class=msg_to_dlt_get_rewrite_max_distance_km_4.chat.id,
                    message_id_class=msg_to_dlt_get_rewrite_max_distance_km_4.message_id)

    except ApiTelegramException as exception:
        logger.exception(
            'user_id - {0}; тип ошибки - {1}'.format(message_rewrite_max_distance_km.from_user.id, exception))

        msg_to_dlt_mistake_1: Message = \
            bot.send_message(message_rewrite_max_distance_km.chat.id,
                             text='Ошибка связи с Телеграм.\nНажмите меню для выбора дальнейших действий.')

        crud.update_message_db(user_id_class=msg_to_dlt_mistake_1.from_user.id,
                               chat_id_class=msg_to_dlt_mistake_1.chat.id,
                               message_id_class=msg_to_dlt_mistake_1.message_id)

    except (ReadTimeout, TimeoutError) as exception:
        logger.exception(
            'user_id - {0}; тип ошибки - {1}'.format(message_rewrite_max_distance_km.from_user.id, exception))

        msg_to_dlt_mistake_2: Message = \
            bot.send_message(message_rewrite_max_distance_km.chat.id,
                             text='Ошибка. Время ожидания истекло.\nНажмите меню для выбора дальнейших действий.')

        crud.update_message_db(user_id_class=msg_to_dlt_mistake_2.from_user.id,
                               chat_id_class=msg_to_dlt_mistake_2.chat.id,
                               message_id_class=msg_to_dlt_mistake_2.message_id)

    except (OperationalError, ValueError, KeyError, NameError) as exception:
        logger.exception(
            'user_id - {0}; тип ошибки - {1}'.format(message_rewrite_max_distance_km.from_user.id, exception))

        msg_to_dlt_mistake_3: Message = \
            bot.send_message(message_rewrite_max_distance_km.chat.id,
                             text='Ошибка доступа к Вашей базе запросов.\nНажмите меню для выбора дальнейших действий.')

        crud.update_message_db(user_id_class=msg_to_dlt_mistake_3.from_user.id,
                               chat_id_class=msg_to_dlt_mistake_3.chat.id,
                               message_id_class=msg_to_dlt_mistake_3.message_id)


@bot.callback_query_handler(func=None, state=SearchStates.max_distance_from_center_rewrite)
def get_rewrite_max_distance_from_center(callback: CallbackQuery) -> None:
    """
    Функция обрабатывает уточненный результат работы клавиатуры km_mile_keyboard.

    :param callback: Входящий запрос обратного вызова с кнопки клавиатуры km_mile_keyboard
    :type callback: CallbackQuery
    """
    try:
        logger.info('user_id - {0}; callback.data - {1}'.format(callback.from_user.id, callback.data))

        logger.debug('user_id - {0}; вызов - функция get_rewrite_max_distance_from_center({1})'.
                     format(callback.from_user.id, callback))

        crud.delete_message_db(user_id_class=callback.from_user.id,
                               chat_id_class=callback.message.chat.id)

        with bot.retrieve_data(callback.from_user.id, callback.message.chat.id) \
                as data_rewrite_max_distance:

            if callback.data == 'km':

                bot.set_state(callback.from_user.id,
                              SearchStates.max_distance_from_center_rewrite_km,
                              callback.message.chat.id)

                msg_to_dlt_get_rewrite_max_distance_1: Message = bot.send_message(
                    callback.message.chat.id,
                    text=''.join(i_element for i_element in data_rewrite_max_distance['main_text'].values()))

                crud.update_message_db(user_id_class=msg_to_dlt_get_rewrite_max_distance_1.from_user.id,
                                       chat_id_class=msg_to_dlt_get_rewrite_max_distance_1.chat.id,
                                       message_id_class=msg_to_dlt_get_rewrite_max_distance_1.message_id)

                msg_to_dlt_get_rewrite_max_distance_2: Message = \
                    bot.send_message(callback.message.chat.id,
                                     text='Введите максимальное расстояние от центра города в км:')

                crud.update_message_db(user_id_class=msg_to_dlt_get_rewrite_max_distance_2.from_user.id,
                                       chat_id_class=msg_to_dlt_get_rewrite_max_distance_2.chat.id,
                                       message_id_class=msg_to_dlt_get_rewrite_max_distance_2.message_id)

            elif callback.data == 'mile':

                bot.set_state(callback.from_user.id,
                              SearchStates.max_distance_from_center_rewrite_mile,
                              callback.message.chat.id)

                msg_to_dlt_rewrite_get_max_distance_3: Message = bot.send_message(
                    callback.message.chat.id,
                    text=''.join(i_element for i_element in data_rewrite_max_distance['main_text'].values()))

                crud.update_message_db(user_id_class=msg_to_dlt_rewrite_get_max_distance_3.from_user.id,
                                       chat_id_class=msg_to_dlt_rewrite_get_max_distance_3.chat.id,
                                       message_id_class=msg_to_dlt_rewrite_get_max_distance_3.message_id)

                msg_to_dlt_rewrite_get_max_distance_4: Message = \
                    bot.send_message(callback.message.chat.id,
                                     text='Введите максимальное расстояние от центра города в милях:')

                crud.update_message_db(user_id_class=msg_to_dlt_rewrite_get_max_distance_4.from_user.id,
                                       chat_id_class=msg_to_dlt_rewrite_get_max_distance_4.chat.id,
                                       message_id_class=msg_to_dlt_rewrite_get_max_distance_4.message_id)

    except ApiTelegramException as exception:
        logger.exception(
            'user_id - {0}; тип ошибки - {1}'.format(callback.from_user.id, exception))

        msg_to_dlt_mistake_1: Message = \
            bot.send_message(callback.message.chat.id,
                             text='Ошибка связи с Телеграм.\nНажмите меню для выбора дальнейших действий.')

        crud.update_message_db(user_id_class=msg_to_dlt_mistake_1.from_user.id,
                               chat_id_class=msg_to_dlt_mistake_1.chat.id,
                               message_id_class=msg_to_dlt_mistake_1.message_id)

    except (ReadTimeout, TimeoutError) as exception:
        logger.exception(
            'user_id - {0}; тип ошибки - {1}'.format(callback.from_user.id, exception))

        msg_to_dlt_mistake_2: Message = \
            bot.send_message(callback.message.chat.id,
                             text='Ошибка. Время ожидания истекло.\nНажмите меню для выбора дальнейших действий.')

        crud.update_message_db(user_id_class=msg_to_dlt_mistake_2.from_user.id,
                               chat_id_class=msg_to_dlt_mistake_2.chat.id,
                               message_id_class=msg_to_dlt_mistake_2.message_id)

    except (OperationalError, ValueError, KeyError, NameError) as exception:
        logger.exception(
            'user_id - {0}; тип ошибки - {1}'.format(callback.from_user.id, exception))

        msg_to_dlt_mistake_3: Message = \
            bot.send_message(callback.message.chat.id,
                             text='Ошибка доступа к Вашей базе запросов.\nНажмите меню для выбора дальнейших действий.')

        crud.update_message_db(user_id_class=msg_to_dlt_mistake_3.from_user.id,
                               chat_id_class=msg_to_dlt_mistake_3.chat.id,
                               message_id_class=msg_to_dlt_mistake_3.message_id)


@bot.message_handler(state=SearchStates.max_distance_from_center_mile)
def get_max_distance_from_center_mile(message_max_distance_mile: Message) -> None:
    """
    Функция принимает от пользователя расстояние в милях от отеля до центра города, проверяет чтобы это
    значение было числом и не было отрицательным, переводит это значение в километры,
    сохраняет это значение.

    :param message_max_distance_mile: Значение полученное от пользователя
    :type message_max_distance_mile: Message
    """
    try:
        logger.debug('user_id - {0}; вызов - функция get_max_distance_from_center_mile({1})'.
                     format(message_max_distance_mile.from_user.id, message_max_distance_mile))

        crud.update_message_db(user_id_class=message_max_distance_mile.from_user.id,
                               chat_id_class=message_max_distance_mile.chat.id,
                               message_id_class=message_max_distance_mile.message_id)

        crud.delete_message_db(user_id_class=message_max_distance_mile.from_user.id,
                               chat_id_class=message_max_distance_mile.chat.id)

        with bot.retrieve_data(message_max_distance_mile.from_user.id,
                               message_max_distance_mile.chat.id) as \
                data_max_distance_mile:

            if not message_max_distance_mile.text.isdigit():
                logger.warning('user_id - {0}; расстояние {1} в милях не является числом или'
                               ' отрицательное число'.
                               format(message_max_distance_mile.from_user.id,
                                      message_max_distance_mile.text))

                msg_to_dlt_get_max_distance_mil_1: Message = bot.send_message(
                    message_max_distance_mile.chat.id,
                    text=''.join(
                        i_element for i_element in data_max_distance_mile['main_text'].values()))

                crud.update_message_db(user_id_class=msg_to_dlt_get_max_distance_mil_1.from_user.id,
                                       chat_id_class=msg_to_dlt_get_max_distance_mil_1.chat.id,
                                       message_id_class=msg_to_dlt_get_max_distance_mil_1.message_id)

                msg_to_dlt_get_max_distance_mil_2: Message = \
                    bot.send_message(message_max_distance_mile.chat.id,
                                     text='Расстояние {} в милях должно быть числом и'
                                          ' не может быть отрицательным!!!!'
                                          '\nВведите  другое максимальное расстояние от центра города:'.
                                     format(message_max_distance_mile.text))

                crud.update_message_db(user_id_class=msg_to_dlt_get_max_distance_mil_2.from_user.id,
                                       chat_id_class=msg_to_dlt_get_max_distance_mil_2.chat.id,
                                       message_id_class=msg_to_dlt_get_max_distance_mil_2.message_id)

                bot.set_state(message_max_distance_mile.from_user.id,
                              SearchStates.max_distance_from_center_mile,
                              message_max_distance_mile.chat.id)

            else:
                bot.set_state(message_max_distance_mile.from_user.id, SearchStates.hotels,
                              message_max_distance_mile.chat.id)

                result_distance = int(message_max_distance_mile.text) * 1.609344

                data_max_distance_mile['max_distance_from_center'] = str(result_distance)
                data_max_distance_mile['main_text']['max_distance_from_center'] = \
                    '\nМаксимальное расстояние до центра города - {}км.'. \
                    format(data_max_distance_mile['max_distance_from_center'])

                logger.info('user_id - {0}; максимальное расстояние от центра города - {1}км'.
                            format(message_max_distance_mile.from_user.id,
                                   data_max_distance_mile['max_distance_from_center']))

                msg_to_dlt_get_max_distance_mil_3: Message = bot.send_message(
                    message_max_distance_mile.chat.id,
                    text=''.join(
                        i_element for i_element in data_max_distance_mile['main_text'].values()))

                crud.update_message_db(user_id_class=msg_to_dlt_get_max_distance_mil_3.from_user.id,
                                       chat_id_class=msg_to_dlt_get_max_distance_mil_3.chat.id,
                                       message_id_class=msg_to_dlt_get_max_distance_mil_3.message_id)

                msg_to_dlt_get_max_distance_mil_4: Message = bot.send_message(
                    message_max_distance_mile.chat.id,
                    text='Проверьте Ваш запрос.\nВсе верно?',
                    reply_markup=create_yes_no_keyboard(
                        user_id=message_max_distance_mile.from_user.id,
                        callback_data_yes='yes',
                        callback_data_no='no'))

                crud.update_message_db(user_id_class=msg_to_dlt_get_max_distance_mil_4.from_user.id,
                                       chat_id_class=msg_to_dlt_get_max_distance_mil_4.chat.id,
                                       message_id_class=msg_to_dlt_get_max_distance_mil_4.message_id)

    except ApiTelegramException as exception:
        logger.exception(
            'user_id - {0}; тип ошибки - {1}'.format(message_max_distance_mile.from_user.id, exception))

        msg_to_dlt_mistake_1: Message = \
            bot.send_message(message_max_distance_mile.chat.id,
                             text='Ошибка связи с Телеграм.\nНажмите меню для выбора дальнейших действий.')

        crud.update_message_db(user_id_class=msg_to_dlt_mistake_1.from_user.id,
                               chat_id_class=msg_to_dlt_mistake_1.chat.id,
                               message_id_class=msg_to_dlt_mistake_1.message_id)

    except (ReadTimeout, TimeoutError) as exception:
        logger.exception(
            'user_id - {0}; тип ошибки - {1}'.format(message_max_distance_mile.from_user.id, exception))

        msg_to_dlt_mistake_2: Message = \
            bot.send_message(message_max_distance_mile.chat.id,
                             text='Ошибка. Время ожидания истекло.\nНажмите меню для выбора дальнейших действий.')

        crud.update_message_db(user_id_class=msg_to_dlt_mistake_2.from_user.id,
                               chat_id_class=msg_to_dlt_mistake_2.chat.id,
                               message_id_class=msg_to_dlt_mistake_2.message_id)

    except (OperationalError, ValueError, KeyError, NameError) as exception:
        logger.exception(
            'user_id - {0}; тип ошибки - {1}'.format(message_max_distance_mile.from_user.id, exception))

        msg_to_dlt_mistake_3: Message = \
            bot.send_message(message_max_distance_mile.chat.id,
                             text='Ошибка доступа к Вашей базе запросов.\nНажмите меню для выбора дальнейших действий.')

        crud.update_message_db(user_id_class=msg_to_dlt_mistake_3.from_user.id,
                               chat_id_class=msg_to_dlt_mistake_3.chat.id,
                               message_id_class=msg_to_dlt_mistake_3.message_id)


@bot.message_handler(state=SearchStates.max_distance_from_center_km)
def get_max_distance_from_center_km(message_max_distance_km: Message) -> None:
    """
    Функция принимает от пользователя расстояние в километрах от отеля до центра города,
    проверяет чтобы это значение было числом и не было отрицательным, сохраняет это значение.

    :param message_max_distance_km: Значение полученное от пользователя
    :type message_max_distance_km: Message
    """
    try:
        logger.debug('user_id - {0}; вызов - функция get_max_distance_from_center_km({1})'.
                     format(message_max_distance_km.from_user.id, message_max_distance_km))

        crud.update_message_db(user_id_class=message_max_distance_km.from_user.id,
                               chat_id_class=message_max_distance_km.chat.id,
                               message_id_class=message_max_distance_km.message_id)

        crud.delete_message_db(user_id_class=message_max_distance_km.from_user.id,
                               chat_id_class=message_max_distance_km.chat.id)

        with bot.retrieve_data(message_max_distance_km.from_user.id, message_max_distance_km.chat.id) as \
                data_max_distance_km:
            if not message_max_distance_km.text.isdigit():
                logger.warning(
                    'user_id - {0}; расстояние {1}км не является числом или отрицательное число'.
                    format(message_max_distance_km.from_user.id, message_max_distance_km.text))

                msg_to_dlt_get_max_distance_km_1: Message = bot.send_message(
                    message_max_distance_km.chat.id,
                    text=''.join(
                        i_element for i_element in data_max_distance_km['main_text'].values()))

                crud.update_message_db(user_id_class=msg_to_dlt_get_max_distance_km_1.from_user.id,
                                       chat_id_class=msg_to_dlt_get_max_distance_km_1.chat.id,
                                       message_id_class=msg_to_dlt_get_max_distance_km_1.message_id)

                msg_to_dlt_get_max_distance_km_2: Message = \
                    bot.send_message(message_max_distance_km.chat.id,
                                     text='Расстояние {}км должно быть числом и'
                                          ' не может быть отрицательным!!!'
                                          '\nВведите другое максимальное расстояние от центра города:'.
                                     format(message_max_distance_km.text))

                crud.update_message_db(user_id_class=msg_to_dlt_get_max_distance_km_2.from_user.id,
                                       chat_id_class=msg_to_dlt_get_max_distance_km_2.chat.id,
                                       message_id_class=msg_to_dlt_get_max_distance_km_2.message_id)

                bot.set_state(message_max_distance_km.from_user.id,
                              SearchStates.max_distance_from_center_km,
                              message_max_distance_km.chat.id)

            else:
                bot.set_state(message_max_distance_km.from_user.id, SearchStates.hotels,
                              message_max_distance_km.chat.id)

                data_max_distance_km['max_distance_from_center'] = message_max_distance_km.text
                data_max_distance_km['main_text']['max_distance_from_center'] = \
                    '\nМаксимальное расстояние до центра города - {}км.'. \
                    format(data_max_distance_km['max_distance_from_center'])

                logger.info('user_id - {0}; максимальное расстояние от центра города - {1}км'.
                            format(message_max_distance_km.from_user.id,
                                   data_max_distance_km['max_distance_from_center']))

                msg_to_dlt_get_max_distance_km_3: Message = bot.send_message(
                    message_max_distance_km.chat.id,
                    text=''.join(
                        i_element for i_element in data_max_distance_km['main_text'].values()))

                crud.update_message_db(user_id_class=msg_to_dlt_get_max_distance_km_3.from_user.id,
                                       chat_id_class=msg_to_dlt_get_max_distance_km_3.chat.id,
                                       message_id_class=msg_to_dlt_get_max_distance_km_3.message_id)

                msg_to_dlt_get_max_distance_km_4: Message = bot.send_message(
                    message_max_distance_km.chat.id,
                    text='Проверьте Ваш запрос.\nВсе верно?',
                    reply_markup=create_yes_no_keyboard(
                        user_id=message_max_distance_km.from_user.id,
                        callback_data_yes='yes',
                        callback_data_no='no'))

                crud.update_message_db(user_id_class=msg_to_dlt_get_max_distance_km_4.from_user.id,
                                       chat_id_class=msg_to_dlt_get_max_distance_km_4.chat.id,
                                       message_id_class=msg_to_dlt_get_max_distance_km_4.message_id)

    except ApiTelegramException as exception:
        logger.exception(
            'user_id - {0}; тип ошибки - {1}'.format(message_max_distance_km.from_user.id, exception))

        msg_to_dlt_mistake_1: Message = \
            bot.send_message(message_max_distance_km.chat.id,
                             text='Ошибка связи с Телеграм.\nНажмите меню для выбора дальнейших действий.')

        crud.update_message_db(user_id_class=msg_to_dlt_mistake_1.from_user.id,
                               chat_id_class=msg_to_dlt_mistake_1.chat.id,
                               message_id_class=msg_to_dlt_mistake_1.message_id)

    except (ReadTimeout, TimeoutError) as exception:
        logger.exception(
            'user_id - {0}; тип ошибки - {1}'.format(message_max_distance_km.from_user.id, exception))

        msg_to_dlt_mistake_2: Message = \
            bot.send_message(message_max_distance_km.chat.id,
                             text='Ошибка. Время ожидания истекло.\nНажмите меню для выбора дальнейших действий.')

        crud.update_message_db(user_id_class=msg_to_dlt_mistake_2.from_user.id,
                               chat_id_class=msg_to_dlt_mistake_2.chat.id,
                               message_id_class=msg_to_dlt_mistake_2.message_id)

    except (OperationalError, ValueError, KeyError, NameError) as exception:
        logger.exception(
            'user_id - {0}; тип ошибки - {1}'.format(message_max_distance_km.from_user.id, exception))

        msg_to_dlt_mistake_3: Message = \
            bot.send_message(message_max_distance_km.chat.id,
                             text='Ошибка доступа к Вашей базе запросов.\nНажмите меню для выбора дальнейших действий.')

        crud.update_message_db(user_id_class=msg_to_dlt_mistake_3.from_user.id,
                               chat_id_class=msg_to_dlt_mistake_3.chat.id,
                               message_id_class=msg_to_dlt_mistake_3.message_id)


@bot.callback_query_handler(func=None, state=SearchStates.max_distance_from_center)
def get_max_distance_from_center(callback: CallbackQuery) -> None:
    """
    Функция обрабатывает результат работы клавиатуры km_mile_keyboard.

    :param callback: входящий запрос обратного вызова с кнопки клавиатуры km_mile_keyboard
    :type callback: CallbackQuery
    """
    try:
        logger.info('user_id - {0}; callback.data - {1}'.format(callback.from_user.id, callback.data))

        logger.debug('user_id - {0}; вызов - функция get_max_distance_from_center({1})'.
                     format(callback.from_user.id, callback))

        crud.delete_message_db(user_id_class=callback.from_user.id,
                               chat_id_class=callback.message.chat.id)

        with bot.retrieve_data(callback.from_user.id, callback.message.chat.id) \
                as data_max_distance_from_center:

            if callback.data == 'km':
                bot.set_state(callback.from_user.id,
                              SearchStates.max_distance_from_center_km,
                              callback.message.chat.id)

                msg_to_dlt_get_max_distance_1: Message = bot.send_message(
                    callback.message.chat.id,
                    text=''.join(i_element for i_element in data_max_distance_from_center['main_text'].values()))

                crud.update_message_db(user_id_class=msg_to_dlt_get_max_distance_1.from_user.id,
                                       chat_id_class=msg_to_dlt_get_max_distance_1.chat.id,
                                       message_id_class=msg_to_dlt_get_max_distance_1.message_id)

                msg_to_dlt_get_max_distance_2: Message = \
                    bot.send_message(callback.message.chat.id,
                                     text='Введите максимальное расстояние в км от центра города:')

                crud.update_message_db(user_id_class=msg_to_dlt_get_max_distance_2.from_user.id,
                                       chat_id_class=msg_to_dlt_get_max_distance_2.chat.id,
                                       message_id_class=msg_to_dlt_get_max_distance_2.message_id)

            elif callback.data == 'mile':

                bot.set_state(callback.from_user.id,
                              SearchStates.max_distance_from_center_mile,
                              callback.message.chat.id)

                msg_to_dlt_get_max_distance_3: Message = bot.send_message(
                    callback.message.chat.id,
                    text=''.join(i_element for i_element in data_max_distance_from_center['main_text'].values()))

                crud.update_message_db(user_id_class=msg_to_dlt_get_max_distance_3.from_user.id,
                                       chat_id_class=msg_to_dlt_get_max_distance_3.chat.id,
                                       message_id_class=msg_to_dlt_get_max_distance_3.message_id)

                msg_to_dlt_get_max_distance_4: Message = \
                    bot.send_message(callback.message.chat.id,
                                     text='Введите максимальное расстояние от центра города в милях:')

                crud.update_message_db(user_id_class=msg_to_dlt_get_max_distance_4.from_user.id,
                                       chat_id_class=msg_to_dlt_get_max_distance_4.chat.id,
                                       message_id_class=msg_to_dlt_get_max_distance_4.message_id)

    except ApiTelegramException as exception:
        logger.exception(
            'user_id - {0}; тип ошибки - {1}'.format(callback.from_user.id, exception))

        msg_to_dlt_mistake_1: Message = \
            bot.send_message(callback.message.chat.id,
                             text='Ошибка связи с Телеграм.\nНажмите меню для выбора дальнейших действий.')

        crud.update_message_db(user_id_class=msg_to_dlt_mistake_1.from_user.id,
                               chat_id_class=msg_to_dlt_mistake_1.chat.id,
                               message_id_class=msg_to_dlt_mistake_1.message_id)

    except (ReadTimeout, TimeoutError) as exception:
        logger.exception(
            'user_id - {0}; тип ошибки - {1}'.format(callback.from_user.id, exception))

        msg_to_dlt_mistake_2: Message = \
            bot.send_message(callback.message.chat.id,
                             text='Ошибка. Время ожидания истекло.\nНажмите меню для выбора дальнейших действий.')

        crud.update_message_db(user_id_class=msg_to_dlt_mistake_2.from_user.id,
                               chat_id_class=msg_to_dlt_mistake_2.chat.id,
                               message_id_class=msg_to_dlt_mistake_2.message_id)

    except (OperationalError, ValueError, KeyError, NameError) as exception:
        logger.exception(
            'user_id - {0}; тип ошибки - {1}'.format(callback.from_user.id, exception))

        msg_to_dlt_mistake_3: Message = \
            bot.send_message(callback.message.chat.id,
                             text='Ошибка доступа к Вашей базе запросов.\nНажмите меню для выбора дальнейших действий.')

        crud.update_message_db(user_id_class=msg_to_dlt_mistake_3.from_user.id,
                               chat_id_class=msg_to_dlt_mistake_3.chat.id,
                               message_id_class=msg_to_dlt_mistake_3.message_id)


@bot.message_handler(state=SearchStates.single_child_age_rewrite)
def get_rewrite_single_child_age(message: Message) -> None:
    """
    Функция принимает возраст каждого ребенка в зависимости от количества детей.

    :param message: Сообщение с возрастом ребенка полученное от пользователя
    :type message: Message
    """
    try:
        logger.debug('user_id - {0}; вызов - функция get_child_age({1})'.
                     format(message.from_user.id,
                            message))

        crud.update_message_db(user_id_class=message.from_user.id,
                               chat_id_class=message.chat.id,
                               message_id_class=message.message_id)

        crud.delete_message_db(user_id_class=message.from_user.id,
                               chat_id_class=message.chat.id)

        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            if not message.text.isdigit():
                logger.warning(
                    'user_id - {0}; возраст {1} не является целым числом или отрицательное число'.
                    format(message.from_user.id,
                           message.text))

                msg_to_dlt_get_rewrite_child_age_1: Message = bot.send_message(
                    message.chat.id,
                    text=''.join(i_element for i_element in
                                 data['main_text'].values()))

                crud.update_message_db(user_id_class=msg_to_dlt_get_rewrite_child_age_1.from_user.id,
                                       chat_id_class=msg_to_dlt_get_rewrite_child_age_1.chat.id,
                                       message_id_class=msg_to_dlt_get_rewrite_child_age_1.message_id)

                msg_to_dlt_get_rewrite_child_age_2: Message = bot.send_message(
                    message.chat.id,
                    text='Возраст {0} должно быть целым числом и'
                         ' не может быть отрицательным!!!'
                         '\nВведите другой возраст {1}-го ребенка:'.
                    format(message.text,
                           data['child_number']))

                crud.update_message_db(user_id_class=msg_to_dlt_get_rewrite_child_age_2.from_user.id,
                                       chat_id_class=msg_to_dlt_get_rewrite_child_age_2.chat.id,
                                       message_id_class=msg_to_dlt_get_rewrite_child_age_2.message_id)

                bot.set_state(message.from_user.id,
                              SearchStates.single_child_age_rewrite,
                              message.chat.id)

            elif int(message.text) > 18:

                msg_to_dlt_get_rewrite_child_age_3: Message = bot.send_message(
                    message.chat.id,
                    text=''.join(i_element for i_element in
                                 data['main_text'].values()))

                crud.update_message_db(user_id_class=msg_to_dlt_get_rewrite_child_age_3.from_user.id,
                                       chat_id_class=msg_to_dlt_get_rewrite_child_age_3.chat.id,
                                       message_id_class=msg_to_dlt_get_rewrite_child_age_3.message_id)

                msg_to_dlt_get_rewrite_child_age_4: Message = bot.send_message(
                    message.chat.id,
                    text='Возраст {0} должен быть меньше 18!!!'
                         '\nВведите другой возраст {1}-го ребенка:'.
                    format(message.text,
                           data['child_number']))

                crud.update_message_db(user_id_class=msg_to_dlt_get_rewrite_child_age_4.from_user.id,
                                       chat_id_class=msg_to_dlt_get_rewrite_child_age_4.chat.id,
                                       message_id_class=msg_to_dlt_get_rewrite_child_age_4.message_id)

                bot.set_state(message.from_user.id,
                              SearchStates.single_child_age_rewrite,
                              message.chat.id)

            else:
                data['main_text'].pop('{}_child_age'.format(data['child_number']))

                data['children_ages'][int(data['child_number']) - 1]['age'] = int(message.text)

                data['main_text']['{}_child_age'.format(data['child_number'])] = \
                    '\nВозраст {0}-го ребенка - {1}'.format(data['child_number'], message.text)

                msg_to_dlt_get_rewrite_child_age_5: Message = bot.send_message(
                    message.chat.id,
                    text=''.join(i_element for i_element in
                                 data['main_text'].values()))

                crud.update_message_db(user_id_class=msg_to_dlt_get_rewrite_child_age_5.from_user.id,
                                       chat_id_class=msg_to_dlt_get_rewrite_child_age_5.chat.id,
                                       message_id_class=msg_to_dlt_get_rewrite_child_age_5.message_id)

                bot.set_state(message.from_user.id,
                              SearchStates.hotels,
                              message.chat.id)

                logger.info('user_id - {0}; список возрастов детей - {1}'.
                            format(message.from_user.id,
                                   data['children_quantity']))

                msg_to_dlt_get_rewrite_child_age_6: Message = bot.send_message(message.chat.id,
                                                                               text='Проверьте Ваш запрос.\nВсе верно?',
                                                                               reply_markup=create_yes_no_keyboard(
                                                                                   user_id=message.from_user.id,
                                                                                   callback_data_yes='yes',
                                                                                   callback_data_no='no'))

                crud.update_message_db(user_id_class=msg_to_dlt_get_rewrite_child_age_6.from_user.id,
                                       chat_id_class=msg_to_dlt_get_rewrite_child_age_6.chat.id,
                                       message_id_class=msg_to_dlt_get_rewrite_child_age_6.message_id)

    except ApiTelegramException as exception:
        logger.exception(
            'user_id - {0}; тип ошибки - {1}'.format(message.from_user.id, exception))

        msg_to_dlt_mistake_1: Message = \
            bot.send_message(message.chat.id,
                             text='Ошибка связи с Телеграм.\nНажмите меню для выбора дальнейших действий.')

        crud.update_message_db(user_id_class=msg_to_dlt_mistake_1.from_user.id,
                               chat_id_class=msg_to_dlt_mistake_1.chat.id,
                               message_id_class=msg_to_dlt_mistake_1.message_id)

    except (ReadTimeout, TimeoutError) as exception:
        logger.exception(
            'user_id - {0}; тип ошибки - {1}'.format(message.from_user.id, exception))

        msg_to_dlt_mistake_2: Message = \
            bot.send_message(message.chat.id,
                             text='Ошибка. Время ожидания истекло.\nНажмите меню для выбора дальнейших действий.')

        crud.update_message_db(user_id_class=msg_to_dlt_mistake_2.from_user.id,
                               chat_id_class=msg_to_dlt_mistake_2.chat.id,
                               message_id_class=msg_to_dlt_mistake_2.message_id)

    except (OperationalError, ValueError, KeyError, NameError) as exception:
        logger.exception(
            'user_id - {0}; тип ошибки - {1}'.format(message.from_user.id, exception))

        msg_to_dlt_mistake_3: Message = \
            bot.send_message(message.chat.id,
                             text='Ошибка доступа к Вашей базе запросов.\nНажмите меню для выбора дальнейших действий.')

        crud.update_message_db(user_id_class=msg_to_dlt_mistake_3.from_user.id,
                               chat_id_class=msg_to_dlt_mistake_3.chat.id,
                               message_id_class=msg_to_dlt_mistake_3.message_id)


@bot.message_handler(state=SearchStates.child_age_rewrite)
def get_rewrite_child_age(message_get_rewrite_child_age: Message) -> None:
    """
    Функция принимает возраст каждого ребенка в зависимости от количества детей.

    :param message_get_rewrite_child_age: Сообщение с возрастом ребенка полученное от пользователя
    :type message_get_rewrite_child_age: Message
    """
    try:
        logger.debug('user_id - {0}; вызов - функция get_child_age({1})'.
                     format(message_get_rewrite_child_age.from_user.id,
                            message_get_rewrite_child_age))

        crud.update_message_db(user_id_class=message_get_rewrite_child_age.from_user.id,
                               chat_id_class=message_get_rewrite_child_age.chat.id,
                               message_id_class=message_get_rewrite_child_age.message_id)

        crud.delete_message_db(user_id_class=message_get_rewrite_child_age.from_user.id,
                               chat_id_class=message_get_rewrite_child_age.chat.id)

        with bot.retrieve_data(message_get_rewrite_child_age.from_user.id,
                               message_get_rewrite_child_age.chat.id) as data_get_rewrite_child_age:

            if not message_get_rewrite_child_age.text.isdigit():
                logger.warning(
                    'user_id - {0}; возраст {1} не является целым числом или отрицательное число'.
                    format(message_get_rewrite_child_age.from_user.id,
                           message_get_rewrite_child_age.text))

                msg_to_dlt_get_rewrite_child_age_1: Message = bot.send_message(
                    message_get_rewrite_child_age.chat.id,
                    text=''.join(i_element for i_element in
                                 data_get_rewrite_child_age['main_text'].values()))

                crud.update_message_db(
                    user_id_class=msg_to_dlt_get_rewrite_child_age_1.from_user.id,
                    chat_id_class=msg_to_dlt_get_rewrite_child_age_1.chat.id,
                    message_id_class=msg_to_dlt_get_rewrite_child_age_1.message_id)

                msg_to_dlt_get_rewrite_child_age_2: Message = bot.send_message(
                    message_get_rewrite_child_age.from_user.id,
                    text='Возраст {0} должно быть целым числом и'
                         ' не может быть отрицательным!!!'
                         '\nВведите другой возраст {1}-го ребенка:'.
                    format(message_get_rewrite_child_age.text,
                           data_get_rewrite_child_age['children_quantity_in_process'] + 1))

                crud.update_message_db(
                    user_id_class=msg_to_dlt_get_rewrite_child_age_2.from_user.id,
                    chat_id_class=msg_to_dlt_get_rewrite_child_age_2.chat.id,
                    message_id_class=msg_to_dlt_get_rewrite_child_age_2.message_id)

                bot.set_state(message_get_rewrite_child_age.from_user.id,
                              SearchStates.child_age_rewrite,
                              message_get_rewrite_child_age.chat.id)

            elif int(message_get_rewrite_child_age.text) > 18:

                msg_to_dlt_get_rewrite_child_age_3: Message = bot.send_message(
                    message_get_rewrite_child_age.chat.id,
                    text=''.join(i_element for i_element in
                                 data_get_rewrite_child_age['main_text'].values()))

                crud.update_message_db(
                    user_id_class=msg_to_dlt_get_rewrite_child_age_3.from_user.id,
                    chat_id_class=msg_to_dlt_get_rewrite_child_age_3.chat.id,
                    message_id_class=msg_to_dlt_get_rewrite_child_age_3.message_id)

                msg_to_dlt_get_rewrite_child_age_4: Message = bot.send_message(
                    message_get_rewrite_child_age.chat.id,
                    text='Возраст {0} должен быть меньше 18!!!'
                         '\nВведите другой возраст {1}-го ребенка:'.
                    format(message_get_rewrite_child_age.text,
                           data_get_rewrite_child_age['children_quantity_in_process'] + 1))

                crud.update_message_db(
                    user_id_class=msg_to_dlt_get_rewrite_child_age_4.from_user.id,
                    chat_id_class=msg_to_dlt_get_rewrite_child_age_4.chat.id,
                    message_id_class=msg_to_dlt_get_rewrite_child_age_4.message_id)

                bot.set_state(message_get_rewrite_child_age.from_user.id,
                              SearchStates.child_age_rewrite,
                              message_get_rewrite_child_age.chat.id)

            else:
                data_get_rewrite_child_age['children_ages'].append(
                    {'age': int(message_get_rewrite_child_age.text)})

                data_get_rewrite_child_age['children_quantity_in_process'] += 1

                data_get_rewrite_child_age['main_text']['{}_child_age'.format(
                    data_get_rewrite_child_age['children_quantity_in_process'])] = '\nВозраст {0}-го ребенка - {1}'. \
                    format(data_get_rewrite_child_age['children_quantity_in_process'],
                           message_get_rewrite_child_age.text)

                msg_to_dlt_get_rewrite_child_age_5: Message = bot.send_message(
                    message_get_rewrite_child_age.chat.id,
                    text=''.join(i_element for i_element in
                                 data_get_rewrite_child_age['main_text'].values()))

                crud.update_message_db(
                    user_id_class=msg_to_dlt_get_rewrite_child_age_5.from_user.id,
                    chat_id_class=msg_to_dlt_get_rewrite_child_age_5.chat.id,
                    message_id_class=msg_to_dlt_get_rewrite_child_age_5.message_id)

                if data_get_rewrite_child_age['children_quantity_in_process'] < int(
                        data_get_rewrite_child_age['children_quantity']):

                    msg_to_dlt_get_rewrite_child_age_6: Message = bot.send_message(
                        message_get_rewrite_child_age.chat.id,
                        text='Введите возраст {}-го ребенка'.
                        format(
                            data_get_rewrite_child_age['children_quantity_in_process'] + 1))

                    crud.update_message_db(
                        user_id_class=msg_to_dlt_get_rewrite_child_age_6.from_user.id,
                        chat_id_class=msg_to_dlt_get_rewrite_child_age_6.chat.id,
                        message_id_class=msg_to_dlt_get_rewrite_child_age_6.message_id)

                    bot.set_state(message_get_rewrite_child_age.from_user.id,
                                  SearchStates.child_age_rewrite,
                                  message_get_rewrite_child_age.chat.id)

                else:

                    bot.set_state(message_get_rewrite_child_age.from_user.id,
                                  SearchStates.hotels,
                                  message_get_rewrite_child_age.chat.id)

                    logger.info('user_id - {0}; список возрастов детей - {1}'.
                                format(message_get_rewrite_child_age.from_user.id,
                                       data_get_rewrite_child_age['children_quantity']))

                    msg_to_dlt_get_rewrite_child_age_7: Message = bot.send_message(
                        message_get_rewrite_child_age.chat.id,
                        text='Проверьте Ваш запрос.\nВсе верно?',
                        reply_markup=create_yes_no_keyboard(
                            user_id=message_get_rewrite_child_age.from_user.id,
                            callback_data_yes='yes',
                            callback_data_no='no'))

                    crud.update_message_db(
                        user_id_class=msg_to_dlt_get_rewrite_child_age_7.from_user.id,
                        chat_id_class=msg_to_dlt_get_rewrite_child_age_7.chat.id,
                        message_id_class=msg_to_dlt_get_rewrite_child_age_7.message_id)

    except ApiTelegramException as exception:
        logger.exception(
            'user_id - {0}; тип ошибки - {1}'.format(message_get_rewrite_child_age.from_user.id, exception))

        msg_to_dlt_mistake_1: Message = \
            bot.send_message(message_get_rewrite_child_age.chat.id,
                             text='Ошибка связи с Телеграм.\nНажмите меню для выбора дальнейших действий.')

        crud.update_message_db(user_id_class=msg_to_dlt_mistake_1.from_user.id,
                               chat_id_class=msg_to_dlt_mistake_1.chat.id,
                               message_id_class=msg_to_dlt_mistake_1.message_id)

    except (ReadTimeout, TimeoutError) as exception:
        logger.exception(
            'user_id - {0}; тип ошибки - {1}'.format(message_get_rewrite_child_age.from_user.id, exception))

        msg_to_dlt_mistake_2: Message = \
            bot.send_message(message_get_rewrite_child_age.chat.id,
                             text='Ошибка. Время ожидания истекло.\nНажмите меню для выбора дальнейших действий.')

        crud.update_message_db(user_id_class=msg_to_dlt_mistake_2.from_user.id,
                               chat_id_class=msg_to_dlt_mistake_2.chat.id,
                               message_id_class=msg_to_dlt_mistake_2.message_id)

    except (OperationalError, ValueError, KeyError, NameError) as exception:
        logger.exception(
            'user_id - {0}; тип ошибки - {1}'.format(message_get_rewrite_child_age.from_user.id, exception))

        msg_to_dlt_mistake_3: Message = \
            bot.send_message(message_get_rewrite_child_age.chat.id,
                             text='Ошибка доступа к Вашей базе запросов.\nНажмите меню для выбора дальнейших действий.')

        crud.update_message_db(user_id_class=msg_to_dlt_mistake_3.from_user.id,
                               chat_id_class=msg_to_dlt_mistake_3.chat.id,
                               message_id_class=msg_to_dlt_mistake_3.message_id)


@bot.message_handler(state=SearchStates.children_quantity_rewrite)
def get_rewrite_children_quantity(message: Message) -> None:
    """
    Функция принимает и обрабатывает измененное значение количества детей.

    :param message: Сообщение с количеством детей полученное от пользователя
    :type message: Message
    """
    try:
        logger.debug('user_id - {0}; вызов - функция get_rewrite_children_quantity({1})'.
                     format(message.from_user.id, message))

        crud.update_message_db(user_id_class=message.from_user.id,
                               chat_id_class=message.chat.id,
                               message_id_class=message.message_id)

        crud.delete_message_db(user_id_class=message.from_user.id,
                               chat_id_class=message.chat.id)

        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            if not message.text.isdigit():
                logger.warning(
                    'user_id - {0}; количество детей {1} не является целым числом или отрицательное число'.
                    format(message.from_user.id, message.text))

                msg_to_dlt_get_rewrite_children_quantity_1: Message = bot.send_message(
                    message.chat.id, text=''.join(i_element for i_element in data['main_text'].values()))

                crud.update_message_db(user_id_class=msg_to_dlt_get_rewrite_children_quantity_1.from_user.id,
                                       chat_id_class=msg_to_dlt_get_rewrite_children_quantity_1.chat.id,
                                       message_id_class=msg_to_dlt_get_rewrite_children_quantity_1.message_id)

                msg_to_dlt_get_rewrite_children_quantity_2: Message = bot.send_message(
                    message.chat.id, text='Количество детей {} должно быть целым числом и'
                                          ' не может быть отрицательным!!!'
                                          '\nВведите другое количество детей:'.
                    format(message.text))

                crud.update_message_db(user_id_class=msg_to_dlt_get_rewrite_children_quantity_2.from_user.id,
                                       chat_id_class=msg_to_dlt_get_rewrite_children_quantity_2.chat.id,
                                       message_id_class=msg_to_dlt_get_rewrite_children_quantity_2.message_id)

                bot.set_state(message.from_user.id, SearchStates.children_quantity_rewrite,
                              message.chat.id)

            else:
                data['children_quantity_in_process'] = 0

                data['children_ages'] = []

                result_keys = [j_key for j_key in data['main_text'].keys() if j_key.endswith('child_age')]
                for i_key in result_keys:
                    data['main_text'].pop(i_key, None)

                data['children_quantity'] = message.text
                data['main_text']['children_quantity'] = '\nКоличество детей - {}'.format(data['children_quantity'])

                logger.info('user_id - {0}; количество детей - {1}'.
                            format(message.from_user.id, data['children_quantity']))

                if data['children_quantity_in_process'] < int(data['children_quantity']):
                    bot.set_state(message.from_user.id, SearchStates.child_age_rewrite,
                                  message.chat.id)

                    msg_to_dlt_get_rewrite_children_quantity_3: Message = bot.send_message(
                        message.chat.id, text=''.join(i_element for i_element in data['main_text'].values()))

                    crud.update_message_db(user_id_class=msg_to_dlt_get_rewrite_children_quantity_3.from_user.id,
                                           chat_id_class=msg_to_dlt_get_rewrite_children_quantity_3.chat.id,
                                           message_id_class=msg_to_dlt_get_rewrite_children_quantity_3.message_id)

                    msg_to_dlt_get_rewrite_children_quantity_4: Message = bot.send_message(
                        message.chat.id, text='Введите возраст {}-го ребенка:'
                        .format(data['children_quantity_in_process'] + 1))

                    crud.update_message_db(user_id_class=msg_to_dlt_get_rewrite_children_quantity_4.from_user.id,
                                           chat_id_class=msg_to_dlt_get_rewrite_children_quantity_4.chat.id,
                                           message_id_class=msg_to_dlt_get_rewrite_children_quantity_4.message_id)

                else:
                    bot.set_state(message.from_user.id, SearchStates.hotels,
                                  message.chat.id)

                    msg_to_dlt_get_rewrite_children_quantity_5: Message = bot.send_message(
                        message.chat.id, text=''.join(i_element for i_element in data['main_text'].values()))

                    crud.update_message_db(user_id_class=msg_to_dlt_get_rewrite_children_quantity_5.from_user.id,
                                           chat_id_class=msg_to_dlt_get_rewrite_children_quantity_5.chat.id,
                                           message_id_class=msg_to_dlt_get_rewrite_children_quantity_5.message_id)

                    data['children_ages'] = []

                    logger.info('user_id - {0}; список возрастов детей - {1}'.
                                format(message.from_user.id, data['children_quantity']))

                    msg_to_dlt_get_rewrite_child_age_6: Message =\
                        bot.send_message(message.chat.id,
                                         text='Проверьте Ваш запрос.\nВсе верно?',
                                         reply_markup=create_yes_no_keyboard(user_id=message.from_user.id,
                                                                             callback_data_yes='yes',
                                                                             callback_data_no='no'))

                    crud.update_message_db(user_id_class=msg_to_dlt_get_rewrite_child_age_6.from_user.id,
                                           chat_id_class=msg_to_dlt_get_rewrite_child_age_6.chat.id,
                                           message_id_class=msg_to_dlt_get_rewrite_child_age_6.message_id)

    except ApiTelegramException as exception:
        logger.exception(
            'user_id - {0}; тип ошибки - {1}'.format(message.from_user.id, exception))

        msg_to_dlt_mistake_1: Message = \
            bot.send_message(message.chat.id,
                             text='Ошибка связи с Телеграм.\nНажмите меню для выбора дальнейших действий.')

        crud.update_message_db(user_id_class=msg_to_dlt_mistake_1.from_user.id,
                               chat_id_class=msg_to_dlt_mistake_1.chat.id,
                               message_id_class=msg_to_dlt_mistake_1.message_id)

    except (ReadTimeout, TimeoutError) as exception:
        logger.exception(
            'user_id - {0}; тип ошибки - {1}'.format(message.from_user.id, exception))

        msg_to_dlt_mistake_2: Message = \
            bot.send_message(message.chat.id,
                             text='Ошибка. Время ожидания истекло.\nНажмите меню для выбора дальнейших действий.')

        crud.update_message_db(user_id_class=msg_to_dlt_mistake_2.from_user.id,
                               chat_id_class=msg_to_dlt_mistake_2.chat.id,
                               message_id_class=msg_to_dlt_mistake_2.message_id)

    except (OperationalError, ValueError, KeyError, NameError) as exception:
        logger.exception(
            'user_id - {0}; тип ошибки - {1}'.format(message.from_user.id, exception))

        msg_to_dlt_mistake_3: Message = \
            bot.send_message(message.chat.id,
                             text='Ошибка доступа к Вашей базе запросов.\nНажмите меню для выбора дальнейших действий.')

        crud.update_message_db(user_id_class=msg_to_dlt_mistake_3.from_user.id,
                               chat_id_class=msg_to_dlt_mistake_3.chat.id,
                               message_id_class=msg_to_dlt_mistake_3.message_id)


@bot.message_handler(state=SearchStates.child_age)
def get_child_age(message_get_child_age: Message) -> None:
    """
    Функция запрашивает возраст каждого ребенка в зависимости от количества детей.

    :param message_get_child_age: Сообщение с возрастом ребенка полученное от пользователя
    :type message_get_child_age: Message
    """
    try:
        logger.debug('user_id - {0}; вызов - функция get_child_age({1})'.
                     format(message_get_child_age.from_user.id, message_get_child_age))

        crud.update_message_db(user_id_class=message_get_child_age.from_user.id,
                               chat_id_class=message_get_child_age.chat.id,
                               message_id_class=message_get_child_age.message_id)

        crud.delete_message_db(user_id_class=message_get_child_age.from_user.id,
                               chat_id_class=message_get_child_age.chat.id)

        with bot.retrieve_data(message_get_child_age.from_user.id,
                               message_get_child_age.chat.id) as data_get_child_age:
            if not message_get_child_age.text.isdigit():
                logger.warning(
                    'user_id - {0}; возраст {1} не является целым числом или отрицательное число'.
                    format(message_get_child_age.from_user.id, message_get_child_age.text))

                msg_to_dlt_get_child_age_1: Message = bot.send_message(
                    message_get_child_age.chat.id,
                    text=''.join(
                        i_element for i_element in data_get_child_age['main_text'].values()))

                crud.update_message_db(user_id_class=msg_to_dlt_get_child_age_1.from_user.id,
                                       chat_id_class=msg_to_dlt_get_child_age_1.chat.id,
                                       message_id_class=msg_to_dlt_get_child_age_1.message_id)

                msg_to_dlt_get_child_age_2: Message = bot.send_message(
                    message_get_child_age.chat.id,
                    text='Возраст {0} должно быть целым числом и'
                         ' не может быть отрицательным!!!'
                         '\nВведите другой возраст {1}-го ребенка:'.
                    format(message_get_child_age.text,
                           data_get_child_age['children_quantity_in_process'] + 1))

                crud.update_message_db(user_id_class=msg_to_dlt_get_child_age_2.from_user.id,
                                       chat_id_class=msg_to_dlt_get_child_age_2.chat.id,
                                       message_id_class=msg_to_dlt_get_child_age_2.message_id)

                bot.set_state(message_get_child_age.from_user.id, SearchStates.child_age,
                              message_get_child_age.chat.id)

            elif int(message_get_child_age.text) > 18:

                msg_to_dlt_get_child_age_3: Message = bot.send_message(
                    message_get_child_age.chat.id,
                    text=''.join(
                        i_element for i_element in data_get_child_age['main_text'].values()))

                crud.update_message_db(user_id_class=msg_to_dlt_get_child_age_3.from_user.id,
                                       chat_id_class=msg_to_dlt_get_child_age_3.chat.id,
                                       message_id_class=msg_to_dlt_get_child_age_3.message_id)

                msg_to_dlt_get_child_age_4: Message = bot.send_message(
                    message_get_child_age.chat.id, text='Возраст {0} должен быть меньше 18!!!'
                                                        '\nВведите другой возраст {1}-го ребенка:'.
                    format(message_get_child_age.text,
                           data_get_child_age['children_quantity_in_process'] + 1))

                crud.update_message_db(user_id_class=msg_to_dlt_get_child_age_4.from_user.id,
                                       chat_id_class=msg_to_dlt_get_child_age_4.chat.id,
                                       message_id_class=msg_to_dlt_get_child_age_4.message_id)

                bot.set_state(message_get_child_age.from_user.id, SearchStates.child_age,
                              message_get_child_age.chat.id)

            else:
                data_get_child_age['children_ages'].append({'age': int(message_get_child_age.text)})

                data_get_child_age['children_quantity_in_process'] += 1

                data_get_child_age['main_text'][
                    '{}_child_age'.format(data_get_child_age['children_quantity_in_process'])] = \
                    '\nВозраст {0}-го ребенка - {1}'.format(data_get_child_age['children_quantity_in_process'],
                                                            message_get_child_age.text)

                msg_to_dlt_get_child_age_5: Message = bot.send_message(
                    message_get_child_age.chat.id,
                    text=''.join(
                        i_element for i_element in data_get_child_age['main_text'].values()))

                crud.update_message_db(user_id_class=msg_to_dlt_get_child_age_5.from_user.id,
                                       chat_id_class=msg_to_dlt_get_child_age_5.chat.id,
                                       message_id_class=msg_to_dlt_get_child_age_5.message_id)

                if data_get_child_age['children_quantity_in_process'] < int(
                        data_get_child_age['children_quantity']):

                    msg_to_dlt_get_child_age_6: Message = bot.send_message(
                        message_get_child_age.chat.id,
                        text='Введите возраст {}-го ребенка'.
                        format(data_get_child_age['children_quantity_in_process'] + 1))

                    crud.update_message_db(user_id_class=msg_to_dlt_get_child_age_6.from_user.id,
                                           chat_id_class=msg_to_dlt_get_child_age_6.chat.id,
                                           message_id_class=msg_to_dlt_get_child_age_6.message_id)

                    bot.set_state(message_get_child_age.from_user.id, SearchStates.child_age,
                                  message_get_child_age.chat.id)

                else:

                    bot.set_state(message_get_child_age.from_user.id,
                                  SearchStates.max_distance_from_center,
                                  message_get_child_age.chat.id)

                    logger.info('user_id - {0}; список возрастов детей - {1}'.
                                format(message_get_child_age.from_user.id,
                                       data_get_child_age['children_quantity']))

                    create_km_mile_keyboard(message_get_child_age.from_user.id,
                                            message_get_child_age.chat.id)

    except ApiTelegramException as exception:
        logger.exception(
            'user_id - {0}; тип ошибки - {1}'.format(message_get_child_age.from_user.id, exception))

        msg_to_dlt_mistake_1: Message = \
            bot.send_message(message_get_child_age.chat.id,
                             text='Ошибка связи с Телеграм.\nНажмите меню для выбора дальнейших действий.')

        crud.update_message_db(user_id_class=msg_to_dlt_mistake_1.from_user.id,
                               chat_id_class=msg_to_dlt_mistake_1.chat.id,
                               message_id_class=msg_to_dlt_mistake_1.message_id)

    except (ReadTimeout, TimeoutError) as exception:
        logger.exception(
            'user_id - {0}; тип ошибки - {1}'.format(message_get_child_age.from_user.id, exception))

        msg_to_dlt_mistake_2: Message = \
            bot.send_message(message_get_child_age.chat.id,
                             text='Ошибка. Время ожидания истекло.\nНажмите меню для выбора дальнейших действий.')

        crud.update_message_db(user_id_class=msg_to_dlt_mistake_2.from_user.id,
                               chat_id_class=msg_to_dlt_mistake_2.chat.id,
                               message_id_class=msg_to_dlt_mistake_2.message_id)

    except (OperationalError, ValueError, KeyError, NameError) as exception:
        logger.exception(
            'user_id - {0}; тип ошибки - {1}'.format(message_get_child_age.from_user.id, exception))

        msg_to_dlt_mistake_3: Message = \
            bot.send_message(message_get_child_age.chat.id,
                             text='Ошибка доступа к Вашей базе запросов.\nНажмите меню для выбора дальнейших действий.')

        crud.update_message_db(user_id_class=msg_to_dlt_mistake_3.from_user.id,
                               chat_id_class=msg_to_dlt_mistake_3.chat.id,
                               message_id_class=msg_to_dlt_mistake_3.message_id)


@bot.message_handler(state=SearchStates.children_quantity)
def get_children_quantity(message: Message) -> None:
    """
    Функция принимает и обрабатывает значение количества детей.

    :param message: Сообщение с количеством детей полученное от пользователя
    :type message: Message
    """
    try:
        logger.debug('user_id - {0}; вызов - функция get_children_quantity({1})'.
                     format(message.from_user.id, message))

        crud.update_message_db(user_id_class=message.from_user.id,
                               chat_id_class=message.chat.id,
                               message_id_class=message.message_id)

        crud.delete_message_db(user_id_class=message.from_user.id,
                               chat_id_class=message.chat.id)

        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            if not message.text.isdigit():
                logger.warning(
                    'user_id - {0}; количество детей {1} не является целым числом или отрицательное число'.
                    format(message.from_user.id, message.text))

                msg_to_dlt_get_children_quantity_1: Message = bot.send_message(
                    message.chat.id, text=''.join(i_element for i_element in data['main_text'].values()))

                crud.update_message_db(user_id_class=msg_to_dlt_get_children_quantity_1.from_user.id,
                                       chat_id_class=msg_to_dlt_get_children_quantity_1.chat.id,
                                       message_id_class=msg_to_dlt_get_children_quantity_1.message_id)

                msg_to_dlt_get_children_quantity_2: Message = bot.send_message(
                    message.chat.id, text='Количество детей {} должно быть целым числом и'
                                          ' не может быть отрицательным!!!'
                                          '\nВведите другое количество детей:'.
                    format(message.text))

                crud.update_message_db(user_id_class=msg_to_dlt_get_children_quantity_2.from_user.id,
                                       chat_id_class=msg_to_dlt_get_children_quantity_2.chat.id,
                                       message_id_class=msg_to_dlt_get_children_quantity_2.message_id)

                bot.set_state(message.from_user.id, SearchStates.children_quantity,
                              message.chat.id)

            else:
                data['children_ages'] = []
                data['children_quantity_in_process'] = 0
                data['children_quantity'] = message.text
                data['main_text']['children_quantity'] = '\nКоличество детей - {}'.format(data['children_quantity'])

                logger.info('user_id - {0}; количество детей - {1}'.
                            format(message.from_user.id, data['children_quantity']))

                if data['children_quantity_in_process'] < int(data['children_quantity']):
                    bot.set_state(message.from_user.id, SearchStates.child_age,
                                  message.chat.id)

                    msg_to_dlt_get_children_quantity_3: Message = bot.send_message(
                        message.chat.id, text=''.join(i_element for i_element in data['main_text'].values()))

                    crud.update_message_db(user_id_class=msg_to_dlt_get_children_quantity_3.from_user.id,
                                           chat_id_class=msg_to_dlt_get_children_quantity_3.chat.id,
                                           message_id_class=msg_to_dlt_get_children_quantity_3.message_id)

                    msg_to_dlt_get_children_quantity_4: Message = bot.send_message(
                        message.chat.id, text='Введите возраст {}-го ребенка:'.
                        format(int(data['children_quantity_in_process']) + 1))

                    crud.update_message_db(user_id_class=msg_to_dlt_get_children_quantity_4.from_user.id,
                                           chat_id_class=msg_to_dlt_get_children_quantity_4.chat.id,
                                           message_id_class=msg_to_dlt_get_children_quantity_4.message_id)

                else:
                    bot.set_state(message.from_user.id, SearchStates.max_distance_from_center,
                                  message.chat.id)

                    data['children_ages'] = []

                    logger.info('user_id - {0}; список возрастов детей - {1}'.
                                format(message.from_user.id, data['children_quantity']))

                    create_km_mile_keyboard(message.from_user.id, message.chat.id)

    except ApiTelegramException as exception:
        logger.exception(
            'user_id - {0}; тип ошибки - {1}'.format(message.from_user.id, exception))

        msg_to_dlt_mistake_1: Message = \
            bot.send_message(message.chat.id,
                             text='Ошибка связи с Телеграм.\nНажмите меню для выбора дальнейших действий.')

        crud.update_message_db(user_id_class=msg_to_dlt_mistake_1.from_user.id,
                               chat_id_class=msg_to_dlt_mistake_1.chat.id,
                               message_id_class=msg_to_dlt_mistake_1.message_id)

    except (ReadTimeout, TimeoutError) as exception:
        logger.exception(
            'user_id - {0}; тип ошибки - {1}'.format(message.from_user.id, exception))

        msg_to_dlt_mistake_2: Message = \
            bot.send_message(message.chat.id,
                             text='Ошибка. Время ожидания истекло.\nНажмите меню для выбора дальнейших действий.')

        crud.update_message_db(user_id_class=msg_to_dlt_mistake_2.from_user.id,
                               chat_id_class=msg_to_dlt_mistake_2.chat.id,
                               message_id_class=msg_to_dlt_mistake_2.message_id)

    except (OperationalError, ValueError, KeyError, NameError) as exception:
        logger.exception(
            'user_id - {0}; тип ошибки - {1}'.format(message.from_user.id, exception))

        msg_to_dlt_mistake_3: Message = \
            bot.send_message(message.chat.id,
                             text='Ошибка доступа к Вашей базе запросов.\nНажмите меню для выбора дальнейших действий.')

        crud.update_message_db(user_id_class=msg_to_dlt_mistake_3.from_user.id,
                               chat_id_class=msg_to_dlt_mistake_3.chat.id,
                               message_id_class=msg_to_dlt_mistake_3.message_id)


@bot.message_handler(state=SearchStates.adults_quantity_rewrite)
def get_rewrite_adults_quantity(message: Message) -> None:
    """
    Функция принимает и обрабатывает измененное значение количества взрослых.

    :param message: Сообщение с количеством взрослых полученное от пользователя
    :type message: Message
    """
    try:
        logger.debug('user_id - {0}; вызов - функция get_adults_quantity({1})'.
                     format(message.from_user.id, message))

        crud.update_message_db(user_id_class=message.from_user.id,
                               chat_id_class=message.chat.id,
                               message_id_class=message.message_id)

        crud.delete_message_db(user_id_class=message.from_user.id,
                               chat_id_class=message.chat.id)

        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            if not message.text.isdigit():
                logger.warning('user_id - {0};'
                               ' количество взрослых {1} не является целым числом или отрицательное число'.
                               format(message.from_user.id, message.text))

                msg_to_dlt_get_rewrite_adults_quantity_1: Message = bot.send_message(
                    message.chat.id, text=''.join(i_element for i_element in data['main_text'].values()))

                crud.update_message_db(user_id_class=msg_to_dlt_get_rewrite_adults_quantity_1.from_user.id,
                                       chat_id_class=msg_to_dlt_get_rewrite_adults_quantity_1.chat.id,
                                       message_id_class=msg_to_dlt_get_rewrite_adults_quantity_1.message_id)

                msg_to_dlt_get_rewrite_adults_quantity_2: Message = bot.send_message(
                    message.chat.id, text='Количество взрослых {} должно быть целым числом и'
                                          ' не может быть отрицательным!!!'
                                          '\nВведите другое количество взрослых:'.
                    format(message.text))

                crud.update_message_db(user_id_class=msg_to_dlt_get_rewrite_adults_quantity_2.from_user.id,
                                       chat_id_class=msg_to_dlt_get_rewrite_adults_quantity_2.chat.id,
                                       message_id_class=msg_to_dlt_get_rewrite_adults_quantity_2.message_id)

                bot.set_state(message.from_user.id, SearchStates.adults_quantity_rewrite,
                              message.chat.id)

            else:
                bot.set_state(message.from_user.id, SearchStates.hotels,
                              message.chat.id)

                data['adults_quantity'] = message.text
                data['main_text']['adults_quantity'] = '\nКоличество взрослых - {}'.format(data['adults_quantity'])
                data['main_text']['start'] = 'Ваш запрос:'

                logger.info('user_id - {0}; количество взрослых - {1}'.
                            format(message.from_user.id, data['adults_quantity']))

                msg_to_dlt_get_rewrite_adults_quantity_3: Message = bot.send_message(
                    message.chat.id, text=''.join(i_element for i_element in data['main_text'].values()))

                crud.update_message_db(user_id_class=msg_to_dlt_get_rewrite_adults_quantity_3.from_user.id,
                                       chat_id_class=msg_to_dlt_get_rewrite_adults_quantity_3.chat.id,
                                       message_id_class=msg_to_dlt_get_rewrite_adults_quantity_3.message_id)

                msg_to_dlt_get_rewrite_adults_quantity_4: Message = \
                    bot.send_message(message.chat.id,
                                     text='Проверьте Ваш запрос.\nВсе верно?',
                                     reply_markup=create_yes_no_keyboard(user_id=message.from_user.id,
                                                                         callback_data_yes='yes',
                                                                         callback_data_no='no'))

                crud.update_message_db(user_id_class=msg_to_dlt_get_rewrite_adults_quantity_4.from_user.id,
                                       chat_id_class=msg_to_dlt_get_rewrite_adults_quantity_4.chat.id,
                                       message_id_class=msg_to_dlt_get_rewrite_adults_quantity_4.message_id)

    except ApiTelegramException as exception:
        logger.exception(
            'user_id - {0}; тип ошибки - {1}'.format(message.from_user.id, exception))

        msg_to_dlt_mistake_1: Message = \
            bot.send_message(message.chat.id,
                             text='Ошибка связи с Телеграм.\nНажмите меню для выбора дальнейших действий.')

        crud.update_message_db(user_id_class=msg_to_dlt_mistake_1.from_user.id,
                               chat_id_class=msg_to_dlt_mistake_1.chat.id,
                               message_id_class=msg_to_dlt_mistake_1.message_id)

    except (ReadTimeout, TimeoutError) as exception:
        logger.exception(
            'user_id - {0}; тип ошибки - {1}'.format(message.from_user.id, exception))

        msg_to_dlt_mistake_2: Message = \
            bot.send_message(message.chat.id,
                             text='Ошибка. Время ожидания истекло.\nНажмите меню для выбора дальнейших действий.')

        crud.update_message_db(user_id_class=msg_to_dlt_mistake_2.from_user.id,
                               chat_id_class=msg_to_dlt_mistake_2.chat.id,
                               message_id_class=msg_to_dlt_mistake_2.message_id)

    except (OperationalError, ValueError, KeyError, NameError) as exception:
        logger.exception(
            'user_id - {0}; тип ошибки - {1}'.format(message.from_user.id, exception))

        msg_to_dlt_mistake_3: Message = \
            bot.send_message(message.chat.id,
                             text='Ошибка доступа к Вашей базе запросов.\nНажмите меню для выбора дальнейших действий.')

        crud.update_message_db(user_id_class=msg_to_dlt_mistake_3.from_user.id,
                               chat_id_class=msg_to_dlt_mistake_3.chat.id,
                               message_id_class=msg_to_dlt_mistake_3.message_id)


@bot.message_handler(state=SearchStates.adults_quantity)
def get_adults_quantity(message: Message) -> None:
    """
    Функция принимает и обрабатывает значение количества взрослых.

    :param message: Сообщение с количеством взрослых полученное от пользователя
    :type message: Message
    """
    try:
        logger.debug('user_id - {0}; вызов - функция get_adults_quantity({1})'.
                     format(message.from_user.id, message))

        crud.update_message_db(user_id_class=message.from_user.id,
                               chat_id_class=message.chat.id,
                               message_id_class=message.message_id)

        crud.delete_message_db(user_id_class=message.from_user.id,
                               chat_id_class=message.chat.id)

        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            if not message.text.isdigit():
                logger.warning('user_id - {0};'
                               ' количество взрослых {1} не является целым числом или отрицательное число'.
                               format(message.from_user.id, message.text))

                msg_to_dlt_get_adults_quantity_1: Message = bot.send_message(
                    message.chat.id, text=''.join(i_element for i_element in data['main_text'].values()))

                crud.update_message_db(user_id_class=msg_to_dlt_get_adults_quantity_1.from_user.id,
                                       chat_id_class=msg_to_dlt_get_adults_quantity_1.chat.id,
                                       message_id_class=msg_to_dlt_get_adults_quantity_1.message_id)

                msg_to_dlt_get_adults_quantity_2: Message = bot.send_message(
                    message.chat.id, text='Количество взрослых {} должно быть целым числом и'
                                          ' не может быть отрицательным!!!'
                                          '\nВведите другое количество взрослых:'.
                    format(message.text))

                crud.update_message_db(user_id_class=msg_to_dlt_get_adults_quantity_2.from_user.id,
                                       chat_id_class=msg_to_dlt_get_adults_quantity_2.chat.id,
                                       message_id_class=msg_to_dlt_get_adults_quantity_2.message_id)

                bot.set_state(message.from_user.id, SearchStates.adults_quantity,
                              message.chat.id)

            else:
                bot.set_state(message.from_user.id, SearchStates.children_quantity,
                              message.chat.id)

                data['adults_quantity'] = message.text
                data['main_text']['adults_quantity'] = '\nКоличество взрослых - {}'.format(data['adults_quantity'])

                logger.info('user_id - {0}; количество взрослых - {1}'.
                            format(message.from_user.id, data['adults_quantity']))

                msg_to_dlt_get_adults_quantity_3: Message = bot.send_message(
                    message.chat.id, text=''.join(i_element for i_element in data['main_text'].values()))

                crud.update_message_db(user_id_class=msg_to_dlt_get_adults_quantity_3.from_user.id,
                                       chat_id_class=msg_to_dlt_get_adults_quantity_3.chat.id,
                                       message_id_class=msg_to_dlt_get_adults_quantity_3.message_id)

                msg_to_dlt_get_adults_quantity_4: Message = bot.send_message(
                    message.chat.id, text='Введите количество детей:')

                crud.update_message_db(user_id_class=msg_to_dlt_get_adults_quantity_4.from_user.id,
                                       chat_id_class=msg_to_dlt_get_adults_quantity_4.chat.id,
                                       message_id_class=msg_to_dlt_get_adults_quantity_4.message_id)

    except ApiTelegramException as exception:
        logger.exception(
            'user_id - {0}; тип ошибки - {1}'.format(message.from_user.id, exception))

        msg_to_dlt_mistake_1: Message = \
            bot.send_message(message.chat.id,
                             text='Ошибка связи с Телеграм.\nНажмите меню для выбора дальнейших действий.')

        crud.update_message_db(user_id_class=msg_to_dlt_mistake_1.from_user.id,
                               chat_id_class=msg_to_dlt_mistake_1.chat.id,
                               message_id_class=msg_to_dlt_mistake_1.message_id)

    except (ReadTimeout, TimeoutError) as exception:
        logger.exception(
            'user_id - {0}; тип ошибки - {1}'.format(message.from_user.id, exception))

        msg_to_dlt_mistake_2: Message = \
            bot.send_message(message.chat.id,
                             text='Ошибка. Время ожидания истекло.\nНажмите меню для выбора дальнейших действий.')

        crud.update_message_db(user_id_class=msg_to_dlt_mistake_2.from_user.id,
                               chat_id_class=msg_to_dlt_mistake_2.chat.id,
                               message_id_class=msg_to_dlt_mistake_2.message_id)

    except (OperationalError, ValueError, KeyError, NameError) as exception:
        logger.exception(
            'user_id - {0}; тип ошибки - {1}'.format(message.from_user.id, exception))

        msg_to_dlt_mistake_3: Message = \
            bot.send_message(message.chat.id,
                             text='Ошибка доступа к Вашей базе запросов.\nНажмите меню для выбора дальнейших действий.')

        crud.update_message_db(user_id_class=msg_to_dlt_mistake_3.from_user.id,
                               chat_id_class=msg_to_dlt_mistake_3.chat.id,
                               message_id_class=msg_to_dlt_mistake_3.message_id)


@bot.message_handler(state=SearchStates.max_price_rewrite)
def get_rewrite_max_price(message: Message) -> None:
    """
    Функция принимает от пользователя измененное значение максимальной цены за сутки, проверяет чтобы полученное
    значение было числом, было больше минимальной цены за сутки, сохраняет его.

    :param message: Значение полученное от пользователя
    :type message: Message
    """
    try:
        logger.debug('user_id - {0}; вызов - функция get_rewrite_max_price({1})'.
                     format(message.from_user.id, message))

        crud.update_message_db(user_id_class=message.from_user.id,
                               chat_id_class=message.chat.id,
                               message_id_class=message.message_id)

        crud.delete_message_db(user_id_class=message.from_user.id,
                               chat_id_class=message.chat.id)

        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            if not message.text.isdigit():
                logger.warning('user_id - {0}; максимальная цена {1}$ не является числом или отрицательное число'.
                               format(message.from_user.id, message.text))

                msg_to_dlt_get_rewrite_max_price_1: Message = bot.send_message(
                    message.chat.id, text=''.join(i_element for i_element in data['main_text'].values()))

                crud.update_message_db(user_id_class=msg_to_dlt_get_rewrite_max_price_1.from_user.id,
                                       chat_id_class=msg_to_dlt_get_rewrite_max_price_1.chat.id,
                                       message_id_class=msg_to_dlt_get_rewrite_max_price_1.message_id)

                msg_to_dlt_get_rewrite_max_price_2: Message = \
                    bot.send_message(message.chat.id,
                                     text='Цена {}$ должна быть числом и не может быть отрицательной!!!'
                                          '\nВведите другую максимальную цену проживания за сутки в $:'.
                                     format(message.text))

                crud.update_message_db(user_id_class=msg_to_dlt_get_rewrite_max_price_2.from_user.id,
                                       chat_id_class=msg_to_dlt_get_rewrite_max_price_2.chat.id,
                                       message_id_class=msg_to_dlt_get_rewrite_max_price_2.message_id)

                bot.set_state(message.from_user.id, SearchStates.max_price_rewrite,
                              message.chat.id)

            elif float(message.text) < float(data['min_price']):
                logger.warning('user_id - {0}; максимальная цена {1}$ меньше минимальной цены {2}$'.
                               format(message.from_user.id, float(message.text), data['min_price']))

                msg_to_dlt_get_rewrite_max_price_3: Message = bot.send_message(
                    message.chat.id, text=''.join(i_element for i_element in data['main_text'].values()))

                crud.update_message_db(user_id_class=msg_to_dlt_get_rewrite_max_price_3.from_user.id,
                                       chat_id_class=msg_to_dlt_get_rewrite_max_price_3.chat.id,
                                       message_id_class=msg_to_dlt_get_rewrite_max_price_3.message_id)

                msg_to_dlt_get_rewrite_max_price_4: Message = \
                    bot.send_message(message.chat.id,
                                     text='Максимальная цена {0}$ должна быть больше или равна минимальной цене {1}$!!!'
                                          '\nВведите другую максимальную цену проживания за сутки в $:'.
                                     format(message.text, data['min_price']))

                crud.update_message_db(user_id_class=msg_to_dlt_get_rewrite_max_price_4.from_user.id,
                                       chat_id_class=msg_to_dlt_get_rewrite_max_price_4.chat.id,
                                       message_id_class=msg_to_dlt_get_rewrite_max_price_4.message_id)

                bot.set_state(message.from_user.id, SearchStates.max_price_rewrite,
                              message.chat.id)

            else:
                bot.set_state(message.from_user.id, SearchStates.hotels,
                              message.chat.id)

                data['max_price'] = message.text
                data['main_text']['max_price'] = '\nМаксимальная цена - {}$'.format(data['max_price'])

                logger.info('user_id - {0}; максимальная цена - {1}$'.
                            format(message.from_user.id, data['max_price']))

                msg_to_dlt_get_rewrite_max_price_5: Message = bot.send_message(
                    message.chat.id, text=''.join(i_element for i_element in data['main_text'].values()))

                crud.update_message_db(user_id_class=msg_to_dlt_get_rewrite_max_price_5.from_user.id,
                                       chat_id_class=msg_to_dlt_get_rewrite_max_price_5.chat.id,
                                       message_id_class=msg_to_dlt_get_rewrite_max_price_5.message_id)

                msg_to_dlt_get_rewrite_max_price_6: Message = bot.send_message(message.chat.id,
                                                                               text='Проверьте Ваш запрос.\nВсе верно?',
                                                                               reply_markup=create_yes_no_keyboard(
                                                                                   user_id=message.from_user.id,
                                                                                   callback_data_yes='yes',
                                                                                   callback_data_no='no'))

                crud.update_message_db(user_id_class=msg_to_dlt_get_rewrite_max_price_6.from_user.id,
                                       chat_id_class=msg_to_dlt_get_rewrite_max_price_6.chat.id,
                                       message_id_class=msg_to_dlt_get_rewrite_max_price_6.message_id)

    except ApiTelegramException as exception:
        logger.exception(
            'user_id - {0}; тип ошибки - {1}'.format(message.from_user.id, exception))

        msg_to_dlt_mistake_1: Message = \
            bot.send_message(message.chat.id,
                             text='Ошибка связи с Телеграм.\nНажмите меню для выбора дальнейших действий.')

        crud.update_message_db(user_id_class=msg_to_dlt_mistake_1.from_user.id,
                               chat_id_class=msg_to_dlt_mistake_1.chat.id,
                               message_id_class=msg_to_dlt_mistake_1.message_id)

    except (ReadTimeout, TimeoutError) as exception:
        logger.exception(
            'user_id - {0}; тип ошибки - {1}'.format(message.from_user.id, exception))

        msg_to_dlt_mistake_2: Message = \
            bot.send_message(message.chat.id,
                             text='Ошибка. Время ожидания истекло.\nНажмите меню для выбора дальнейших действий.')

        crud.update_message_db(user_id_class=msg_to_dlt_mistake_2.from_user.id,
                               chat_id_class=msg_to_dlt_mistake_2.chat.id,
                               message_id_class=msg_to_dlt_mistake_2.message_id)

    except (OperationalError, ValueError, KeyError, NameError) as exception:
        logger.exception(
            'user_id - {0}; тип ошибки - {1}'.format(message.from_user.id, exception))

        msg_to_dlt_mistake_3: Message = \
            bot.send_message(message.chat.id,
                             text='Ошибка доступа к Вашей базе запросов.\nНажмите меню для выбора дальнейших действий.')

        crud.update_message_db(user_id_class=msg_to_dlt_mistake_3.from_user.id,
                               chat_id_class=msg_to_dlt_mistake_3.chat.id,
                               message_id_class=msg_to_dlt_mistake_3.message_id)


@bot.message_handler(state=SearchStates.max_price)
def get_max_price(message: Message) -> None:
    """
    Функция принимает от пользователя значение максимальной цены за сутки, проверяет чтобы полученное значение
    было числом, было больше минимальной цены за сутки, сохраняет его,
    запрашивает у пользователя максимальное расстояние отеля от центра города.

    :param message: Сообщение с максимальной ценой проживания полученное от пользователя
    :type message: Message
    """
    try:
        logger.debug('user_id - {0}; вызов - функция get_max_price({1})'.
                     format(message.from_user.id, message))

        crud.update_message_db(user_id_class=message.from_user.id,
                               chat_id_class=message.chat.id,
                               message_id_class=message.message_id)

        crud.delete_message_db(user_id_class=message.from_user.id,
                               chat_id_class=message.chat.id)

        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            if not message.text.isdigit():
                logger.warning('user_id - {0}; максимальная цена {1}$ не является числом или отрицательное число'.
                               format(message.from_user.id, message.text))

                msg_to_dlt_get_max_price_1: Message = bot.send_message(
                    message.chat.id, text=''.join(i_element for i_element in data['main_text'].values()))

                crud.update_message_db(user_id_class=msg_to_dlt_get_max_price_1.from_user.id,
                                       chat_id_class=msg_to_dlt_get_max_price_1.chat.id,
                                       message_id_class=msg_to_dlt_get_max_price_1.message_id)

                msg_to_dlt_get_max_price_2: Message = bot.send_message(
                    message.chat.id, text='Цена {}$ должна быть числом и не может быть отрицательной!!!'
                                          '\nВведите другую максимальную цену проживания за сутки в $:'.
                    format(message.text))

                crud.update_message_db(user_id_class=msg_to_dlt_get_max_price_2.from_user.id,
                                       chat_id_class=msg_to_dlt_get_max_price_2.chat.id,
                                       message_id_class=msg_to_dlt_get_max_price_2.message_id)

                bot.set_state(message.from_user.id, SearchStates.max_price,
                              message.chat.id)

            elif float(message.text) < float(data['min_price']):
                logger.warning('user_id - {0}; максимальная цена {1}$ меньше минимальной цены {2}$'.
                               format(message.from_user.id, float(message.text), data['min_price']))

                msg_to_dlt_get_max_price_3: Message = bot.send_message(
                    message.chat.id, text=''.join(i_element for i_element in data['main_text'].values()))

                crud.update_message_db(user_id_class=msg_to_dlt_get_max_price_3.from_user.id,
                                       chat_id_class=msg_to_dlt_get_max_price_3.chat.id,
                                       message_id_class=msg_to_dlt_get_max_price_3.message_id)

                msg_to_dlt_get_max_price_4: Message = bot.send_message(
                    message.chat.id, text='Максимальная цена {0}$ должна быть больше или равна'
                                          ' минимальной цене {1}$!!!'
                                          '\nВведите другую максимальную цену проживания'
                                          ' за сутки в $:'.format(message.text,
                                                                  data['min_price']))

                crud.update_message_db(user_id_class=msg_to_dlt_get_max_price_4.from_user.id,
                                       chat_id_class=msg_to_dlt_get_max_price_4.chat.id,
                                       message_id_class=msg_to_dlt_get_max_price_4.message_id)

                bot.set_state(message.from_user.id, SearchStates.max_price,
                              message.chat.id)

            else:
                bot.set_state(message.from_user.id, SearchStates.adults_quantity,
                              message.chat.id)

                data['max_price'] = message.text
                data['main_text']['max_price'] = '\nМаксимальная цена - {}$'.format(data['max_price'])

                logger.info('user_id - {0}; максимальная цена - {1}$'.
                            format(message.from_user.id, data['max_price']))

                msg_to_dlt_get_max_price_5: Message = bot.send_message(
                    message.chat.id, text=''.join(i_element for i_element in data['main_text'].values()))

                crud.update_message_db(user_id_class=msg_to_dlt_get_max_price_5.from_user.id,
                                       chat_id_class=msg_to_dlt_get_max_price_5.chat.id,
                                       message_id_class=msg_to_dlt_get_max_price_5.message_id)

                msg_to_dlt_get_max_price_6: Message = bot.send_message(
                    message.chat.id, text='Введите количество взрослых:')

                crud.update_message_db(user_id_class=msg_to_dlt_get_max_price_6.from_user.id,
                                       chat_id_class=msg_to_dlt_get_max_price_6.chat.id,
                                       message_id_class=msg_to_dlt_get_max_price_6.message_id)

    except ApiTelegramException as exception:
        logger.exception(
            'user_id - {0}; тип ошибки - {1}'.format(message.from_user.id, exception))

        msg_to_dlt_mistake_1: Message = \
            bot.send_message(message.chat.id,
                             text='Ошибка связи с Телеграм.\nНажмите меню для выбора дальнейших действий.')

        crud.update_message_db(user_id_class=msg_to_dlt_mistake_1.from_user.id,
                               chat_id_class=msg_to_dlt_mistake_1.chat.id,
                               message_id_class=msg_to_dlt_mistake_1.message_id)

    except (ReadTimeout, TimeoutError) as exception:
        logger.exception(
            'user_id - {0}; тип ошибки - {1}'.format(message.from_user.id, exception))

        msg_to_dlt_mistake_2: Message = \
            bot.send_message(message.chat.id,
                             text='Ошибка. Время ожидания истекло.\nНажмите меню для выбора дальнейших действий.')

        crud.update_message_db(user_id_class=msg_to_dlt_mistake_2.from_user.id,
                               chat_id_class=msg_to_dlt_mistake_2.chat.id,
                               message_id_class=msg_to_dlt_mistake_2.message_id)

    except (OperationalError, ValueError, KeyError, NameError) as exception:
        logger.exception(
            'user_id - {0}; тип ошибки - {1}'.format(message.from_user.id, exception))

        msg_to_dlt_mistake_3: Message = \
            bot.send_message(message.chat.id,
                             text='Ошибка доступа к Вашей базе запросов.\nНажмите меню для выбора дальнейших действий.')

        crud.update_message_db(user_id_class=msg_to_dlt_mistake_3.from_user.id,
                               chat_id_class=msg_to_dlt_mistake_3.chat.id,
                               message_id_class=msg_to_dlt_mistake_3.message_id)


@bot.message_handler(state=SearchStates.min_price_rewrite)
def get_rewrite_min_price(message: Message) -> None:
    """
    Функция принимает от пользователя измененное значение минимальной цены за сутки, проверяет чтобы полученное значение
    было числом, было больше 0, сохраняет его.

    :param message: Значение полученное от пользователя
    :type message: Message
    """
    try:
        logger.debug('user_id - {0}; вызов - функция get_rewrite_min_price({1})'.
                     format(message.from_user.id, message))

        crud.update_message_db(user_id_class=message.from_user.id,
                               chat_id_class=message.chat.id,
                               message_id_class=message.message_id)

        crud.delete_message_db(user_id_class=message.from_user.id,
                               chat_id_class=message.chat.id)

        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:

            if not message.text.isdigit():
                logger.warning('user_id - {0}; минимальная цена {1}$ не является числом или отрицательное число'.
                               format(message.from_user.id, message.text))

                msg_to_dlt_get_rewrite_min_price_1: Message = bot.send_message(
                    message.chat.id, text=''.join(i_element for i_element in data['main_text'].values()))

                crud.update_message_db(user_id_class=msg_to_dlt_get_rewrite_min_price_1.from_user.id,
                                       chat_id_class=msg_to_dlt_get_rewrite_min_price_1.chat.id,
                                       message_id_class=msg_to_dlt_get_rewrite_min_price_1.message_id)

                msg_to_dlt_get_rewrite_min_price_2: Message = \
                    bot.send_message(message.chat.id,
                                     text='Цена {}$ должна быть числом и не может быть отрицательной!!!'
                                          '\nВведите другую минимальную цену проживания за сутки в $:'.
                                     format(message.text))

                crud.update_message_db(user_id_class=msg_to_dlt_get_rewrite_min_price_2.from_user.id,
                                       chat_id_class=msg_to_dlt_get_rewrite_min_price_2.chat.id,
                                       message_id_class=msg_to_dlt_get_rewrite_min_price_2.message_id)

                bot.set_state(message.from_user.id, SearchStates.min_price_rewrite,
                              message.chat.id)

            else:
                if float(message.text) == 0:
                    bot.set_state(message.from_user.id, SearchStates.hotels,
                                  message.chat.id)

                    data['min_price'] = '1'
                    data['main_text']['min_price'] = '\nМинимальная цена - {}$'.format(int(data['min_price']) - 1)

                    logger.info('user_id - {0}; минимальная цена - {1}$'.
                                format(message.from_user.id, data['min_price']))

                    msg_to_dlt_get_rewrite_min_price_3: Message = bot.send_message(
                        message.chat.id, text=''.join(i_element for i_element in data['main_text'].values()))

                    crud.update_message_db(user_id_class=msg_to_dlt_get_rewrite_min_price_3.from_user.id,
                                           chat_id_class=msg_to_dlt_get_rewrite_min_price_3.chat.id,
                                           message_id_class=msg_to_dlt_get_rewrite_min_price_3.message_id)

                    msg_to_dlt_get_rewrite_min_price_4: Message =\
                        bot.send_message(message.chat.id,
                                         text='Проверьте Ваш запрос.\nВсе верно?',
                                         reply_markup=create_yes_no_keyboard(user_id=message.from_user.id,
                                                                             callback_data_yes='yes',
                                                                             callback_data_no='no'))

                    crud.update_message_db(user_id_class=msg_to_dlt_get_rewrite_min_price_4.from_user.id,
                                           chat_id_class=msg_to_dlt_get_rewrite_min_price_4.chat.id,
                                           message_id_class=msg_to_dlt_get_rewrite_min_price_4.message_id)

                else:
                    bot.set_state(message.from_user.id, SearchStates.hotels,
                                  message.chat.id)

                    if float(message.text) > float(data['max_price']):
                        logger.warning(
                            'user_id - {0}; минимальная цена {1}$ больше максимальной цены {2}$'.
                            format(message.from_user.id, message.text, data['max_price']))

                        msg_to_dlt_get_rewrite_min_price_5: Message = bot.send_message(
                            message.chat.id, text=''.join(i_element for i_element in data['main_text'].values()))

                        crud.update_message_db(user_id_class=msg_to_dlt_get_rewrite_min_price_5.from_user.id,
                                               chat_id_class=msg_to_dlt_get_rewrite_min_price_5.chat.id,
                                               message_id_class=msg_to_dlt_get_rewrite_min_price_5.message_id)

                        msg_to_dlt_get_rewrite_min_price_6: Message = \
                            bot.send_message(message.chat.id,
                                             text='Минимальная цена {0}$ должна быть меньше или равна '
                                                  'максимальной цене {1}$!!!'
                                                  '\nВведите  другую минимальную цену проживания за сутки в $:'.
                                             format(message.text, data['max_price']))

                        crud.update_message_db(user_id_class=msg_to_dlt_get_rewrite_min_price_6.from_user.id,
                                               chat_id_class=msg_to_dlt_get_rewrite_min_price_6.chat.id,
                                               message_id_class=msg_to_dlt_get_rewrite_min_price_6.message_id)

                        bot.set_state(message.from_user.id, SearchStates.min_price_rewrite,
                                      message.chat.id)
                    else:

                        data['min_price'] = message.text
                        data['main_text']['min_price'] = '\nМинимальная цена - {}$'.format(int(data['min_price']))

                        logger.info('user_id - {0}; минимальная цена - {1}$'.
                                    format(message.from_user.id, data['min_price']))

                        msg_to_dlt_get_rewrite_min_price_7: Message = bot.send_message(
                            message.chat.id, text=''.join(i_element for i_element in data['main_text'].values()))

                        crud.update_message_db(user_id_class=msg_to_dlt_get_rewrite_min_price_7.from_user.id,
                                               chat_id_class=msg_to_dlt_get_rewrite_min_price_7.chat.id,
                                               message_id_class=msg_to_dlt_get_rewrite_min_price_7.message_id)

                        msg_to_dlt_get_rewrite_min_price_8: Message = \
                            bot.send_message(message.chat.id,
                                             text='Проверьте Ваш запрос.\nВсе верно?',
                                             reply_markup=create_yes_no_keyboard(user_id=message.from_user.id,
                                                                                 callback_data_yes='yes',
                                                                                 callback_data_no='no'))

                        crud.update_message_db(user_id_class=msg_to_dlt_get_rewrite_min_price_8.from_user.id,
                                               chat_id_class=msg_to_dlt_get_rewrite_min_price_8.chat.id,
                                               message_id_class=msg_to_dlt_get_rewrite_min_price_8.message_id)

    except ApiTelegramException as exception:
        logger.exception(
            'user_id - {0}; тип ошибки - {1}'.format(message.from_user.id, exception))

        msg_to_dlt_mistake_1: Message = \
            bot.send_message(message.chat.id,
                             text='Ошибка связи с Телеграм.\nНажмите меню для выбора дальнейших действий.')

        crud.update_message_db(user_id_class=msg_to_dlt_mistake_1.from_user.id,
                               chat_id_class=msg_to_dlt_mistake_1.chat.id,
                               message_id_class=msg_to_dlt_mistake_1.message_id)

    except (ReadTimeout, TimeoutError) as exception:
        logger.exception(
            'user_id - {0}; тип ошибки - {1}'.format(message.from_user.id, exception))

        msg_to_dlt_mistake_2: Message = \
            bot.send_message(message.chat.id,
                             text='Ошибка. Время ожидания истекло.\nНажмите меню для выбора дальнейших действий.')

        crud.update_message_db(user_id_class=msg_to_dlt_mistake_2.from_user.id,
                               chat_id_class=msg_to_dlt_mistake_2.chat.id,
                               message_id_class=msg_to_dlt_mistake_2.message_id)

    except (OperationalError, ValueError, KeyError, NameError) as exception:
        logger.exception(
            'user_id - {0}; тип ошибки - {1}'.format(message.from_user.id, exception))

        msg_to_dlt_mistake_3: Message = \
            bot.send_message(message.chat.id,
                             text='Ошибка доступа к Вашей базе запросов.\nНажмите меню для выбора дальнейших действий.')

        crud.update_message_db(user_id_class=msg_to_dlt_mistake_3.from_user.id,
                               chat_id_class=msg_to_dlt_mistake_3.chat.id,
                               message_id_class=msg_to_dlt_mistake_3.message_id)


@bot.message_handler(state=SearchStates.min_price)
def get_min_price(message: Message) -> None:
    """
    Функция принимает от пользователя значение минимальной цены за сутки, проверяет чтобы полученное значение
    было числом, было больше 0, сохраняет его, запрашивает у пользователя максимальную цену за сутки.

    :param message: Сообщение с минимальной ценой проживания полученное от пользователя
    :type message: Message
    """
    try:
        logger.debug('user_id - {0}; вызов - функция get_min_price({1})'.
                     format(message.from_user.id, message))

        crud.update_message_db(user_id_class=message.from_user.id,
                               chat_id_class=message.chat.id,
                               message_id_class=message.message_id)

        crud.delete_message_db(user_id_class=message.from_user.id,
                               chat_id_class=message.chat.id)

        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            if not message.text.isdigit():
                logger.warning('user_id - {0}; минимальная цена {1}$ не является числом или отрицательное число'.
                               format(message.from_user.id, message.text))

                msg_to_dlt_get_min_price_1: Message = bot.send_message(
                    message.chat.id, text=''.join(i_element for i_element in data['main_text'].values()))

                crud.update_message_db(user_id_class=msg_to_dlt_get_min_price_1.from_user.id,
                                       chat_id_class=msg_to_dlt_get_min_price_1.chat.id,
                                       message_id_class=msg_to_dlt_get_min_price_1.message_id)

                msg_to_dlt_get_min_price_2: Message = bot.send_message(
                    message.chat.id, text='Цена {}$ должна быть числом и не может быть отрицательной!!!'
                                          '\nВведите другую минимальную цену проживания за сутки'
                                          ' в $:'.
                    format(message.text))

                crud.update_message_db(user_id_class=msg_to_dlt_get_min_price_2.from_user.id,
                                       chat_id_class=msg_to_dlt_get_min_price_2.chat.id,
                                       message_id_class=msg_to_dlt_get_min_price_2.message_id)

                bot.set_state(message.from_user.id, SearchStates.min_price,
                              message.chat.id)

            else:
                if float(message.text) == 0:
                    bot.set_state(message.from_user.id, SearchStates.max_price,
                                  message.chat.id)

                    data['min_price'] = '1'
                    data['main_text']['min_price'] = '\nМинимальная цена - {}$'.format(int(data['min_price']) - 1)

                    logger.info('user_id - {0}; минимальная цена - {1}$'.
                                format(message.from_user.id, data['min_price']))

                    msg_to_dlt_get_min_price_3: Message = bot.send_message(
                        message.chat.id, text=''.join(i_element for i_element in data['main_text'].values()))

                    crud.update_message_db(user_id_class=msg_to_dlt_get_min_price_3.from_user.id,
                                           chat_id_class=msg_to_dlt_get_min_price_3.chat.id,
                                           message_id_class=msg_to_dlt_get_min_price_3.message_id)

                    msg_to_dlt_get_min_price_4: Message = bot.send_message(
                        message.chat.id, text='Введите максимальную цену проживания за сутки в $:')

                    crud.update_message_db(user_id_class=msg_to_dlt_get_min_price_4.from_user.id,
                                           chat_id_class=msg_to_dlt_get_min_price_4.chat.id,
                                           message_id_class=msg_to_dlt_get_min_price_4.message_id)

                else:
                    bot.set_state(message.from_user.id, SearchStates.max_price,
                                  message.chat.id)

                    data['min_price'] = message.text
                    data['main_text']['min_price'] = '\nМинимальная цена - {}$'.format(int(data['min_price']))

                    logger.info('user_id - {0}; минимальная цена - {1}$'.
                                format(message.from_user.id, data['min_price']))

                    msg_to_dlt_get_min_price_5: Message = bot.send_message(
                        message.chat.id, text=''.join(i_element for i_element in data['main_text'].values()))

                    crud.update_message_db(user_id_class=msg_to_dlt_get_min_price_5.from_user.id,
                                           chat_id_class=msg_to_dlt_get_min_price_5.chat.id,
                                           message_id_class=msg_to_dlt_get_min_price_5.message_id)

                    msg_to_dlt_get_min_price_6: Message = bot.send_message(
                        message.chat.id, text='Введите максимальную цену проживания за сутки в $:')

                    crud.update_message_db(user_id_class=msg_to_dlt_get_min_price_6.from_user.id,
                                           chat_id_class=msg_to_dlt_get_min_price_6.chat.id,
                                           message_id_class=msg_to_dlt_get_min_price_6.message_id)

    except ApiTelegramException as exception:
        logger.exception(
            'user_id - {0}; тип ошибки - {1}'.format(message.from_user.id, exception))

        msg_to_dlt_mistake_1: Message = \
            bot.send_message(message.chat.id,
                             text='Ошибка связи с Телеграм.\nНажмите меню для выбора дальнейших действий.')

        crud.update_message_db(user_id_class=msg_to_dlt_mistake_1.from_user.id,
                               chat_id_class=msg_to_dlt_mistake_1.chat.id,
                               message_id_class=msg_to_dlt_mistake_1.message_id)

    except (ReadTimeout, TimeoutError) as exception:
        logger.exception(
            'user_id - {0}; тип ошибки - {1}'.format(message.from_user.id, exception))

        msg_to_dlt_mistake_2: Message = \
            bot.send_message(message.chat.id,
                             text='Ошибка. Время ожидания истекло.\nНажмите меню для выбора дальнейших действий.')

        crud.update_message_db(user_id_class=msg_to_dlt_mistake_2.from_user.id,
                               chat_id_class=msg_to_dlt_mistake_2.chat.id,
                               message_id_class=msg_to_dlt_mistake_2.message_id)

    except (OperationalError, ValueError, KeyError, NameError) as exception:
        logger.exception(
            'user_id - {0}; тип ошибки - {1}'.format(message.from_user.id, exception))

        msg_to_dlt_mistake_3: Message = \
            bot.send_message(message.chat.id,
                             text='Ошибка доступа к Вашей базе запросов.\nНажмите меню для выбора дальнейших действий.')

        crud.update_message_db(user_id_class=msg_to_dlt_mistake_3.from_user.id,
                               chat_id_class=msg_to_dlt_mistake_3.chat.id,
                               message_id_class=msg_to_dlt_mistake_3.message_id)


@bot.callback_query_handler(func=None, state=SearchStates.date_of_departure_rewrite)
def get_rewrite_date_of_departure(callback: CallbackQuery) -> None:
    """
    Функция обрабатывает результат работы клавиатуры yes_no_keyboard, проверяет,
    чтобы выбранная дата отъезда была позже даты приезда, сохраняет полученные данные.

    :param callback: Входящий запрос обратного вызова с кнопки клавиатуры yes_no_keyboard
    :type callback: CallbackQuery
    """
    try:
        logger.info('user_id - {0}; callback.data - {1}'.format(callback.from_user.id, callback.data))

        logger.debug('user_id - {0}; вызов - функция get_rewrite_date_of_departure({1})'.
                     format(callback.from_user.id, callback))

        crud.delete_message_db(user_id_class=callback.from_user.id,
                               chat_id_class=callback.message.chat.id)

        with bot.retrieve_data(callback.from_user.id, callback.message.chat.id) as data:

            if callback.data == 'no' or callback.message.text.find('None') != -1:

                logger.warning('user_id - {0}; дата отъезда {1} введена неверно'.
                               format(callback.from_user.id, callback.message.text[18:28]))

                msg_to_dlt_rewrite_date_of_departure_1: Message = bot.send_message(
                    callback.message.chat.id,
                    text=''.join(i_element for i_element in data['main_text'].values()))

                crud.update_message_db(user_id_class=msg_to_dlt_rewrite_date_of_departure_1.from_user.id,
                                       chat_id_class=msg_to_dlt_rewrite_date_of_departure_1.chat.id,
                                       message_id_class=msg_to_dlt_rewrite_date_of_departure_1.message_id)

                msg_to_dlt_rewrite_date_of_departure_2: Message = bot.send_message(callback.message.chat.id,
                                                                                   text='Введите другую дату отъезда:')

                crud.update_message_db(user_id_class=msg_to_dlt_rewrite_date_of_departure_2.from_user.id,
                                       chat_id_class=msg_to_dlt_rewrite_date_of_departure_2.chat.id,
                                       message_id_class=msg_to_dlt_rewrite_date_of_departure_2.message_id)

                run_calendar(callback.from_user.id, callback.message.chat.id)

                bot.set_state(callback.from_user.id, SearchStates.date_of_departure_rewrite,
                              callback.message.chat.id)

            else:
                date_of_departure = datetime.datetime.strptime(callback.data, '%Y-%m-%d')

                if date_of_departure < data['arrival_date']:
                    logger.warning('user_id - {0}; дата отъезда {1} раньше чем дата приезда {2}'.
                                   format(callback.from_user.id, str(date_of_departure)[:10],
                                          str(data['arrival_date'])[:10]))

                    msg_to_dlt_rewrite_date_of_departure_3: Message = bot.send_message(
                        callback.message.chat.id,
                        text=''.join(i_element for i_element in data['main_text'].values()))

                    crud.update_message_db(user_id_class=msg_to_dlt_rewrite_date_of_departure_3.from_user.id,
                                           chat_id_class=msg_to_dlt_rewrite_date_of_departure_3.chat.id,
                                           message_id_class=msg_to_dlt_rewrite_date_of_departure_3.message_id)

                    msg_to_dlt_rewrite_date_of_departure_4: Message = \
                        bot.send_message(callback.message.chat.id,
                                         text='Дата отъезда {0} раньше чем дата приезда {1}!!!'
                                              '\nВведите другую дату отъезда:'.
                                         format(str(date_of_departure)[:10], str(data['arrival_date'])[:10]))

                    crud.update_message_db(user_id_class=msg_to_dlt_rewrite_date_of_departure_4.from_user.id,
                                           chat_id_class=msg_to_dlt_rewrite_date_of_departure_4.chat.id,
                                           message_id_class=msg_to_dlt_rewrite_date_of_departure_4.message_id)

                    run_calendar(callback.from_user.id, callback.message.chat.id)

                    bot.set_state(callback.from_user.id, SearchStates.date_of_departure_rewrite,
                                  callback.message.chat.id)

                else:
                    bot.set_state(callback.from_user.id, SearchStates.hotels,
                                  callback.message.chat.id)

                    date_of_departure = datetime.datetime.strptime(callback.data, '%Y-%m-%d')

                    data['date_of_departure'] = date_of_departure
                    data['main_text']['date_of_departure'] = '\nДата отъезда - {}'. \
                        format(str(data['date_of_departure'])[:10])

                    logger.info('user_id - {0}; дата отъезда - {1}'.
                                format(callback.from_user.id, data['date_of_departure']))

                    msg_to_dlt_rewrite_date_of_departure_6: Message = bot.send_message(
                        callback.message.chat.id, text=''.
                        join(i_element for i_element in data['main_text'].values()))

                    crud.update_message_db(user_id_class=msg_to_dlt_rewrite_date_of_departure_6.from_user.id,
                                           chat_id_class=msg_to_dlt_rewrite_date_of_departure_6.chat.id,
                                           message_id_class=msg_to_dlt_rewrite_date_of_departure_6.message_id)

                    msg_to_dlt_rewrite_date_of_departure_7: Message = \
                        bot.send_message(callback.message.chat.id,
                                         text='Проверьте Ваш запрос.\nВсе верно?',
                                         reply_markup=create_yes_no_keyboard(user_id=callback.from_user.id,
                                                                             callback_data_yes='yes',
                                                                             callback_data_no='no'))

                    crud.update_message_db(user_id_class=msg_to_dlt_rewrite_date_of_departure_7.from_user.id,
                                           chat_id_class=msg_to_dlt_rewrite_date_of_departure_7.chat.id,
                                           message_id_class=msg_to_dlt_rewrite_date_of_departure_7.message_id)

    except ApiTelegramException as exception:
        logger.exception(
            'user_id - {0}; тип ошибки - {1}'.format(callback.from_user.id, exception))

        msg_to_dlt_mistake_1: Message = \
            bot.send_message(callback.message.chat.id,
                             text='Ошибка связи с Телеграм.\nНажмите меню для выбора дальнейших действий.')

        crud.update_message_db(user_id_class=msg_to_dlt_mistake_1.from_user.id,
                               chat_id_class=msg_to_dlt_mistake_1.chat.id,
                               message_id_class=msg_to_dlt_mistake_1.message_id)

    except (ReadTimeout, TimeoutError) as exception:
        logger.exception(
            'user_id - {0}; тип ошибки - {1}'.format(callback.from_user.id, exception))

        msg_to_dlt_mistake_2: Message = \
            bot.send_message(callback.message.chat.id,
                             text='Ошибка. Время ожидания истекло.\nНажмите меню для выбора дальнейших действий.')

        crud.update_message_db(user_id_class=msg_to_dlt_mistake_2.from_user.id,
                               chat_id_class=msg_to_dlt_mistake_2.chat.id,
                               message_id_class=msg_to_dlt_mistake_2.message_id)

    except (OperationalError, ValueError, KeyError, NameError) as exception:
        logger.exception(
            'user_id - {0}; тип ошибки - {1}'.format(callback.from_user.id, exception))

        msg_to_dlt_mistake_3: Message = \
            bot.send_message(callback.message.chat.id,
                             text='Ошибка доступа к Вашей базе запросов.\nНажмите меню для выбора дальнейших действий.')

        crud.update_message_db(user_id_class=msg_to_dlt_mistake_3.from_user.id,
                               chat_id_class=msg_to_dlt_mistake_3.chat.id,
                               message_id_class=msg_to_dlt_mistake_3.message_id)


@bot.callback_query_handler(func=None, state=SearchStates.date_of_departure)
def get_date_of_departure(callback: CallbackQuery) -> None:
    """
    Функция обрабатывает результат работы клавиатуры yes_no_keyboard, проверяет,
    чтобы выбранная дата отъезда была позже даты приезда, сохраняет полученные данные,
    запрашивает у пользователя минимальную цену за сутки.

    :param callback: Входящий запрос обратного вызова с кнопки клавиатуры yes_no_keyboard с датой отъезда
    :type callback: CallbackQuery
    """
    try:
        logger.info('user_id - {0}; callback.data - {1}'.format(callback.from_user.id, callback.data))

        logger.debug('user_id - {0}; вызов - функция get_date_of_departure({1})'.
                     format(callback.from_user.id, callback))

        crud.delete_message_db(user_id_class=callback.from_user.id,
                               chat_id_class=callback.message.chat.id)

        with bot.retrieve_data(callback.from_user.id, callback.message.chat.id) as data:

            if callback.data == 'no' or callback.message.text.find('None') != -1:
                logger.warning('user_id - {0}; дата отъезда {1} введена неверно'.
                               format(callback.from_user.id, callback.message.text[18:28]))

                msg_to_dlt_date_of_departure_1: Message = bot.send_message(
                    callback.message.chat.id,
                    text=''.join(i_element for i_element in data['main_text'].values()))

                crud.update_message_db(user_id_class=msg_to_dlt_date_of_departure_1.from_user.id,
                                       chat_id_class=msg_to_dlt_date_of_departure_1.chat.id,
                                       message_id_class=msg_to_dlt_date_of_departure_1.message_id)

                msg_to_dlt_date_of_departure_2: Message = bot.send_message(callback.message.chat.id,
                                                                           text='Введите другую дату отъезда:')

                crud.update_message_db(user_id_class=msg_to_dlt_date_of_departure_2.from_user.id,
                                       chat_id_class=msg_to_dlt_date_of_departure_2.chat.id,
                                       message_id_class=msg_to_dlt_date_of_departure_2.message_id)

                run_calendar(callback.from_user.id, callback.message.chat.id)

                bot.set_state(callback.from_user.id, SearchStates.date_of_departure, callback.message.chat.id)

            else:
                date_of_departure = datetime.datetime.strptime(callback.data, '%Y-%m-%d')

                if date_of_departure < data['arrival_date']:

                    logger.warning('user_id - {0}; дата отъезда {1} раньше чем дата приезда {2}.'.
                                   format(callback.from_user.id, str(date_of_departure)[:10],
                                          str(data['arrival_date'])[:10]))

                    msg_to_dlt_date_of_departure_3: Message = bot.send_message(
                        callback.message.chat.id,
                        text=''.join(i_element for i_element in data['main_text'].values()))

                    crud.update_message_db(user_id_class=msg_to_dlt_date_of_departure_3.from_user.id,
                                           chat_id_class=msg_to_dlt_date_of_departure_3.chat.id,
                                           message_id_class=msg_to_dlt_date_of_departure_3.message_id)

                    msg_to_dlt_date_of_departure_4: Message = bot.send_message(
                        callback.message.chat.id,
                        text='Дата отъезда {0} раньше чем дата приезда {1}!!!'
                             '\nВведите другую дату отъезда:'.
                        format(str(date_of_departure)[:10],
                               str(data['arrival_date'])[:10]))

                    crud.update_message_db(user_id_class=msg_to_dlt_date_of_departure_4.from_user.id,
                                           chat_id_class=msg_to_dlt_date_of_departure_4.chat.id,
                                           message_id_class=msg_to_dlt_date_of_departure_4.message_id)

                    run_calendar(callback.from_user.id, callback.message.chat.id)

                    bot.set_state(callback.from_user.id, SearchStates.date_of_departure, callback.message.chat.id)

                else:
                    bot.set_state(callback.from_user.id, SearchStates.min_price,
                                  callback.message.chat.id)

                    date_of_departure = datetime.datetime.strptime(callback.data, '%Y-%m-%d')

                    data['date_of_departure'] = date_of_departure
                    data['main_text']['date_of_departure'] = '\nДата отъезда - {}'. \
                        format(str(data['date_of_departure'])[:10])

                    logger.info('user_id - {0}; дата отъезда - {1}'.
                                format(callback.from_user.id, data['date_of_departure']))

                    msg_to_dlt_date_of_departure_5: Message = bot.send_message(
                        callback.message.chat.id, text=''.
                        join(i_element for i_element in data['main_text'].values()))

                    crud.update_message_db(user_id_class=msg_to_dlt_date_of_departure_5.from_user.id,
                                           chat_id_class=msg_to_dlt_date_of_departure_5.chat.id,
                                           message_id_class=msg_to_dlt_date_of_departure_5.message_id)

                    msg_to_dlt_date_of_departure_6: Message = bot.send_message(
                        callback.message.chat.id, text='Введите минимальную цену проживания за сутки в $:')

                    crud.update_message_db(user_id_class=msg_to_dlt_date_of_departure_6.from_user.id,
                                           chat_id_class=msg_to_dlt_date_of_departure_6.chat.id,
                                           message_id_class=msg_to_dlt_date_of_departure_6.message_id)

    except ApiTelegramException as exception:
        logger.exception(
            'user_id - {0}; тип ошибки - {1}'.format(callback.from_user.id, exception))

        msg_to_dlt_mistake_1: Message = \
            bot.send_message(callback.message.chat.id,
                             text='Ошибка связи с Телеграм.\nНажмите меню для выбора дальнейших действий.')

        crud.update_message_db(user_id_class=msg_to_dlt_mistake_1.from_user.id,
                               chat_id_class=msg_to_dlt_mistake_1.chat.id,
                               message_id_class=msg_to_dlt_mistake_1.message_id)

    except (ReadTimeout, TimeoutError) as exception:
        logger.exception(
            'user_id - {0}; тип ошибки - {1}'.format(callback.from_user.id, exception))

        msg_to_dlt_mistake_2: Message = \
            bot.send_message(callback.message.chat.id,
                             text='Ошибка. Время ожидания истекло.\nНажмите меню для выбора дальнейших действий.')

        crud.update_message_db(user_id_class=msg_to_dlt_mistake_2.from_user.id,
                               chat_id_class=msg_to_dlt_mistake_2.chat.id,
                               message_id_class=msg_to_dlt_mistake_2.message_id)

    except (OperationalError, ValueError, KeyError, NameError) as exception:
        logger.exception(
            'user_id - {0}; тип ошибки - {1}'.format(callback.from_user.id, exception))

        msg_to_dlt_mistake_3: Message = \
            bot.send_message(callback.message.chat.id,
                             text='Ошибка доступа к Вашей базе запросов.\nНажмите меню для выбора дальнейших действий.')

        crud.update_message_db(user_id_class=msg_to_dlt_mistake_3.from_user.id,
                               chat_id_class=msg_to_dlt_mistake_3.chat.id,
                               message_id_class=msg_to_dlt_mistake_3.message_id)


@bot.callback_query_handler(func=None, state=SearchStates.arrival_date_rewrite)
def get_rewrite_arrival_date(callback: CallbackQuery) -> None:
    """
    Функция обрабатывает результат работы клавиатуры yes_no_keyboard, проверяет,
    чтобы измененная дата была позже текущей, сохраняет полученные данные.

    :param callback: Входящий запрос обратного вызова с кнопки клавиатуры yes_no_keyboard
    :type callback: CallbackQuery
    """
    try:
        logger.info('user_id - {0}; callback.data - {1}'.format(callback.from_user.id,
                                                                callback.data))

        logger.debug('user_id - {0}; вызов - функция get_rewrite_arrival_date({1})'.
                     format(callback.from_user.id, callback))

        crud.delete_message_db(user_id_class=callback.from_user.id,
                               chat_id_class=callback.message.chat.id)

        with bot.retrieve_data(callback.from_user.id,
                               callback.message.chat.id) as data:

            if callback.data == 'no' or callback.message.text.find('None') != -1:
                logger.warning('user_id - {0}; дата приезда {1} введена неверно'.
                               format(callback.from_user.id,
                                      callback.message.text[18:28]))

                msg_to_dlt_get_rewrite_arrival_date_1: Message = bot.send_message(
                    callback.message.chat.id, text=''.join(
                        i_element for i_element in data['main_text'].values()))

                crud.update_message_db(user_id_class=msg_to_dlt_get_rewrite_arrival_date_1.from_user.id,
                                       chat_id_class=msg_to_dlt_get_rewrite_arrival_date_1.chat.id,
                                       message_id_class=msg_to_dlt_get_rewrite_arrival_date_1.message_id)

                msg_to_dlt_get_rewrite_arrival_date_2: Message = \
                    bot.send_message(
                        callback.message.chat.id,
                        text='Введите другую дату приезда:')

                crud.update_message_db(user_id_class=msg_to_dlt_get_rewrite_arrival_date_2.from_user.id,
                                       chat_id_class=msg_to_dlt_get_rewrite_arrival_date_2.chat.id,
                                       message_id_class=msg_to_dlt_get_rewrite_arrival_date_2.message_id)

                run_calendar(callback.from_user.id,
                             callback.message.chat.id)

                bot.set_state(callback.from_user.id,
                              SearchStates.arrival_date_rewrite,
                              callback.message.chat.id)

            else:
                current_date = datetime.datetime.now()

                arrival_date = datetime.datetime.strptime(callback.data, '%Y-%m-%d')

                date_of_departure = data['date_of_departure']

                if arrival_date < current_date:
                    logger.warning('user_id - {0}; дата приезда {1} раньше чем текущая дата {2}.'.
                                   format(callback.from_user.id,
                                          str(arrival_date)[:10], str(current_date)[:10]))

                    msg_to_dlt_get_rewrite_arrival_date_3: Message = bot.send_message(
                        callback.message.chat.id,
                        text=''.join(i_element for i_element in
                                     data['main_text'].values()))

                    crud.update_message_db(user_id_class=msg_to_dlt_get_rewrite_arrival_date_3.from_user.id,
                                           chat_id_class=msg_to_dlt_get_rewrite_arrival_date_3.chat.id,
                                           message_id_class=msg_to_dlt_get_rewrite_arrival_date_3.message_id)

                    msg_to_dlt_get_rewrite_arrival_date_4: Message = \
                        bot.send_message(callback.message.chat.id,
                                         text='Дата приезда {0} раньше чем текущая дата {1}!!!'
                                              '\nВведите другую дату приезда:'.
                                         format(str(arrival_date)[:10], str(current_date)[:10]))

                    crud.update_message_db(user_id_class=msg_to_dlt_get_rewrite_arrival_date_4.from_user.id,
                                           chat_id_class=msg_to_dlt_get_rewrite_arrival_date_4.chat.id,
                                           message_id_class=msg_to_dlt_get_rewrite_arrival_date_4.message_id)

                    run_calendar(callback.from_user.id,
                                 callback.message.chat.id)

                    bot.set_state(callback.from_user.id,
                                  SearchStates.arrival_date_rewrite,
                                  callback.message.chat.id)

                elif arrival_date > date_of_departure:
                    logger.warning('user_id - {0}; дата приезда {1} позже чем дата отъезда {2}.'.
                                   format(callback.from_user.id, str(arrival_date)[:10],
                                          str(date_of_departure)[:10]))

                    msg_to_dlt_get_rewrite_arrival_date_5: Message = bot.send_message(
                        callback.message.chat.id,
                        text=''.join(i_element for i_element in data['main_text'].values()))

                    crud.update_message_db(user_id_class=msg_to_dlt_get_rewrite_arrival_date_5.from_user.id,
                                           chat_id_class=msg_to_dlt_get_rewrite_arrival_date_5.chat.id,
                                           message_id_class=msg_to_dlt_get_rewrite_arrival_date_5.message_id)

                    msg_to_dlt_get_rewrite_arrival_date_6: Message = \
                        bot.send_message(
                            callback.message.chat.id,
                            text='Дата приезда {0} позже чем дата отъезда {1}!!!'
                                 '\nВведите другую дату приезда:'.
                            format(str(arrival_date)[:10], str(date_of_departure)[:10]))

                    crud.update_message_db(user_id_class=msg_to_dlt_get_rewrite_arrival_date_6.from_user.id,
                                           chat_id_class=msg_to_dlt_get_rewrite_arrival_date_6.chat.id,
                                           message_id_class=msg_to_dlt_get_rewrite_arrival_date_6.message_id)

                    run_calendar(callback.from_user.id,
                                 callback.message.chat.id)

                    bot.set_state(callback.from_user.id,
                                  SearchStates.arrival_date_rewrite,
                                  callback.message.chat.id)

                else:
                    bot.set_state(callback.from_user.id,
                                  SearchStates.hotels,
                                  callback.message.chat.id)

                    arrival_date = datetime.datetime.strptime(callback.data, '%Y-%m-%d')

                    data['arrival_date'] = arrival_date

                    logger.info('user_id - {0}; дата приезда - {1}'.
                                format(callback.from_user.id,
                                       data['arrival_date']))

                    data['main_text']['arrival_date'] = '\nДата приезда - {}'. \
                        format(str(data['arrival_date'])[:10])

                    msg_to_dlt_get_rewrite_arrival_date_7: Message = bot.send_message(
                        callback.message.chat.id,
                        text=''.join(i_element for i_element in data['main_text'].values()))

                    crud.update_message_db(user_id_class=msg_to_dlt_get_rewrite_arrival_date_7.from_user.id,
                                           chat_id_class=msg_to_dlt_get_rewrite_arrival_date_7.chat.id,
                                           message_id_class=msg_to_dlt_get_rewrite_arrival_date_7.message_id)

                    msg_to_dlt_get_rewrite_arrival_date_8: Message = \
                        bot.send_message(callback.message.chat.id,
                                         text='Проверьте Ваш запрос.\nВсе верно?',
                                         reply_markup=create_yes_no_keyboard(
                                             user_id=callback.from_user.id,
                                             callback_data_yes='yes', callback_data_no='no'))

                    crud.update_message_db(user_id_class=msg_to_dlt_get_rewrite_arrival_date_8.from_user.id,
                                           chat_id_class=msg_to_dlt_get_rewrite_arrival_date_8.chat.id,
                                           message_id_class=msg_to_dlt_get_rewrite_arrival_date_8.message_id)

    except ApiTelegramException as exception:
        logger.exception(
            'user_id - {0}; тип ошибки - {1}'.format(callback.from_user.id, exception))

        msg_to_dlt_mistake_1: Message = \
            bot.send_message(callback.message.chat.id,
                             text='Ошибка связи с Телеграм.\nНажмите меню для выбора дальнейших действий.')

        crud.update_message_db(user_id_class=msg_to_dlt_mistake_1.from_user.id,
                               chat_id_class=msg_to_dlt_mistake_1.chat.id,
                               message_id_class=msg_to_dlt_mistake_1.message_id)

    except (ReadTimeout, TimeoutError) as exception:
        logger.exception(
            'user_id - {0}; тип ошибки - {1}'.format(callback.from_user.id, exception))

        msg_to_dlt_mistake_2: Message = \
            bot.send_message(callback.message.chat.id,
                             text='Ошибка. Время ожидания истекло.\nНажмите меню для выбора дальнейших действий.')

        crud.update_message_db(user_id_class=msg_to_dlt_mistake_2.from_user.id,
                               chat_id_class=msg_to_dlt_mistake_2.chat.id,
                               message_id_class=msg_to_dlt_mistake_2.message_id)

    except (OperationalError, ValueError, KeyError, NameError) as exception:
        logger.exception(
            'user_id - {0}; тип ошибки - {1}'.format(callback.from_user.id, exception))

        msg_to_dlt_mistake_3: Message = \
            bot.send_message(callback.message.chat.id,
                             text='Ошибка доступа к Вашей базе запросов.\nНажмите меню для выбора дальнейших действий.')

        crud.update_message_db(user_id_class=msg_to_dlt_mistake_3.from_user.id,
                               chat_id_class=msg_to_dlt_mistake_3.chat.id,
                               message_id_class=msg_to_dlt_mistake_3.message_id)


@bot.callback_query_handler(func=None, state=SearchStates.arrival_date)
def get_arrival_date(callback: CallbackQuery) -> None:
    """
    Функция обрабатывает результат работы клавиатуры yes_no_keyboard, проверяет,
    чтобы выбранная дата была позже текущей, сохраняет полученные данные,
    запрашивает у пользователя дату отъезда.

    :param callback: Входящий запрос обратного вызова с кнопки клавиатуры yes_no_keyboard с датой приезда
    :type callback: CallbackQuery
    """
    try:
        logger.debug('user_id - {0}; вызов - функция get_arrival_date({1})'.
                     format(callback.from_user.id, callback))

        logger.info('user_id - {0}; callback.data - {1}'.format(callback.from_user.id, callback.data))

        crud.delete_message_db(user_id_class=callback.from_user.id,
                               chat_id_class=callback.message.chat.id)

        with bot.retrieve_data(callback.from_user.id, callback.message.chat.id) as data:

            if callback.data == 'no' or callback.message.text.find('None') != -1:
                logger.warning('user_id - {0}; дата приезда {1} введена неверно'.
                               format(callback.from_user.id, callback.message.text[18:28]))

                msg_to_dlt_get_arrival_date_1: Message = bot.send_message(
                    callback.message.chat.id, text=''.join(i_element for i_element in data['main_text'].values()))

                crud.update_message_db(user_id_class=msg_to_dlt_get_arrival_date_1.from_user.id,
                                       chat_id_class=msg_to_dlt_get_arrival_date_1.chat.id,
                                       message_id_class=msg_to_dlt_get_arrival_date_1.message_id)

                msg_to_dlt_get_arrival_date_2: Message = bot.send_message(callback.message.chat.id,
                                                                          text='Введите другую дату приезда:')

                crud.update_message_db(user_id_class=msg_to_dlt_get_arrival_date_2.from_user.id,
                                       chat_id_class=msg_to_dlt_get_arrival_date_2.chat.id,
                                       message_id_class=msg_to_dlt_get_arrival_date_2.message_id)

                run_calendar(callback.from_user.id, callback.message.chat.id)

                bot.set_state(callback.from_user.id, SearchStates.arrival_date, callback.message.chat.id)

            else:
                current_date = datetime.datetime.now()

                arrival_date = datetime.datetime.strptime(callback.data, '%Y-%m-%d')

                if arrival_date < current_date:
                    logger.warning('user_id - {0}; дата приезда {1} раньше чем текущая дата {2}.'.
                                   format(callback.from_user.id, str(arrival_date)[:10],
                                          str(current_date)[:10]))

                    msg_to_dlt_get_arrival_date_3: Message = bot.send_message(
                        callback.message.chat.id,
                        text=''.join(i_element for i_element in data['main_text'].values()))

                    crud.update_message_db(user_id_class=msg_to_dlt_get_arrival_date_3.from_user.id,
                                           chat_id_class=msg_to_dlt_get_arrival_date_3.chat.id,
                                           message_id_class=msg_to_dlt_get_arrival_date_3.message_id)

                    msg_to_dlt_get_arrival_date_4: Message = bot.send_message(
                        callback.message.chat.id, text='Дата приезда {0} раньше чем текущая дата {1}!!!'
                                                       '\nВведите другую дату приезда:'.
                        format(str(arrival_date)[:10],
                               str(current_date)[:10]))

                    crud.update_message_db(user_id_class=msg_to_dlt_get_arrival_date_4.from_user.id,
                                           chat_id_class=msg_to_dlt_get_arrival_date_4.chat.id,
                                           message_id_class=msg_to_dlt_get_arrival_date_4.message_id)

                    run_calendar(callback.from_user.id, callback.message.chat.id)

                    bot.set_state(callback.from_user.id, SearchStates.arrival_date, callback.message.chat.id)

                else:
                    bot.set_state(callback.from_user.id, SearchStates.date_of_departure,
                                  callback.message.chat.id)

                    arrival_date = datetime.datetime.strptime(callback.data, '%Y-%m-%d')

                    data['arrival_date'] = arrival_date

                    data['main_text']['arrival_date'] = '\nДата приезда - {}'. \
                        format(str(data['arrival_date'])[:10])

                    logger.info('user_id - {0}; дата приезда - {1}'.
                                format(callback.from_user.id, data['arrival_date']))

                    msg_to_dlt_get_arrival_date_5: Message = bot.send_message(
                        callback.message.chat.id,
                        text=''.join(i_element for i_element in data['main_text'].values()))

                    crud.update_message_db(user_id_class=msg_to_dlt_get_arrival_date_5.from_user.id,
                                           chat_id_class=msg_to_dlt_get_arrival_date_5.chat.id,
                                           message_id_class=msg_to_dlt_get_arrival_date_5.message_id)

                    msg_to_dlt_get_arrival_date_6: Message = bot.send_message(callback.message.chat.id,
                                                                              text='Введите дату отъезда:')

                    crud.update_message_db(user_id_class=msg_to_dlt_get_arrival_date_6.from_user.id,
                                           chat_id_class=msg_to_dlt_get_arrival_date_6.chat.id,
                                           message_id_class=msg_to_dlt_get_arrival_date_6.message_id)

                    run_calendar(callback.from_user.id, callback.message.chat.id)

    except ApiTelegramException as exception:
        logger.exception(
            'user_id - {0}; тип ошибки - {1}'.format(callback.from_user.id, exception))

        msg_to_dlt_mistake_1: Message = \
            bot.send_message(callback.message.chat.id,
                             text='Ошибка связи с Телеграм.\nНажмите меню для выбора дальнейших действий.')

        crud.update_message_db(user_id_class=msg_to_dlt_mistake_1.from_user.id,
                               chat_id_class=msg_to_dlt_mistake_1.chat.id,
                               message_id_class=msg_to_dlt_mistake_1.message_id)

    except (ReadTimeout, TimeoutError) as exception:
        logger.exception(
            'user_id - {0}; тип ошибки - {1}'.format(callback.from_user.id, exception))

        msg_to_dlt_mistake_2: Message = \
            bot.send_message(callback.message.chat.id,
                             text='Ошибка. Время ожидания истекло.\nНажмите меню для выбора дальнейших действий.')

        crud.update_message_db(user_id_class=msg_to_dlt_mistake_2.from_user.id,
                               chat_id_class=msg_to_dlt_mistake_2.chat.id,
                               message_id_class=msg_to_dlt_mistake_2.message_id)

    except (OperationalError, ValueError, KeyError, NameError) as exception:
        logger.exception(
            'user_id - {0}; тип ошибки - {1}'.format(callback.from_user.id, exception))

        msg_to_dlt_mistake_3: Message = \
            bot.send_message(callback.message.chat.id,
                             text='Ошибка доступа к Вашей базе запросов.\nНажмите меню для выбора дальнейших действий.')

        crud.update_message_db(user_id_class=msg_to_dlt_mistake_3.from_user.id,
                               chat_id_class=msg_to_dlt_mistake_3.chat.id,
                               message_id_class=msg_to_dlt_mistake_3.message_id)


@bot.callback_query_handler(func=None, state=SearchStates.refined_city_rewrite)
def get_rewrite_refined_city(callback: CallbackQuery) -> None:
    """
    Функция обрабатывает результат работы клавиатуры eponymous_cities_keyboard,
    сохраняет уточненные данные(id уточненного города, название уточненного города),
    запрашивает у пользователя дату приезда и вызывает клавиатуру подтвержения yes_no_keyboard.

    :param callback: Входящий запрос обратного вызова с кнопки клавиатуры eponymous_cities_keyboard
    :type callback: CallbackQuery
    """
    try:
        logger.info('user_id - {0}; callback.data - {1}'.format(callback.from_user.id, callback.data))

        logger.debug('user_id - {0}; вызов - функция get_rewrite_refined_city({1})'.
                     format(callback.from_user.id, callback.from_user.id))

        crud.delete_message_db(user_id_class=callback.from_user.id,
                               chat_id_class=callback.message.chat.id)

        bot.set_state(callback.from_user.id, SearchStates.hotels, callback.message.chat.id)

        refined_city_id = ''.join([element for element in callback.data if element.isdigit()])

        refined_city_name = ''.join([element for element in callback.data if element.isdigit() is False])

        with bot.retrieve_data(callback.from_user.id, callback.message.chat.id) as data_rewrite_refined_city:
            data_rewrite_refined_city['refined_city'] = [refined_city_id, refined_city_name]
            data_rewrite_refined_city['main_text']['city'] = '\nГород - {}'.format(
                data_rewrite_refined_city['refined_city'][1])

            logger.info('user_id - {0}; уточненный город - {1}'.format(callback.from_user.id,
                                                                       data_rewrite_refined_city['refined_city']))

            msg_to_dlt_get_rewrite_refined_city_1: Message = bot.send_message(callback.message.chat.id,
                                                                              text=''.join(
                                                                                  i_element for i_element in
                                                                                  data_rewrite_refined_city[
                                                                                      'main_text'].values()))

            crud.update_message_db(user_id_class=msg_to_dlt_get_rewrite_refined_city_1.from_user.id,
                                   chat_id_class=msg_to_dlt_get_rewrite_refined_city_1.chat.id,
                                   message_id_class=msg_to_dlt_get_rewrite_refined_city_1.message_id)

            msg_to_dlt_get_rewrite_refined_city_2: Message = \
                bot.send_message(
                    callback.message.chat.id,
                    text='Проверьте Ваш запрос.\nВсе верно?',
                    reply_markup=create_yes_no_keyboard(
                        user_id=callback.from_user.id,
                        callback_data_yes='yes',
                        callback_data_no='no'))

            crud.update_message_db(user_id_class=msg_to_dlt_get_rewrite_refined_city_2.from_user.id,
                                   chat_id_class=msg_to_dlt_get_rewrite_refined_city_2.chat.id,
                                   message_id_class=msg_to_dlt_get_rewrite_refined_city_2.message_id)

    except ApiTelegramException as exception:
        logger.exception(
            'user_id - {0}; тип ошибки - {1}'.format(callback.from_user.id, exception))

        msg_to_dlt_mistake_1: Message = \
            bot.send_message(callback.message.chat.id,
                             text='Ошибка связи с Телеграм.\nНажмите меню для выбора дальнейших действий.')

        crud.update_message_db(user_id_class=msg_to_dlt_mistake_1.from_user.id,
                               chat_id_class=msg_to_dlt_mistake_1.chat.id,
                               message_id_class=msg_to_dlt_mistake_1.message_id)

    except (ReadTimeout, TimeoutError) as exception:
        logger.exception(
            'user_id - {0}; тип ошибки - {1}'.format(callback.from_user.id, exception))

        msg_to_dlt_mistake_2: Message = \
            bot.send_message(callback.message.chat.id,
                             text='Ошибка. Время ожидания истекло.\nНажмите меню для выбора дальнейших действий.')

        crud.update_message_db(user_id_class=msg_to_dlt_mistake_2.from_user.id,
                               chat_id_class=msg_to_dlt_mistake_2.chat.id,
                               message_id_class=msg_to_dlt_mistake_2.message_id)

    except (OperationalError, ValueError, KeyError, NameError) as exception:
        logger.exception(
            'user_id - {0}; тип ошибки - {1}'.format(callback.from_user.id, exception))

        msg_to_dlt_mistake_3: Message = \
            bot.send_message(callback.message.chat.id,
                             text='Ошибка доступа к Вашей базе запросов.\nНажмите меню для выбора дальнейших действий.')

        crud.update_message_db(user_id_class=msg_to_dlt_mistake_3.from_user.id,
                               chat_id_class=msg_to_dlt_mistake_3.chat.id,
                               message_id_class=msg_to_dlt_mistake_3.message_id)


@bot.callback_query_handler(func=None, state=SearchStates.refined_city)
def get_refined_city(callback: CallbackQuery) -> None:
    """
    Функция обрабатывает результат работы клавиатуры eponymous_cities_keyboard,
    сохраняет полученные данные(id уточненного города, название уточненного города),
    запрашивает у пользователя дату приезда.

    :param callback: Входящий запрос обратного вызова с кнопки клавиатуры eponymous_cities_keyboard
     с уточненным название города
    :type callback: CallbackQuery
    """
    try:
        logger.info('user_id - {0}; callback.data - {1}'.format(callback.from_user.id, callback.data))

        logger.debug('user_id - {0}; вызов - функция get_refined_city({1})'.
                     format(callback.from_user.id, callback))

        crud.delete_message_db(user_id_class=callback.from_user.id,
                               chat_id_class=callback.message.chat.id)

        bot.set_state(callback.from_user.id, SearchStates.arrival_date, callback.message.chat.id)

        refined_city_id = ''.join([element for element in callback.data if element.isdigit()])

        refined_city_name = ''.join([element for element in callback.data if element.isdigit() is False])

        with bot.retrieve_data(callback.from_user.id, callback.message.chat.id) as data:
            data['refined_city'] = [refined_city_id, refined_city_name]
            data['main_text']['city'] = '\nГород - {}'.format(data['refined_city'][1])

            logger.info('user_id - {0}; уточненный город - {1}'.format(callback.from_user.id, data['refined_city']))

            msg_to_dlt_get_refined_city_1: Message = bot.send_message(callback.message.chat.id,
                                                                      text=''.join(i_element for i_element in
                                                                                   data['main_text'].values()))

            crud.update_message_db(user_id_class=msg_to_dlt_get_refined_city_1.from_user.id,
                                   chat_id_class=msg_to_dlt_get_refined_city_1.chat.id,
                                   message_id_class=msg_to_dlt_get_refined_city_1.message_id)

            msg_to_dlt_get_refined_city_2: Message = bot.send_message(callback.message.chat.id,
                                                                      text='Введите дату приезда:')

            crud.update_message_db(user_id_class=msg_to_dlt_get_refined_city_2.from_user.id,
                                   chat_id_class=msg_to_dlt_get_refined_city_2.chat.id,
                                   message_id_class=msg_to_dlt_get_refined_city_2.message_id)

            run_calendar(callback.from_user.id, callback.message.chat.id)

    except ApiTelegramException as exception:
        logger.exception(
            'user_id - {0}; тип ошибки - {1}'.format(callback.from_user.id, exception))

        msg_to_dlt_mistake_1: Message = \
            bot.send_message(callback.message.chat.id,
                             text='Ошибка связи с Телеграм.\nНажмите меню для выбора дальнейших действий.')

        crud.update_message_db(user_id_class=msg_to_dlt_mistake_1.from_user.id,
                               chat_id_class=msg_to_dlt_mistake_1.chat.id,
                               message_id_class=msg_to_dlt_mistake_1.message_id)

    except (ReadTimeout, TimeoutError) as exception:
        logger.exception(
            'user_id - {0}; тип ошибки - {1}'.format(callback.from_user.id, exception))

        msg_to_dlt_mistake_2: Message = \
            bot.send_message(callback.message.chat.id,
                             text='Ошибка. Время ожидания истекло.\nНажмите меню для выбора дальнейших действий.')

        crud.update_message_db(user_id_class=msg_to_dlt_mistake_2.from_user.id,
                               chat_id_class=msg_to_dlt_mistake_2.chat.id,
                               message_id_class=msg_to_dlt_mistake_2.message_id)

    except (OperationalError, ValueError, KeyError, NameError) as exception:
        logger.exception(
            'user_id - {0}; тип ошибки - {1}'.format(callback.from_user.id, exception))

        msg_to_dlt_mistake_3: Message = \
            bot.send_message(callback.message.chat.id,
                             text='Ошибка доступа к Вашей базе запросов.\nНажмите меню для выбора дальнейших действий.')

        crud.update_message_db(user_id_class=msg_to_dlt_mistake_3.from_user.id,
                               chat_id_class=msg_to_dlt_mistake_3.chat.id,
                               message_id_class=msg_to_dlt_mistake_3.message_id)


@bot.message_handler(state=SearchStates.city_rewrite)
def get_rewrite_city(message: Message) -> None:
    """
    Функция получает от пользователя измененное название города, сохраняет это значение,
    отправляет запрос с названием города на сайт rapidapi.com для поиска одноименных или похожих названий и
    выводит клавиатуру eponymous_cities_keyboard с одноименными городами для уточнения, если города,
    который ввел пользователь, не существует, предлагает пользователю ввести другой город.

    :param message: Сообщение от пользователя
    :type message: Message
    :raise ConnectionError: если тип результата работы функции
    find_eponymous_cities(method_endswith: str, method_type: str, city: str) будет int
    """
    try:
        logger.debug('user_id - {0}; вызов - функция get_rewrite_city({1})'.
                     format(message.from_user.id, message))

        crud.update_message_db(user_id_class=message.from_user.id,
                               chat_id_class=message.chat.id,
                               message_id_class=message.message_id)

        crud.delete_message_db(user_id_class=message.from_user.id,
                               chat_id_class=message.chat.id)

        bot.set_state(message.from_user.id, SearchStates.refined_city_rewrite, message.chat.id)

        with bot.retrieve_data(message.from_user.id, message.chat.id) as data_rewrite_city:
            data_rewrite_city['city'] = message.text
            data_rewrite_city['main_text']['city'] = '\nГород - {}'.format(data_rewrite_city['city'])

            logger.info('user_id - {0}; город - {1}'.format(message.from_user.id, data_rewrite_city['city']))

            msg_to_dlt_get_rewrite_city_1: Message = bot.send_message(message.chat.id,
                                                                      text=''.join(
                                                                          i_element for i_element in
                                                                          data_rewrite_city['main_text'].values()))

            crud.update_message_db(user_id_class=msg_to_dlt_get_rewrite_city_1.from_user.id,
                                   chat_id_class=msg_to_dlt_get_rewrite_city_1.chat.id,
                                   message_id_class=msg_to_dlt_get_rewrite_city_1.message_id)
            try:
                eponymous_cities: Dict | int = find_eponymous_cities(user_id=message.from_user.id,
                                                                     method_endswith='locations/v3/search',
                                                                     method_type='GET',
                                                                     city=data_rewrite_city['city'])

                if type(eponymous_cities) == int:
                    raise ConnectionError

                else:
                    if len(eponymous_cities) == 0:
                        logger.warning('user_id - {}; одноименных и похожих городов не найдено'.
                                       format(message.from_user.id))

                        msg_to_dlt_get_rewrite_city_2: Message = bot.send_message(
                            message.chat.id, text='Город с названием {} не найден.'
                                                  '\nВведите другой город:'.format(message.text))

                        crud.update_message_db(user_id_class=msg_to_dlt_get_rewrite_city_2.from_user.id,
                                               chat_id_class=msg_to_dlt_get_rewrite_city_2.chat.id,
                                               message_id_class=msg_to_dlt_get_rewrite_city_2.message_id)

                        bot.set_state(message.from_user.id, SearchStates.city_rewrite, message.chat.id)

                    else:
                        create_eponymous_cities_keyboard(message.from_user.id, message.chat.id,
                                                         eponymous_cities)

            except (AttributeError, KeyError) as exc:
                logger.exception('user_id - {0}; тип ошибки - {1}'.format(message.from_user.id, exc))

                msg_to_dlt_mistake_5: Message = \
                    bot.send_message(message.chat.id,
                                     text='Ошибка связи с сайтом.'
                                          '\nНажмите меню для выбора дальнейших действий.')

                crud.update_message_db(user_id_class=msg_to_dlt_mistake_5.from_user.id,
                                       chat_id_class=msg_to_dlt_mistake_5.chat.id,
                                       message_id_class=msg_to_dlt_mistake_5.message_id)

            except (ReadTimeout, TimeoutError) as exc:
                logger.exception('user_id - {0}; тип ошибки - {1}'.format(message.from_user.id, exc))

                msg_to_dlt_mistake_6: Message = \
                    bot.send_message(message.chat.id,
                                     text='Ошибка. Время ожидания истекло.'
                                          '\nНажмите меню для выбора дальнейших действий.')

                crud.update_message_db(user_id_class=msg_to_dlt_mistake_6.from_user.id,
                                       chat_id_class=msg_to_dlt_mistake_6.chat.id,
                                       message_id_class=msg_to_dlt_mistake_6.message_id)

            except ApiTelegramException as exc:
                logger.exception('user_id - {0}; тип ошибки - {1}'.format(message.from_user.id, exc))

                msg_to_dlt_mistake_7: Message = \
                    bot.send_message(message.chat.id,
                                     text='Ошибка связи с Телеграм.'
                                          '\nНажмите меню для выбора дальнейших действий.')

                crud.update_message_db(user_id_class=msg_to_dlt_mistake_7.from_user.id,
                                       chat_id_class=msg_to_dlt_mistake_7.chat.id,
                                       message_id_class=msg_to_dlt_mistake_7.message_id)

            except ConnectionError as exc:
                logger.exception('user_id - {0}; тип ошибки - {1}'.format(message.from_user.id, exc))

                msg_to_dlt_mistake_8: Message = \
                    bot.send_message(message.chat.id,
                                     text='Ошибка связи с сайтом.'
                                          '\nНажмите меню для выбора дальнейших действий.')

                crud.update_message_db(user_id_class=msg_to_dlt_mistake_8.from_user.id,
                                       chat_id_class=msg_to_dlt_mistake_8.chat.id,
                                       message_id_class=msg_to_dlt_mistake_8.message_id)

    except ApiTelegramException as exception:
        logger.exception(
            'user_id - {0}; тип ошибки - {1}'.format(message.from_user.id, exception))

        msg_to_dlt_mistake_1: Message = \
            bot.send_message(message.chat.id,
                             text='Ошибка связи с Телеграм.\nНажмите меню для выбора дальнейших действий.')

        crud.update_message_db(user_id_class=msg_to_dlt_mistake_1.from_user.id,
                               chat_id_class=msg_to_dlt_mistake_1.chat.id,
                               message_id_class=msg_to_dlt_mistake_1.message_id)

    except (ReadTimeout, TimeoutError) as exception:
        logger.exception(
            'user_id - {0}; тип ошибки - {1}'.format(message.from_user.id, exception))

        msg_to_dlt_mistake_2: Message = \
            bot.send_message(message.chat.id,
                             text='Ошибка. Время ожидания истекло.\nНажмите меню для выбора дальнейших действий.')

        crud.update_message_db(user_id_class=msg_to_dlt_mistake_2.from_user.id,
                               chat_id_class=msg_to_dlt_mistake_2.chat.id,
                               message_id_class=msg_to_dlt_mistake_2.message_id)

    except (OperationalError, ValueError, KeyError, NameError) as exception:
        logger.exception(
            'user_id - {0}; тип ошибки - {1}'.format(message.from_user.id, exception))

        msg_to_dlt_mistake_3: Message = \
            bot.send_message(message.chat.id,
                             text='Ошибка доступа к Вашей базе запросов.\nНажмите меню для выбора дальнейших действий.')

        crud.update_message_db(user_id_class=msg_to_dlt_mistake_3.from_user.id,
                               chat_id_class=msg_to_dlt_mistake_3.chat.id,
                               message_id_class=msg_to_dlt_mistake_3.message_id)


@bot.message_handler(state=SearchStates.city)
def get_city(message: Message) -> None:
    """
    Функция получает от пользователя название города, сохраняет это значение,
    отправляет запрос с названием города на сайт rapidapi.com для поиска одноименных или
    похожих названий и выводит клавиатуру eponymous_cities_keyboard
    с одноименными городами для уточнения, если города, который ввел пользователь, не существует,
    предлагает пользователю ввести другой город.

    :param message: Сообщение с названием города полученное от пользователя
    :type message: Message
    :raise ConnectionError: если тип результата работы функции
    find_eponymous_cities(method_endswith: str, method_type: str, city: str) будет int
    """
    try:
        logger.debug('user_id - {0}; вызов - функция get_city({1})'.format(message.from_user.id, message))

        crud.update_message_db(user_id_class=message.from_user.id,
                               chat_id_class=message.chat.id,
                               message_id_class=message.message_id)

        crud.delete_message_db(user_id_class=message.from_user.id,
                               chat_id_class=message.chat.id)

        bot.set_state(message.from_user.id, SearchStates.refined_city, message.chat.id)

        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['city'] = message.text
            data['main_text'] = {}
            data['main_text']['start'] = 'Ваш запрос:'
            data['main_text']['city'] = '\nГород - {}'.format(data['city'])

            logger.info('user_id - {0}; город - {1}'.format(message.from_user.id, data['city']))

            msg_to_dlt_get_city_1: Message = bot.send_message(message.chat.id,
                                                              text=''.join(
                                                                  i_element for i_element in
                                                                  data['main_text'].values()))

            crud.update_message_db(user_id_class=msg_to_dlt_get_city_1.from_user.id,
                                   chat_id_class=msg_to_dlt_get_city_1.chat.id,
                                   message_id_class=msg_to_dlt_get_city_1.message_id)
            try:
                eponymous_cities: Dict | int = find_eponymous_cities(user_id=message.from_user.id,
                                                                     method_endswith='locations/v3/search',
                                                                     method_type='GET', city=data['city'])

                if type(eponymous_cities) == int:
                    raise ConnectionError

                else:
                    if len(eponymous_cities) == 0:
                        logger.warning('user_id - {}; одноименных и похожих городов не найдено'.
                                       format(message.from_user.id))

                        msg_to_dlt_get_city_2: Message = bot.send_message(message.chat.id,
                                                                          text='Город с названием {} не найден.'
                                                                               '\nВведите другой город:'.
                                                                          format(message.text))

                        crud.update_message_db(user_id_class=msg_to_dlt_get_city_2.from_user.id,
                                               chat_id_class=msg_to_dlt_get_city_2.chat.id,
                                               message_id_class=msg_to_dlt_get_city_2.message_id)

                        bot.set_state(message.from_user.id, SearchStates.city, message.chat.id)

                    else:

                        create_eponymous_cities_keyboard(message.from_user.id, message.chat.id,
                                                         eponymous_cities)

            except (AttributeError, KeyError) as exc:

                logger.exception('user_id - {0}; тип ошибки - {1}'.format(message.from_user.id, exc))

                msg_to_dlt_mistake_1: Message = \
                    bot.send_message(message.chat.id,
                                     text='Ошибка связи с сайтом./nНажмите меню для выбора дальнейших действий.')

                crud.update_message_db(user_id_class=msg_to_dlt_mistake_1.from_user.id,
                                       chat_id_class=msg_to_dlt_mistake_1.chat.id,
                                       message_id_class=msg_to_dlt_mistake_1.message_id)

            except (ReadTimeout, TimeoutError) as exc:

                logger.exception('user_id - {0}; тип ошибки - {1}'.format(message.from_user.id, exc))

                msg_to_dlt_mistake_2: Message = \
                    bot.send_message(message.chat.id,
                                     text='Ошибка. Время ожидания истекло.'
                                          '\nНажмите меню для выбора дальнейших действий.')

                crud.update_message_db(user_id_class=msg_to_dlt_mistake_2.from_user.id,
                                       chat_id_class=msg_to_dlt_mistake_2.chat.id,
                                       message_id_class=msg_to_dlt_mistake_2.message_id)

            except ApiTelegramException as exc:

                logger.exception('user_id - {0}; тип ошибки - {1}'.format(message.from_user.id, exc))

                msg_to_dlt_mistake_3: Message = \
                    bot.send_message(message.chat.id,
                                     text='Ошибка связи с Телеграм.'
                                          '\nНажмите меню для выбора дальнейших действий.')

                crud.update_message_db(user_id_class=msg_to_dlt_mistake_3.from_user.id,
                                       chat_id_class=msg_to_dlt_mistake_3.chat.id,
                                       message_id_class=msg_to_dlt_mistake_3.message_id)

            except ConnectionError as exc:

                logger.exception('user_id - {0}; тип ошибки - {1}'.format(message.from_user.id, exc))

                msg_to_dlt_mistake_4: Message = \
                    bot.send_message(message.chat.id,
                                     text='Ошибка связи с сайтом.'
                                          '\nНажмите меню для выбора дальнейших действий.')

                crud.update_message_db(user_id_class=msg_to_dlt_mistake_4.from_user.id,
                                       chat_id_class=msg_to_dlt_mistake_4.chat.id,
                                       message_id_class=msg_to_dlt_mistake_4.message_id)

    except ApiTelegramException as exception:
        logger.exception(
            'user_id - {0}; тип ошибки - {1}'.format(message.from_user.id, exception))

        msg_to_dlt_mistake_5: Message = \
            bot.send_message(message.chat.id,
                             text='Ошибка связи с Телеграм.\nНажмите меню для выбора дальнейших действий.')

        crud.update_message_db(user_id_class=msg_to_dlt_mistake_5.from_user.id,
                               chat_id_class=msg_to_dlt_mistake_5.chat.id,
                               message_id_class=msg_to_dlt_mistake_5.message_id)

    except (ReadTimeout, TimeoutError) as exception:
        logger.exception(
            'user_id - {0}; тип ошибки - {1}'.format(message.from_user.id, exception))

        msg_to_dlt_mistake_6: Message = \
            bot.send_message(message.chat.id,
                             text='Ошибка. Время ожидания истекло.\nНажмите меню для выбора дальнейших действий.')

        crud.update_message_db(user_id_class=msg_to_dlt_mistake_6.from_user.id,
                               chat_id_class=msg_to_dlt_mistake_6.chat.id,
                               message_id_class=msg_to_dlt_mistake_6.message_id)

    except (OperationalError, ValueError, KeyError, NameError) as exception:
        logger.exception(
            'user_id - {0}; тип ошибки - {1}'.format(message.from_user.id, exception))

        msg_to_dlt_mistake_7: Message = \
            bot.send_message(message.chat.id,
                             text='Ошибка доступа к Вашей базе запросов.\nНажмите меню для выбора дальнейших действий.')

        crud.update_message_db(user_id_class=msg_to_dlt_mistake_7.from_user.id,
                               chat_id_class=msg_to_dlt_mistake_7.chat.id,
                               message_id_class=msg_to_dlt_mistake_7.message_id)


@bot.message_handler(commands=['search'])
def start_search(start_message: Message) -> None:
    """
    Функция обрабатывает команду /search, запрашивает у пользователя название города.

    :param start_message: Сообщение от пользователя
    :type start_message: Message
    """
    try:
        logger.info('id пользователя - {}; команда - /search'.format(start_message.from_user.id))

        logger.debug('id пользователя - {0}; вызов - функция start_search({1})'.
                     format(start_message.from_user.id, start_message))

        crud.update_message_db(user_id_class=start_message.from_user.id,
                               chat_id_class=start_message.chat.id,
                               message_id_class=start_message.message_id)

        crud.delete_message_db(user_id_class=start_message.from_user.id,
                               chat_id_class=start_message.chat.id)

        crud.update_user_db(user_id_class=start_message.from_user.id)

        bot.set_state(start_message.from_user.id, SearchStates.city, start_message.chat.id)

        msg_to_dlt_start_search_1: Message = bot.send_message(start_message.chat.id, text='Введите город:')

        crud.update_message_db(user_id_class=msg_to_dlt_start_search_1.from_user.id,
                               chat_id_class=msg_to_dlt_start_search_1.chat.id,
                               message_id_class=msg_to_dlt_start_search_1.message_id)

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
