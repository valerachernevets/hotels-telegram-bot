"""
В этом модуле описываются функции для работы с базой данных и объявляется класс CrudInterface c методами
для взаимодействия пользователя с его базой запросов.
"""
from typing import List, Dict

from database.common.base import db_history, db_message

from database.common.models import User, Request, Message

import loader

from utils.logger import logger


def _func_update_user_db(user_id_func: int) -> None:
    """
    Записывает id пользователя в таблицу User, если его там нет.

    :param user_id_func: Id пользователя
    :type user_id_func: int
    """
    logger.debug('user_id - {0}; вызов - функция '
                 '_func_update_user_db(user_id_func={1})'.
                 format(user_id_func, user_id_func))

    data: List = [{'user_id': user_id_func}]
    with db_history.atomic():
        if data[0]['user_id'] not in [i_user.user_id for i_user in User.select()]:
            User.insert_many(data).execute()

    logger.info('user_id - {0}, запись id пользователя - {1} в таблицу User'.
                format(user_id_func, user_id_func))


def _func_update_request_db(user_id_func: int, data_func: List[Dict]) -> None:
    """
    Записывает запрос пользователя в таблицу Request.

    :param user_id_func: Id пользователя
    :param data_func: данные для записи в таблицу
    :type user_id_func: int
    :type data_func: List[Dict]
    """
    logger.debug('user_id - {0}; вызов - функция '
                 '_func_update_request_db(user_id_func={1}, data_func={2})'.
                 format(user_id_func, user_id_func, data_func))

    with db_history.atomic():
        Request.insert_many(data_func).execute()

    logger.info('user_id- {0}; записывает запрос пользователя {1}'.
                format(user_id_func, data_func))


def _func_update_message_db(user_id_func: int, chat_id_func: int, message_id_func: int) -> None:
    """
    Записывает пару 'id чата - id сообщения' полученную от пользователя в таблицу Message.

    :param user_id_func: Id пользователя
    :param chat_id_func: id чата
    :param message_id_func: id сообщения
    :type user_id_func: int
    :type chat_id_func: int
    :type message_id_func: int
    """
    logger.debug('user_id - {0},'
                 ' вызов - функция _func_update_message_db(user_id_func={1}, chat_id_func={2},'
                 ' message_id_func={3})'.format(user_id_func, user_id_func, chat_id_func, message_id_func))

    data: List = [{'chat_id': chat_id_func, 'message_id': message_id_func}]

    with db_message.atomic():
        Message.insert_many(data).execute()

    logger.info('user_id - {0}; запись пары \'chat_id = {1} - message_id = {2}\' в таблицу Message'.
                format(user_id_func, chat_id_func, message_id_func))


def _func_retrieve_db(user_id_func: int) -> List[List]:
    """
    Формирует список по каждому отелю который просматривал пользователь.

    Список содержит город в котором расположен отель, название отеля, адрес отеля, ссылка на фото отеля.

    :param user_id_func: Id пользователя
    :type user_id_func: int
    :return user_history: список с информацией по каждому отелю
    :rtype user_history: List[List]
    """
    logger.debug('user_id - {0}; вызов - функция '
                 '_func_retrieve_db(user_id_func={1})'.
                 format(user_id_func, user_id_func))

    user_history: List = []

    full_user_history = User.get(User.user_id == str(user_id_func))

    for i_history in full_user_history.request:
        user_history.append([i_history.hotel_id, i_history.refined_city,
                             i_history.hotel_name, i_history.hotel_address, i_history.hotel_photo_url])

    user_history.reverse()

    logger.info('user_id - {0}; результат работы функции '
                '_func_update_message_db('
                'user_id_func={1}) = {2}'.
                format(user_id_func, user_id_func, user_history))

    return user_history


def _func_delete_message_db(user_id_func: int, chat_id_func: int) -> None:
    """
    Функция удаляет сообщения из чата, а потом удаляет пары 'id чата - id сообщения' из таблицы Message.

    :param user_id_func: Id пользователя
    :param chat_id_func: id чата
    :type user_id_func: int
    :type chat_id_func: int
    """
    logger.debug('user_id - {0};'
                 ' вызов - функция _func_delete_message_db(user_id_func={1}, chat_id_func={2}'.
                 format(user_id_func, user_id_func, chat_id_func))

    message_db = Message.select()

    for i_message in message_db:
        if i_message.chat_id == chat_id_func:
            loader.bot.delete_message(i_message.chat_id, i_message.message_id)

    for i_message in message_db:
        if i_message.chat_id == chat_id_func:
            i_message.delete_instance()

    logger.info('user_id - {0}, удаление всех пар \'id чата - id сообщения\''
                ' при значении id чата равному {1}'.format(user_id_func, chat_id_func))


def _func_delete_db(user_id_func: int) -> None:
    """
    Удаляет все записи из базы данных.

    :param user_id_func: Id пользователя
    :type user_id_func: int
    """
    logger.debug('user_id - {0};'
                 ' вызов - функция _func_delete_db(user_id_func={1}'.
                 format(user_id_func, user_id_func))

    full_user_history = User.get(User.user_id == str(user_id_func))

    for i_history in full_user_history.request:
        i_history.delete_instance()

    logger.info('user_id - {0}, удаление всех запросов пользователя с id равным {1}'
                .format(user_id_func, user_id_func))


def _func_delete_file_db(user_id_func: int, hotel_id_func: str) -> None:
    """
    Удаляет информацию о выбранном отеле.

    :param user_id_func: Id пользователя
    :type hotel_id_func: int
    :param user_id_func: id отеля
    :type hotel_id_func: str
    """
    logger.debug('user_id - {0}; вызов - функция _func_delete_file_db({1}, {2})'.
                 format(user_id_func,
                        user_id_func,
                        hotel_id_func))

    full_user_history = User.get(User.user_id == str(user_id_func))

    for i_history in full_user_history.request:
        if i_history.hotel_id == int(hotel_id_func):
            i_history.delete_instance()

    logger.info('user_id - {0}; результат работы функции _func_delete_file_db({1}, {2})'
                ' удаление информации про отель'.
                format(user_id_func, user_id_func, hotel_id_func))


class CrudInterface:
    """
    Базовый класс - CrudInterface.

    Описает взаимодействие пользователя с его базой запросов.

    """
    logger.debug('создание объекта класса CrudInterface()')

    @staticmethod
    def update_user_db(user_id_class: int):
        """
        Возвращает результат работы функции _func_update_user_db(user_id_func).

        :param user_id_class: Id пользователя
        :type user_id_class: int
        """
        logger.debug('user_id - {0}; вызов - метод update_user_db(user_id_class={1})'
                     ' класс CrudInterface'.format(user_id_class, user_id_class))

        logger.info('user_id - {0}; возвращает результат работы функции '
                    '_func_update_user_db('
                    'user_id_func={1})'.
                    format(user_id_class, user_id_class))

        return _func_update_user_db(user_id_func=user_id_class)

    @staticmethod
    def update_request_db(user_id_class: int, data_class: List[Dict]):
        """
        Возвращает результат работы функции _func_update_request_db(data_func).

        :param user_id_class: Id пользователя
        :param data_class: данные для записи в таблицу
        :type user_id_class: int
        :type data_class: List[Dict]
        """
        logger.debug('user_id - {0}; вызов - метод update_request_db(user_id_func={1}, data_class={2})'
                     ' класс CrudInterface'.format(user_id_class, user_id_class, data_class))

        logger.info('user_id - {0}; возвращает результат работы функции '
                    '_func_update_request_db(user_id_func={1}, data_func={2})'.
                    format(user_id_class, user_id_class, data_class))

        return _func_update_request_db(user_id_func=user_id_class, data_func=data_class)

    @staticmethod
    def update_message_db(user_id_class: int, chat_id_class: int, message_id_class: int):
        """
        Возвращает результат работы функции _func_update_message_db(user_id_func, chat_id_func, message_id_func).

        :param user_id_class: Id пользователя
        :param chat_id_class: id чата
        :param message_id_class: id сообщения
        :type user_id_class: int
        :type chat_id_class: int
        :type message_id_class: int
        """
        logger.debug('user_id - {0}; вызов - метод update_message_db(user_id_class={1},'
                     ' chat_id_class={2}, message_id_class={3})'
                     ' класс CrudInterface'.format(user_id_class, user_id_class, chat_id_class, message_id_class))

        logger.info('user_id - {0}; возвращает результат работы функции '
                    '_func_update_message_db('
                    'user_id_func={1}, chat_id_func={2}, message_id_func={3})'.
                    format(user_id_class, user_id_class, chat_id_class, message_id_class))

        return _func_update_message_db(user_id_func=user_id_class, chat_id_func=chat_id_class,
                                       message_id_func=message_id_class)

    @staticmethod
    def retrieve_db(user_id_class: int) -> List[List]:
        """
        Возвращает результат работы функции _func_retrieve_db(user_id_func).

        Список содержит город в котором расположен отель, название отеля, адрес отеля, ссылка на фото отеля.

        :param user_id_class: Id пользователя
        :type user_id_class: int
        :return : Список с информацией по каждому отелю
        :rtype : List[List]
        """
        logger.debug('user_id - {0}; вызов - метод retrieve_db(user_id_class={1})'
                     ' класс CrudInterface'.format(user_id_class, user_id_class))

        logger.info('user_id - {0}; возвращает результат работы функции '
                    '_func_retrieve_db(user_id_func={1})'.
                    format(user_id_class, user_id_class))

        return _func_retrieve_db(user_id_func=user_id_class)

    @staticmethod
    def delete_message_db(user_id_class: int, chat_id_class: int):
        """
        Возвращает результат работы функции _func_delete_message_db(user_id_func, chat_id_func)

        :param user_id_class: Id пользователя
        :param chat_id_class: id чата
        :type user_id_class: int
        :type chat_id_class: int
        """
        logger.debug('user_id- {0}; вызов - метод delete_message_db(chat_id_class={1})'
                     ' класс CrudInterface'.format(user_id_class, chat_id_class))

        logger.info('user_id - {0}; возвращает результат работы _func_delete_message_db('
                    'user_id_func={1}, chat_id_func={2})'.format(user_id_class, user_id_class, chat_id_class))

        return _func_delete_message_db(user_id_func=user_id_class, chat_id_func=chat_id_class)

    @staticmethod
    def delete_db(user_id_class: int):
        """
        Возвращает результат работы функции _func_delete_db(user_id)

        :param user_id_class: Id пользователя
        :type user_id_class: int
        """
        logger.debug('user_id - {0}; вызов - метод delete_db(user_id_class={1})'
                     ' класс CrudInterface'.format(user_id_class, user_id_class))

        logger.info('user_id - {0}; возвращает результат работы _func_delete_db('
                    'user_id_func={1})'.format(user_id_class, user_id_class))

        return _func_delete_db(user_id_func=user_id_class)

    @staticmethod
    def delete_file_db(user_id_class: int, hotel_id_class: str):
        """
        Возвращает результат работы функции _func_delete_db(user_id)

        :param user_id_class: Id пользователя
        :param hotel_id_class: id отеля
        :type user_id_class: int
        :type hotel_id_class: str
        """
        logger.debug('user_id - {0}; вызов - метод delete_file_db(user_id_class={1},'
                     'hotel_id_class={2})'
                     ' класс CrudInterface'.format(user_id_class, user_id_class, hotel_id_class))

        logger.info('user_id - {0}; возвращает результат работы _func_delete_file_db('
                    'user_id_func={1}, hotel_id_func={2})'.format(user_id_class, user_id_class, hotel_id_class))

        return _func_delete_file_db(user_id_func=user_id_class, hotel_id_func=hotel_id_class)


if __name__ == '__main__':
    _func_update_user_db()
    _func_update_request_db()
    _func_update_message_db()
    _func_retrieve_db()
    _func_delete_message_db()
    _func_delete_db()
    _func_delete_file_db()
    CrudInterface()
