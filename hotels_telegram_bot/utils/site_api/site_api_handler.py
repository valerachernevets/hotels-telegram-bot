"""
В этом модуле описываются функции:

get_required_params(method_endswith: str, city: str | None, refine_city_id: str | None,
                    arrival_date: datetime | None, date_of_departure: datetime | None, min_price: str | None,
                    max_price: str | None, hotel_id: int | None),
функция возвращает нужные параметры для подключения к сайту rapidapi.com;

get_response(method_type: str, url: str, headers: Dict, timeout: int,
             params: Dict | None, json: Dict | None, success=200),
функция возвращает ответ от сайта rapidapi.com;

get_api_request(method_endswith: str, method_type: str, headers: Dict, params: Dict),
функция возвращает ответ от сайта rapidapi.com в зависимости от переданных параметров.
"""
from datetime import datetime

from typing import Dict, List

import requests

from requests import Response

from config_data.config import SiteConfigs

from utils.logger import logger

site_config: SiteConfigs = SiteConfigs()


def get_required_params(user_id: int, method_endswith: str, city: str | None, refine_city_id: str | None,
                        arrival_date: datetime | None, date_of_departure: datetime | None, min_price: str | None,
                        max_price: str | None, adults_quantity: str | None, children_ages: List | None,
                        hotel_id: int | None) -> List:
    """
    Функция возвращает нужные параметры для подключения к сайту rapidapi.com.

    :param user_id: Id пользователя
    :param method_endswith: окончание url необходимого для правильного запроса
    :param city: название города, введенное пользователем
    :param refine_city_id: название уточненного города
    :param arrival_date: дата приезда
    :param date_of_departure: дата отъезда
    :param min_price: минимальная цена проживания за сутки
    :param max_price: максимальная цена проживания за сутки
    :param adults_quantity: количество взрослых
    :param children_ages: список возрастов детей
    :param hotel_id: id отеля
    :type user_id: int
    :type method_endswith: str
    :type city: str | None
    :type refine_city_id: str | None
    :type arrival_date: datetime | None
    :type date_of_departure: datetime | None
    :type min_price: str | None
    :type max_price: str | None
    :type adults_quantity: int | None
    :type children_ages: List | None
    :type hotel_id: int | None
    :return result_params: список параметров для подключения к сайту rapidapi.com
    :rtype result_params: List
    """
    logger.debug('user_id - {0}; вызов - функция get_required_params(user_id={1}, method_endswith={2}, city={3},'
                 ' refine_city_id={4}, arrival_date={5}, date_of_departure={6}, min_price={7},'
                 ' max_price={8}, hotel_id={9})'.
                 format(user_id, user_id, method_endswith, city, refine_city_id, arrival_date,
                        date_of_departure, min_price, max_price, hotel_id))
    result_params: List = []

    if method_endswith == 'locations/v3/search':
        querystring: Dict = {"q": city, "locale": "en_US", "langid": "1033", "siteid": "300000001"}

        headers: Dict = {
            "X-RapidAPI-Key": site_config.EPONYMOUS_CITIES_API_KEY.get_secret_value(),
            "X-RapidAPI-Host": site_config.HOST_API
        }

        result_params = [querystring, headers]

    elif method_endswith == 'properties/v2/list':
        payload: Dict = {
            "currency": "USD",
            "eapid": 1,
            "locale": "en_US",
            "siteId": 300000001,
            "destination": {"regionId": refine_city_id},
            "checkInDate": {
                "day": arrival_date.day,
                "month": arrival_date.month,
                "year": arrival_date.year
            },
            "checkOutDate": {
                "day": date_of_departure.day,
                "month": date_of_departure.month,
                "year": date_of_departure.year
            },
            "rooms": [
                {
                    # "adults": 1,
                    # "children": [{"age": 5}, {"age": 7}]
                    "adults": int(adults_quantity),
                    "children": children_ages
                }
            ],
            "resultsStartingIndex": 0,
            "resultsSize": 200,
            "sort": "PRICE_LOW_TO_HIGH",
            "filters": {"price": {
                "max": int(max_price),
                "min": int(min_price)
            }}
        }

        headers = {
            "content-type": site_config.CONTENT_TYPE_API,
            "X-RapidAPI-Key": site_config.HOTEL_API_KEY.get_secret_value(),
            "X-RapidAPI-Host": site_config.HOST_API
        }

        result_params = [payload, headers]

    elif method_endswith == 'properties/v2/detail':
        payload = {
            "currency": "USD",
            "eapid": 1,
            "locale": "en_US",
            "siteId": 300000001,
            "propertyId": hotel_id
        }

        headers = {
            "content-type": site_config.CONTENT_TYPE_API,
            "X-RapidAPI-Key": site_config.HOTEL_DETAIL_API_KEY.get_secret_value(),
            "X-RapidAPI-Host": site_config.HOST_API
        }

        result_params = [payload, headers]

    logger.info('user_id - {0}; результат работы функции get_required_params(user_id={1}, method_endswith={2},'
                ' city={3}, refine_city_id={4}, arrival_date={5}, date_of_departure={6}, min_price={7},'
                ' max_price={8}, hotel_id={9} = {10})'.
                format(user_id, user_id, method_endswith, city, refine_city_id, arrival_date,
                       date_of_departure, min_price, max_price, hotel_id, result_params))

    return result_params


def get_response(user_id: int, method_type: str, url: str, headers: Dict, params: Dict | None, json: Dict | None,
                 timeout: int, success=200) -> Response | int:
    """
    Функция возвращает ответ от сайта rapidapi.com.

    :param user_id: id пользователя
    :param method_type: тип метода
    :param url: url для подключения
    :param headers: headers
    :param timeout: время ожидания ответа
    :param params: параметры запроса
    :param json: json
    :param success: код ответа от сайта
    :type user_id: int
    :type method_type: str
    :type url: str
    :type headers: Dict
    :type timeout: int
    :type params: Dict
    :type json: Dict
    :type success: int
    :return response: ответ от сайта
    :return status_code: код ответа от сайта
    :rtype response: Response
    :rtype status_code: int
    """
    logger.debug('user_id - {0}; вызов - функция get_response(method_type={1}, url={2}, headers={3}, params={4},'
                 ' json={5}, timeout={6})'.
                 format(user_id, method_type, url, headers, params, json, timeout))

    response: Response = requests.request(method=method_type, url=url, headers=headers, params=params, json=json,
                                          timeout=timeout)

    status_code: int = response.status_code

    if status_code == success:

        logger.info('user_id - {0}; результат работы функции get_response(method_type={1}, url={2}, params={3},'
                    ' json={4}, headers={5}, timeout={6}) = {7}'.
                    format(user_id, method_type, url, headers, params, json, timeout, response))

        return response

    else:

        logger.info('user_id - {0}; результат работы функции get_response(method_type={1}, url={2}, params={3},'
                    ' json={4}, headers={5}, timeout={6}) = {7}'.
                    format(user_id, method_type, url, headers, params, json, timeout, status_code))

        return status_code


def get_api_request(user_id: int, method_endswith: str, method_type: str, city: str | None, refine_city_id: str | None,
                    arrival_date: datetime | None, date_of_departure: datetime | None, min_price: str | None,
                    max_price: str | None, adults_quantity: str | None, children_ages: List | None,
                    hotel_id: int | None) -> Response | int:
    """
    Функция возвращает ответ от сайта rapidapi.com в зависимости от переданных параметров.

    :param user_id: id пользователя
    :param method_endswith: окончание url необходимого для правильного запроса
    :param method_type: тип метода
    :param city: название города
    :param refine_city_id: название уточненного города
    :param arrival_date: дата приезда
    :param date_of_departure: дата отъезда
    :param min_price: минимальная цена за сутки
    :param max_price: максимальная цена за сутки
    :param adults_quantity: количество взрослых
    :param children_ages: список возрастов детей
    :param hotel_id: id отеля
    :type user_id: int
    :type method_endswith: str
    :type method_type: str
    :type city: str | None
    :type refine_city_id: str | None
    :type arrival_date: datetime | None
    :type date_of_departure: datetime | None
    :type min_price: str | None
    :type max_price: str | None
    :type adults_quantity: int | None
    :type children_ages: List | None
    :type hotel_id: int | None
    :return response: ответ от сайта или код соединения с сайтом
    :rtype response: Response | int
    """
    logger.debug('user_id - {0}; вызов - функция get_api_request(user_id={1}; method_endswith={2},'
                 ' method_type={3}, city={4},'
                 ' refine_city_id={5}, arrival_date={6}, date_of_departure={7},'
                 ' min_price={8}, max_price={9}, hotel_id={10})'.
                 format(user_id, user_id, method_endswith, method_type, city, None, None, None, None, None, None))

    required_params: List = get_required_params(user_id=user_id, method_endswith=method_endswith, city=city,
                                                refine_city_id=refine_city_id, arrival_date=arrival_date,
                                                date_of_departure=date_of_departure, min_price=min_price,
                                                max_price=max_price, adults_quantity=adults_quantity,
                                                children_ages=children_ages, hotel_id=hotel_id)

    url: str = 'https://hotels4.p.rapidapi.com/{}'.format(method_endswith)

    if method_type == 'GET':

        response: Response | int = get_response(user_id=user_id, method_type=method_type, url=url,
                                                params=required_params[0], json=None, headers=required_params[1],
                                                timeout=15)

        logger.info('user_id - {0}; результат работы функции get_api_request(user_id={1}; method_endswith={2},'
                    ' method_type={3}, city={4}, refine_city_id={5}, arrival_date={6}, date_of_departure={7},'
                    ' min_price={8}, max_price={9}, hotel_id={10}) = {11}'.
                    format(user_id, user_id, method_endswith, method_type, city,
                           None, None, None, None, None, None, response))

        return response

    elif method_type == 'POST':

        response = get_response(user_id=user_id, method_type=method_type, url=url, params=None,
                                json=required_params[0], headers=required_params[1], timeout=15)

        logger.info('user_id - {0}; результат работы функции get_api_request(user_id={1}; method_endswith={2},'
                    ' method_type={3}, city={4}, refine_city_id={5}, arrival_date={6}, date_of_departure={7},'
                    ' min_price={8}, max_price={9}, hotel_id={10}) = {11}'.
                    format(user_id, user_id, method_endswith, method_type, city,
                           None, None, None, None, None, None, response))

        return response
