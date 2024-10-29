from requests import ReadTimeout

from telebot.apihelper import ApiTelegramException

from database.common.base import db_history, db_message

from database.common.models import User, Request, Message

from loader import bot

from utils.logger import logger

from utils.set_bot_commands import set_default_commands

import telebot.custom_filters

import handlers


if __name__ == '__main__':
    try:
        bot.add_custom_filter(telebot.custom_filters.StateFilter(bot))

        set_default_commands(bot)

        # db.create_tables([User, Request, Message])

        db_history.create_tables([User, Request])

        db_message.create_tables([Message])

        bot.polling(non_stop=True)

    except (ReadTimeout, TimeoutError) as exception:
        logger.exception('тип ошибки - {}'.format(exception))

    except ApiTelegramException as exception:
        logger.exception('тип ошибки - {}'.format(exception))

    except NameError as exception:
        logger.exception('тип ошибки - {}'.format(exception))

    except ValueError as exception:
        logger.exception('тип ошибки - {}'.format(exception))

    except KeyError as exception:
        logger.exception('тип ошибки - {}'.format(exception))

    except ImportError as exception:
        logger.exception('тип ошибки - {}'.format(exception))
