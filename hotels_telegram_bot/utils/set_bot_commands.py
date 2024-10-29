"""В этом модуле описана функция set_default_commands(bot), которая устанавливает список команд бота."""
from telebot import TeleBot

import telebot.types

from config_data import config


def set_default_commands(bot: TeleBot) -> None:
    """Функция устанавливает список команд бота."""
    bot.set_my_commands([telebot.types.BotCommand(*command) for command in config.COMMANDS])
