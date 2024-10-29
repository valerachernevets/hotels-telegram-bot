"""
В этом модуле описана find_eponymous_cities(method_endswith: str, method_type: str, city: str),
это функция поиска одноименных городов или городов с похожим названием на название,
введенное пользователем.
"""
import json

from typing import Dict, Any

from requests import Response

from config_data.config import SiteConfigs

from utils.logger import logger

from utils.site_api.site_api_handler import get_api_request

site_config: SiteConfigs = SiteConfigs()


def find_eponymous_cities(user_id: int, method_endswith: str, method_type: str, city: str) -> Dict | int:
    """
    Функция поиска одноименных городов или городов с похожим названием на название,
    введенное пользователем.

    :param user_id: Id пользователя
    :param method_endswith: окончание url необходимого для правильного запроса
    :param method_type: тип метода
    :param city: название города, введенное пользователем
    :type user_id: int
    :type method_endswith: str
    :type method_type: str
    :type city: str
    :return eponymous_cities: список одноименных или похожих по названию городов
    :return response: код ответа от сайта rapidapi.com
    :rtype eponymous_cities: Dict
    :rtype response: int
    """
    logger.debug('user_id - {0}; вызов - функция find_eponymous_cities('
                 ' user_id={1}, method_endswith={2},'
                 ' method_type={3}, city={4}) '.
                 format(user_id, user_id,
                        method_endswith, method_type, city))

    response: Response | int = get_api_request(user_id=user_id, method_endswith=method_endswith,
                                               method_type=method_type, city=city,
                                               refine_city_id=None, arrival_date=None, date_of_departure=None,
                                               min_price=None, max_price=None, adults_quantity=None,
                                               children_ages=None, hotel_id=None)

    if type(response) == int:

        logger.info('user_id - {0}; результат работы функции find_eponymous_cities('
                    ' user_id={1}, method_endswith={2}, method_type={3}, city={4}) = {5}'.
                    format(user_id, user_id,
                           method_endswith, method_type, city, response))
        return response

    else:
        data: Any = json.loads(response.text)

        with open('eponymous_cities.json', 'w') as file:
            json.dump(data, file, indent=4)

            logger.debug('user_id - {}; запись в файл eponymous_cities.json'.format(user_id))

        eponymous_cities: Dict = {}

        for i_data in data['sr']:
            if i_data['type'] == 'CITY':
                eponymous_cities[i_data['gaiaId']] = i_data['regionNames']['fullName']

        logger.info('user_id - {0}; результат работы функции find_eponymous_cities('
                    ' user_id={1}, method_endswith={2}, method_type={3}, city={4}) = {5}'.
                    format(user_id, user_id,
                           method_endswith, method_type, city, eponymous_cities))

        return eponymous_cities
