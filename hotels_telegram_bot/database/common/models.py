"""В этом модуле объявляются классы User, Request, Message."""
from peewee import DateTimeField, IntegerField, TextField, ForeignKeyField

from database.common.base import Base, BaseMessage

from datetime import datetime


class User(Base):
    """
    Класс -  User. Родительский класс - Base.

    Описывает пользователя телеграм-бота.

    Attributes:
        created_at(datetime): дата и время первого использования телеграм-бота
        user_id(int): id пользователя
    """

    created_at: DateTimeField = DateTimeField(default=datetime.now())
    user_id: IntegerField = IntegerField(primary_key=True, null=True)


class Request(Base):
    """
    Класс - Request. Родительский класс - Base.

    Описывает запрос пользователя.

    Attributes:
        created_at(datetime): время создания запроса
        user(int): id пользователя
        city(str): название города, который ввел пользователь
        refined_city(str): уточненный город
        arrival_date(datetime): дата приезда
        date_of_departure(datetime): дата отъезда
        min_price(int): минимальная стоимость номера за сутки
        max_price(int): максимальная стоимость номера за сутки
        max_distance_from_center(int): максимальное удаление отеля от центра города
        sorting_method_hotels(str): метод сортировки, который применил пользователь
        hotels(str): список отелей подходящих под запрос пользователя
        hotel_id(int): id отеля
        hotel_name(str): название отеля
        hotel_address(str): адрес отеля
        hotel_photo_url(str): ссылка на фото отеля

    """

    created_at: DateTimeField = DateTimeField(default=datetime.now())
    user: ForeignKeyField = ForeignKeyField(User, backref='request', null=True)
    city: TextField = TextField(null=True)
    refined_city: TextField = TextField(null=True)
    arrival_date: DateTimeField = DateTimeField(null=True)
    date_of_departure: DateTimeField = DateTimeField(null=True)
    min_price: IntegerField = IntegerField(null=True)
    max_price: IntegerField = IntegerField(null=True)
    adults_quantity: IntegerField = IntegerField(null=True)
    children_quantity: IntegerField = IntegerField(null=True)
    children_ages: TextField = TextField(null=True)
    max_distance_from_center: IntegerField = IntegerField(null=True)
    sorting_method_hotels: TextField = TextField(null=True)
    hotels: TextField = TextField(null=True)
    hotel_id: IntegerField = IntegerField(null=True)
    hotel_name: TextField = TextField(null=True)
    hotel_address: TextField = TextField(null=True)
    hotel_photo_url: TextField = TextField(null=True)


class Message(BaseMessage):
    """
    Класс - Message. Родительский класс - BaseMessage.

    Описывает сообщения от пользователя.

    Attributes:
        created_at(datetime): время создания запроса
        chat_id(int): id чата
        message_id(int): id сообщения от пользователя
    """
    created_at: DateTimeField = DateTimeField(default=datetime.now())
    chat_id: IntegerField = IntegerField(null=True)
    message_id: IntegerField = IntegerField(null=True)
