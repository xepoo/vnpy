""""""
from peewee import (
    MySQLDatabase,
    PostgresqlDatabase,
    SqliteDatabase,
)
from vnpy.trader.utility import get_file_path
from .database import BaseDatabaseManager, Driver

database_db = None

def init(settings: dict) -> BaseDatabaseManager:
    database_db = init_db(settings)
    driver = Driver(settings["driver"])
    if driver is Driver.MONGODB:
        return init_nosql(driver=driver, settings=settings)
    else:
        return init_sql(database_db, driver=driver, settings=settings)


def init_sqlite(settings: dict):
    database = settings["database"]
    path = str(get_file_path(database))
    db = SqliteDatabase(path)
    return db


def init_mysql(settings: dict):
    keys = {"database", "user", "password", "host", "port"}
    settings = {k: v for k, v in settings.items() if k in keys}
    db = MySQLDatabase(**settings)
    return db


def init_postgresql(settings: dict):
    keys = {"database", "user", "password", "host", "port"}
    settings = {k: v for k, v in settings.items() if k in keys}
    db = PostgresqlDatabase(**settings)
    return db

def create_db(driver: Driver, settings: dict):
    init_funcs = {
        Driver.SQLITE: init_sqlite,
        Driver.MYSQL: init_mysql,
        Driver.POSTGRESQL: init_postgresql,
    }
    assert driver in init_funcs

    db = init_funcs[driver](settings)
    return db


def init_db(settings: dict):
    keys = {'database', "host", "port", "user", "password","driver"}
    settings = {k: v for k, v in settings.items() if k in keys}
    driver = Driver(settings["driver"])
    if driver is Driver.MONGODB:
        return None
    else:
        return create_db(driver=driver, settings=settings)

def init_sql(db, driver: Driver, settings: dict):
    from .database_sql import init
    _database_manager = init(db, driver)
    return _database_manager


def init_nosql(driver: Driver, settings: dict):
    from .database_mongo import init
    _database_manager = init(driver, settings=settings)
    return _database_manager
