"""В этом модуле создаем экземпляры классов StateMemoryStorage, BotConfigs, TeleBot."""
from telebot import TeleBot

from telebot.storage import StateMemoryStorage

from config_data.config import BotConfigs

from database.utils.CRUD import CrudInterface

from database.utils.chat_cleaner import clean_chat

crud = CrudInterface()

state_storage: StateMemoryStorage = StateMemoryStorage()

bot_config: BotConfigs = BotConfigs()

bot: TeleBot = TeleBot(token=bot_config.BOT_TOKEN.get_secret_value(), state_storage=state_storage)

clean_chat()




