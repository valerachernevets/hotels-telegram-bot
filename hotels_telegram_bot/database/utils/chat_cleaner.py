"""В этом модуле описана функция clean_chat(), которая удаляет все сообщения из чата,
если пользователь неактивен в течение одного часа и в чате остались неудаленные сообщения.
"""
import threading

from datetime import datetime, timedelta

import loader

from database.common.models import Message

from utils.logger import logger


def clean_chat():
    logger.debug('вызов - функция clean_chat()')

    threading.Timer(43200.0, clean_chat).start()

    delta = timedelta(hours=6)

    for i_message in Message.select():

        if i_message.created_at < datetime.now() - delta:

            loader.bot.delete_message(i_message.chat_id, i_message.message_id)

            i_message.delete_instance()

            logger.info('удаление сообщения {0} из чата {1}'.format(i_message.message_id, i_message.chat_id))
