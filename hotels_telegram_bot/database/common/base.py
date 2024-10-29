"""
В этом модуле происходит инициализация базы данных, создание экземпляра класса SqliteDatabase,
объявление классов Base, BaseMessage, Meta.
"""
from peewee import SqliteDatabase, Model

db_history: SqliteDatabase = SqliteDatabase('history.db')

db_message: SqliteDatabase = SqliteDatabase('message.db')


class Base(Model):
    """
    Класс - Base. Родительский класс - Model.

    Класс, который будет использовать базу данных."""

    class Meta:
        """
        Класс, содержит единые метаданные для каждой таблицы.

        Attributes:
           database(SqliteDatabase): база данных для модели.
        """

        database: SqliteDatabase = db_history


class BaseMessage(Model):
    """
    Класс - BaseMessage. Родительский класс - Model.

    Класс, который будет использовать базу данных."""

    class Meta:
        """
        Класс, содержит единые метаданные для каждой таблицы.

        Attributes:
           database(SqliteDatabase): база данных для модели.
        """

        database: SqliteDatabase = db_message
