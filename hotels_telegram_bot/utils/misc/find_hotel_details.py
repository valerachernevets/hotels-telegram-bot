"""
В этом модуле описана работа find_hotel_details(method_endswith, method_type, hotel_id), это функция,
которая получает c сайта rapidapi.com подробные сведения про отель по его id.
"""
import json

from typing import List, Any

from requests import Response

from config_data.config import SiteConfigs

from utils.logger import logger

from utils.site_api.site_api_handler import get_api_request

site_config: SiteConfigs = SiteConfigs()


def find_hotel_details(user_id: int, method_endswith: str, method_type: str, hotel_id: int) -> List | int:
    """
    Функция, которая получает c сайта rapidapi.com подробные сведения про отель по его id.

    :param user_id: Id пользователя
    :param method_endswith: окончание url необходимого для правильного запроса
    :param method_type: тип метода
    :param hotel_id: id отеля
    :type user_id: int
    :type method_endswith: str
    :type method_type: str
    :type hotel_id: int
    :return hotel_details: список с подробной информацией про отель
    :rtype hotel_details: List
    """
    logger.debug('user_id - {0}; вызов - функция find_hotel_details(user_id={1},'
                 ' method_endswith={2}, method_type={3}, hotel_id={4})'.
                 format(user_id, user_id, method_endswith,
                        method_type, hotel_id))

    response: Response | int = get_api_request(user_id=user_id, method_endswith=method_endswith,
                                               method_type=method_type, city=None,
                                               refine_city_id=None, arrival_date=None, date_of_departure=None,
                                               min_price=None, max_price=None, adults_quantity=None,
                                               children_ages=None, hotel_id=hotel_id)

    if type(response) == int:
        logger.debug('user_id - {0}; результат работы функции find_hotel_details(user_id={1},'
                     ' method_endswith={2}, method_type={3}, hotel_id={4}) = {5}'.
                     format(user_id, user_id, method_endswith,
                            method_type, hotel_id, response))

        return response

    else:
        data: Any = json.loads(response.text)

        with open('hotels_detail.json', 'w') as file:
            json.dump(data, file, indent=4)

        logger.debug('user_id - {}; запись в файл hotels_detail.json'.format(user_id))

        hotel_details: List = [data['data']['propertyInfo']['summary']['location']['address']['addressLine'],
                               data['data']['propertyInfo']['propertyGallery']['images'][0]['image']['url']]

        logger.debug('user_id - {0}; результат работы функции find_hotel_details(user_id={1},'
                     ' method_endswith={2}, method_type={3}, hotel_id={4}) = {5}'.
                     format(user_id, user_id, method_endswith,
                            method_type, hotel_id, hotel_details))

        return hotel_details
