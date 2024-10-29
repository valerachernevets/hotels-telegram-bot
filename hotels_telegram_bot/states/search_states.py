"""В этом модуле описывается класс состояний SearchStates(StatesGroup)."""
from telebot.handler_backends import StatesGroup, State


class SearchStates(StatesGroup):
    """
    Класс - SearchStates. Родительский класс - StatesGroup.

    Описывает состояния для корректной работы с запросами пользователя.

    Attributes:
        city (State): состояние при запросе города
        city_rewrite (State): состояние при изменении запроса города
        refined_city (State): состояние при уточнении города
        refined_city_rewrite (State): состояние при изменении уточненного города
        arrival_date (State): состояние при запросе даты приезда
        arrival_date_rewrite (State): состояние при изменении даты приезда
        date_of_departure (State): состояние при запросе даты отъезда
        date_of_departure_rewrite (State): состояние при изменении даты отъезда
        min_price (State): состояние при запросе минимальной цены проживания за сутки
        min_price_rewrite (State): состояние при изменении минимальной цены проживания за сутки
        max_price (State): состояние при запросе максимальной цены проживания за сутки
        max_price_rewrite (State): состояние при изменении максимальной цены проживания за сутки
        adults_quantity (State): состояние при запросе количества взрослых
        adults_quantity_rewrite (State): состояние при изменении количества взрослых
        children_quantity (State): состояние при запросе количества детей
        children_quantity_rewrite (State): состояние при изменении количества детей
        child_age (State): состояние при запросе возраста ребенка
        child_age_rewrite (State): состояние при изменении возраста ребенка
        single_child_age_rewrite (State): состояние при изменении возраста конкретного ребенка
        max_distance_from_center (State): состояние при запросе максимального расстояния отеля от центра города
        max_distance_from_center_rewrite (State): состояние при изменении
        максимального расстояния отеля от центра города
        check_data (State): состояние при запросе изменения или подтверждения правильности введенных данных
        sorting_method_hotels (State): состояние при запросе метода сортировки отелей
        sorting_method_hotels_rewrite (State): состояние при изменении метода сортировки отелей
        hotels (State): состояние при работе с параметрами отелей
        hotel_details (State): состояние при работе с данными по отелю, выбранному пользователем
    """

    city = State()
    city_rewrite = State()
    refined_city = State()
    refined_city_rewrite = State()
    arrival_date = State()
    arrival_date_rewrite = State()
    date_of_departure = State()
    date_of_departure_rewrite = State()
    min_price = State()
    min_price_rewrite = State()
    max_price = State()
    max_price_rewrite = State()
    adults_quantity = State()
    adults_quantity_rewrite = State()
    children_quantity = State()
    children_quantity_rewrite = State()
    child_age = State()
    child_age_rewrite = State()
    single_child_age_rewrite = State()
    max_distance_from_center = State()
    max_distance_from_center_km = State()
    max_distance_from_center_mile = State()
    max_distance_from_center_rewrite = State()
    max_distance_from_center_rewrite_km = State()
    max_distance_from_center_rewrite_mile = State()
    check_data = State()
    sorting_method_hotels = State()
    sorting_method_hotels_rewrite = State()
    hotels = State()
    hotel_details = State()
