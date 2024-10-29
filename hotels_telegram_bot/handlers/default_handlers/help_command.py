"""В этом модуле описывается работа бота после введения команды /help."""
from requests import ReadTimeout

from telebot.apihelper import ApiTelegramException

from telebot.types import Message

from config_data.config import COMMANDS

from loader import bot, crud

from utils.logger import logger


@bot.message_handler(commands=['help'])
def help_command(start_message: Message) -> None:
    """
    Функция принимает от пользователя команду /help или результат работы клавиатуры
    и выводит список команд по умолчанию.

    :param start_message: Сообщение от пользователя
    :type start_message: Message
    """
    try:
        logger.info('user_id - {}; команда - /help'.format(start_message.from_user.id))

        logger.debug('user_id - {0}; вызов - функция help_command({1})'.
                     format(start_message.from_user.id, start_message))

        crud.update_message_db(user_id_class=start_message.from_user.id,
                               chat_id_class=start_message.chat.id,
                               message_id_class=start_message.message_id)

        crud.delete_message_db(user_id_class=start_message.from_user.id,
                               chat_id_class=start_message.chat.id)

        crud.update_user_db(user_id_class=start_message.from_user.id)

        answer = [f'/{command} - {description}' for command, description in COMMANDS]

        msg_to_dlt_help_command: Message = \
            bot.send_message(start_message.chat.id,
                             text='Доступные команды:\n{answer_to_user}'.format(answer_to_user='\n'.join(answer)))

        crud.update_message_db(user_id_class=msg_to_dlt_help_command.from_user.id,
                               chat_id_class=msg_to_dlt_help_command.chat.id,
                               message_id_class=msg_to_dlt_help_command.message_id)

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
