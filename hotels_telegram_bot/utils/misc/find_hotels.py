"""
В этом модуле описана работа
find_hotels(method_endswith, method_type, refine_city_id, arrival_date, date_of_departure,
min_price, max_price, max_distance_from_center) это функция поиска отелей, соответствующих критериям пользователя.
"""
import json

from datetime import datetime

from typing import List, Any, Dict

from requests import Response

from config_data.config import SiteConfigs

from utils.logger import logger

from utils.site_api.site_api_handler import get_api_request

site_config: SiteConfigs = SiteConfigs()


def find_hotels(user_id: int, method_endswith: str, method_type: str, refine_city_id: str, arrival_date: datetime,
                date_of_departure: datetime, min_price: str, max_price: str, adults_quantity: str,
                children_ages: List,
                max_distance_from_center: str) -> int | str | List:
    """
    Функция поиска отелей, соответствующих критериям пользователя.

    :param user_id: Id пользователя
    :param method_endswith: окончание url необходимого для правильного запроса
    :param method_type: тип метода
    :param refine_city_id: название уточненного города
    :param arrival_date: дата приезда
    :param date_of_departure: дата отъезда
    :param min_price: минимальная цена проживания за сутки
    :param max_price: максимальная цена проживания за сутки
    :param adults_quantity: количество взрослых
    :param children_ages: список возрастов детей
    :param max_distance_from_center: максимальное расстояние отеля от центра города
    :type user_id: int
    :type method_endswith: str
    :type method_type: str
    :type refine_city_id: str
    :type arrival_date: str
    :type date_of_departure: str
    :type min_price: str
    :type max_price: str
    :type adults_quantity: int | None
    :type children_ages: List | None
    :type max_distance_from_center: str
    :return: hotels_sorted_control, если найдены отели, соответствующие критериям поиска или
    :return: negative_result, если не найдены отели, соответствующие критериям поиска
    :rtype hotels_sorted_control: List
    :rtype negative_result: str
    """
    logger.debug('user_id - {0}; вызов - функция find_hotels(user_id={1}, method_endswith={2},'
                 ' method_type={3}, refine_city_id={4}, arrival_date={5}, date_of_departure={6},'
                 ' min_price={7}, max_price={8}, adults_quantity={9}, children_ages={10},'
                 ' max_distance_from_center={11}'.
                 format(user_id, user_id, method_endswith,
                        method_type, refine_city_id, arrival_date,
                        date_of_departure, min_price, max_price,
                        adults_quantity, str(children_ages),
                        max_distance_from_center))

    response: Response | int = get_api_request(user_id=user_id, method_endswith=method_endswith,
                                               method_type=method_type, city=None,
                                               refine_city_id=refine_city_id, arrival_date=arrival_date,
                                               date_of_departure=date_of_departure, min_price=min_price,
                                               max_price=max_price, adults_quantity=adults_quantity,
                                               children_ages=children_ages, hotel_id=None)

    if type(response) == int:
        logger.info('user_id - {0}; результат работы функции find_hotels(user_id={1},'
                    ' method_endswith={2},'
                    ' method_type={3}, refine_city_id={4}, arrival_date={5}, date_of_departure={6},'
                    ' min_price={7}, max_price={8}, max_distance_from_center={9}) = {10}'.
                    format(user_id, user_id, method_endswith,
                           method_type, refine_city_id, arrival_date,
                           date_of_departure, min_price, max_price,
                           adults_quantity, str(children_ages),
                           max_distance_from_center, response))

        return response

    else:
        data: Any = json.loads(response.text)

        with open('hotels.json', 'w') as file:
            json.dump(data, file, indent=4)

            logger.debug('user_id - {}; запись в файл hotels.json'.format(user_id))

        negative_result: str = 'not found'

        with open('hotels.json', 'r') as file:
            control_data: Dict = json.load(file)

        if 'errors' in control_data.keys():
            logger.info('user_id - {0}; результат работы функции find_hotels(user_id={1},'
                        ' method_endswith={2},'
                        ' method_type={3}, refine_city_id={4}, arrival_date={5}, date_of_departure={6},'
                        ' min_price={7}, max_price={8}, max_distance_from_center={9}) = {10}'.
                        format(user_id, user_id, method_endswith,
                               method_type, refine_city_id, arrival_date,
                               date_of_departure, min_price, max_price,
                               adults_quantity, str(children_ages),
                               max_distance_from_center, negative_result))

            return negative_result

        else:
            hotels_sorted: List = []

            hotels_sorted_control: List = []

            for i_data in data['data']['propertySearch']['properties']:
                hotels_sorted.append([i_data['id'], i_data['name'], i_data['price']['lead']['amount'],
                                      i_data['destinationInfo']['distanceFromDestination']['value']])

            for i_hotel in hotels_sorted:
                if float(min_price) <= i_hotel[2] <= float(max_price) and i_hotel[3] <= float(max_distance_from_center):
                    hotels_sorted_control.append(i_hotel)

            if len(hotels_sorted_control) == 0:
                logger.info('user_id - {0}; результат работы функции find_hotels(user_id={1},'
                            ' method_endswith={2},'
                            ' method_type={3}, refine_city_id={4}, arrival_date={5}, date_of_departure={6},'
                            ' min_price={7}, max_price={8}, max_distance_from_center={9}) = {10}'.
                            format(user_id, user_id, method_endswith,
                                   method_type, refine_city_id, arrival_date,
                                   date_of_departure, min_price, max_price,
                                   adults_quantity, str(children_ages),
                                   max_distance_from_center, negative_result))

                return negative_result

            else:
                with open('hotels_sorted_control.json', 'w') as file:
                    json.dump(hotels_sorted_control, file, indent=4)

                    logger.debug('user_id - {}; запись в файл hotels_sorted_control.json'.format(user_id))

                logger.info('user_id - {0}; результат работы функции find_hotels(user_id={1},'
                            ' method_endswith={2},'
                            ' method_type={3}, refine_city_id={4}, arrival_date={5}, date_of_departure={6},'
                            ' min_price={7}, max_price={8}, max_distance_from_center={9}) = {10}'.
                            format(user_id, user_id, method_endswith,
                                   method_type, refine_city_id, arrival_date,
                                   date_of_departure, min_price, max_price,
                                   adults_quantity, str(children_ages),
                                   max_distance_from_center, hotels_sorted_control))

                return hotels_sorted_control
