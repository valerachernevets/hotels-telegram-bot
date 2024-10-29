"""В этом модуле описывается работа функции echo_command."""
from requests import ReadTimeout

from telebot.apihelper import ApiTelegramException

from telebot.types import Message

from config_data.config import COMMANDS

from loader import bot, crud

from utils.logger import logger


@bot.message_handler(content_types=["text"])
def echo_command(message: Message) -> None:
    """
    Функция принимает команду от пользователя, сравнивает ее с доступными для бота командами, если не находит
    такой команды, то оправляет пользователю эхо-сообщение.

    :param message: Сообщение от пользователя
    :type message: Message
    """
    try:
        logger.warning('user_id - {0}; {1} - неизвестная команда'.format(message.from_user.id, message))

        crud.update_message_db(user_id_class=message.from_user.id,
                               chat_id_class=message.chat.id,
                               message_id_class=message.message_id)

        answer = ['/{} - {}'.format(command, description) for command, description in COMMANDS]

        msg_to_dlt_echo: Message =\
            bot.reply_to(message,
                         'Команды \'{user_message}\' нет в моем списке команд.'
                         '\nНажмите кнопку клавиатуры или выберите доступные команды:\n{answer_to_user}'.
                         format(user_message=message.text, answer_to_user='\n'.join(answer)))

        crud.update_message_db(user_id_class=msg_to_dlt_echo.from_user.id,
                               chat_id_class=msg_to_dlt_echo.chat.id,
                               message_id_class=msg_to_dlt_echo.message_id)

    except ApiTelegramException as exception:
        logger.exception('user_id - {0}; тип ошибки - {1}'.format(message.from_user.id, exception))

        msg_to_dlt_mistake_1: Message = \
            bot.send_message(message.chat.id,
                             text='Ошибка связи с Телеграм.\nНажмите меню для выбора дальнейших действий.')

        crud.update_message_db(user_id_class=msg_to_dlt_mistake_1.from_user.id,
                               chat_id_class=msg_to_dlt_mistake_1.chat.id,
                               message_id_class=msg_to_dlt_mistake_1.message_id)

    except (ReadTimeout, TimeoutError) as exception:
        logger.exception('user_id - {0}; тип ошибки - {1}'.format(message.from_user.id, exception))

        msg_to_dlt_mistake_2: Message = \
            bot.send_message(message.chat.id,
                             text='Ошибка. Время ожидания истекло.\nНажмите меню для выбора дальнейших действий.')

        crud.update_message_db(user_id_class=msg_to_dlt_mistake_2.from_user.id,
                               chat_id_class=msg_to_dlt_mistake_2.chat.id,
                               message_id_class=msg_to_dlt_mistake_2.message_id)
