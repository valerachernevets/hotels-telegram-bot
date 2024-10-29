"""В этом модуле описывается работа бота после команды /start."""
from peewee import OperationalError

from requests import ReadTimeout

from telebot.apihelper import ApiTelegramException

from telebot.types import Message

from loader import bot, crud

from utils.logger import logger


@bot.message_handler(commands=['start'])
def start_command(start_message: Message) -> None:
    """
    Функция принимает от пользователя команду /start, отправляет пользователю приветственное сообщение и
    записывает в базу данных id пользователя.

    :param start_message: Сообщение от пользователя
    :type start_message: Message
    """
    try:
        logger.info('user_id - {}; команда - /start'.format(start_message.from_user.id))

        logger.info('user_id - {}; вызов функции start_command(message: Message)'.format(start_message.from_user.id))

        crud.update_message_db(user_id_class=start_message.from_user.id,
                               chat_id_class=start_message.chat.id,
                               message_id_class=start_message.message_id)

        crud.delete_message_db(user_id_class=start_message.from_user.id,
                               chat_id_class=start_message.chat.id)

        crud.update_user_db(user_id_class=start_message.from_user.id)

        answer = 'Привет! {}.\nЯ - бот по подбору отелей по всему миру!' \
                 '\nВсе мои возможности Вы можете узнать с помощью команды /help.'.\
            format(start_message.from_user.first_name)

        logger.debug('user_id - {0}; вызов - метод crud.update_db_user([user_id: {1}])'.
                     format(start_message.from_user.id, start_message.from_user.id))

        msg_to_dlt_start_command: Message = bot.send_message(start_message.chat.id, text=answer)

        crud.update_message_db(user_id_class=msg_to_dlt_start_command.from_user.id,
                               chat_id_class=msg_to_dlt_start_command.chat.id,
                               message_id_class=msg_to_dlt_start_command.message_id)

    except ApiTelegramException as exception:
        logger.exception('user_id - {0}; тип ошибки - {1}'.format(start_message.from_user.id, exception))

        msg_to_dlt_mistake_1: Message = \
            bot.send_message(start_message.chat.id,
                             text='Ошибка связи с Телеграм.\nНажмите меню для выбора дальнейших действий.')

        crud.update_message_db(user_id_class=msg_to_dlt_mistake_1.from_user.id,
                               chat_id_class=msg_to_dlt_mistake_1.chat.id,
                               message_id_class=msg_to_dlt_mistake_1.message_id)

    except (ReadTimeout, TimeoutError) as exception:
        logger.exception('user_id - {0}; тип ошибки - {1}'.format(start_message.from_user.id, exception))

        msg_to_dlt_mistake_2: Message = \
            bot.send_message(start_message.chat.id,
                             text='Ошибка. Время ожидания истекло.\nНажмите меню для выбора дальнейших действий.')

        crud.update_message_db(user_id_class=msg_to_dlt_mistake_2.from_user.id,
                               chat_id_class=msg_to_dlt_mistake_2.chat.id,
                               message_id_class=msg_to_dlt_mistake_2.message_id)

    except (NameError, KeyError, ValueError, OperationalError) as exception:
        logger.exception('user_id - {0}; тип ошибки - {1}'.format(start_message.from_user.id, exception))

        msg_to_dlt_mistake_3: Message = \
            bot.send_message(start_message.chat.id,
                             text='Ошибка доступа к Вашей базе запросов.\nНажмите меню для выбора дальнейших действий.')

        crud.update_message_db(user_id_class=msg_to_dlt_mistake_3.from_user.id,
                               chat_id_class=msg_to_dlt_mistake_3.chat.id,
                               message_id_class=msg_to_dlt_mistake_3.message_id)
