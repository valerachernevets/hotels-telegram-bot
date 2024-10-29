"""
В модуле проверяется загружены ли переменные среды, объявляются классы
BotConfigs, SiteConfigs и описываются команды бота по умолчанию.
"""
import os

from dotenv import load_dotenv, find_dotenv

from pydantic_settings import BaseSettings

from pydantic import SecretStr, StrictStr

from utils.logger import logger


if not find_dotenv():
    logger.warning('вызов - функция exit(Переменные окружения не загружены, т.к. отсутствует файл .env)')

    exit('Переменные окружения не загружены, т.к. отсутствует файл .env')

else:
    load_dotenv()


class BotConfigs(BaseSettings):
    """
    Класс - BotConfigs. Родительский класс - BaseSettings.

    Читает и парсит переменные среды из файла .env, необходимые для запуска телеграм-бота.

    Attributes:
    BOT_TOKEN (SecretStr): значение ключа 'BOT_TOKEN' переменной среды
    """

    BOT_TOKEN: SecretStr = os.getenv('BOT_TOKEN', None)


class SiteConfigs(BaseSettings):
    """
    Класс - SiteConfigs. Родительский класс - BaseSettings.

    Читает и парсит переменные среды из файла .env, необходимые для правильного подключения
    к сайту rapidapi.com.

    Attributes:
    CONTENT_TYPE_API (StrictStr): значение ключа 'CONTENT_TYPE_API' переменной среды
    HOST_API (StrictStr): значение ключа 'HOST_API' переменной среды
    EPONYMOUS_CITIES_API_KEY (SecretStr): значение ключа 'EPONYMOUS_CITIES_API_KEY' переменной среды
    HOTEL_API_KEY (SecretStr): значение ключа 'HOTEL_API_KEY' переменной среды
    HOTEL_DETAIL_API_KEY (SecretStr): значение ключа 'HOTEL_DETAIL_API_KEY' переменной среды
    """

    CONTENT_TYPE_API: StrictStr = os.getenv('CONTENT_TYPE_API', None)
    HOST_API: StrictStr = os.getenv('HOST_API', None)
    EPONYMOUS_CITIES_API_KEY: SecretStr = os.getenv('EPONYMOUS_CITIES_API_KEY', None)
    HOTEL_API_KEY: SecretStr = os.getenv('HOTEL_API_KEY', None)
    HOTEL_DETAIL_API_KEY: SecretStr = os.getenv('HOTEL_DETAIL_API_KEY', None)


COMMANDS: tuple = (
    ('start', 'Запустить бота'),
    ('help', 'Вывести справочную информацию'),
    ('search', 'Начать поиск отелей'),
    ('history', 'История поиска'),
    ('cancel', 'Отмена поиска'))
