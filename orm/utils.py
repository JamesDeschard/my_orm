import importlib
import inspect

from settings import DB_SETTINGS, ACTIVATE_TESTING, CURRENT_MODELS

from .db_connections import ExecuteQuery
from .sql_queries import DbStatusQueriesPostgres, DbStatusQueriesSqlite


def get_status_query_class():
    if DB_SETTINGS.get('db_engine') == 'psycopg2':
        return DbStatusQueriesPostgres()
    elif DB_SETTINGS.get('db_engine') == 'sqlite3':
        return DbStatusQueriesSqlite()


def get_current_models():
    if ACTIVATE_TESTING:
        CURRENT_MODELS.append('tests.test_models')
    
    classes = dict()
    for module in CURRENT_MODELS:
        module_classes = inspect.getmembers(importlib.import_module(module), inspect.isclass)
        for name, cls in module_classes:
            if cls.__module__ == module:
                classes[name] = cls
    return classes


def get_class_module(field_name):
        for _attr, _class in get_current_models().items():
            if _attr.lower() == field_name:
                return _class.__module__


def get_db_tables():
    query_class = get_status_query_class()
    query = ExecuteQuery(query_class.get_all_tables_query()).execute(read=True)
    tables = list(map(lambda x: x[0], query))
    return tables


def get_table_columns(table_name):
    query_class = get_status_query_class()
    query = ExecuteQuery(query_class.table_exists_query(table_name)).execute(read=True)
    columns = list(map(lambda x: x[0] if type(x[0]) == str else x[1], query))
    return columns



