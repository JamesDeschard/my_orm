import importlib
import inspect
import os
import time

from settings import (ACTIVATE_TESTING, BASE_MIGRATION_PATH, CURRENT_MODELS,
                      DB_SETTINGS)

from .db_connections import ExecuteQuery
from .sql_queries import DbStatusQueriesPostgres, DbStatusQueriesSqlite


def get_status_query_class():
    if DB_SETTINGS.get('db_engine') == 'psycopg2':
        return DbStatusQueriesPostgres()
    elif DB_SETTINGS.get('db_engine') == 'sqlite3':
        return DbStatusQueriesSqlite()


def check_existence_of_migration_dir():
    if not os.path.isdir(BASE_MIGRATION_PATH):
        os.mkdir(BASE_MIGRATION_PATH)


def get_migration_file_name():
    migration_files = os.listdir(BASE_MIGRATION_PATH)
    if not migration_files:
        return '0_migration_init.txt'
    else:
        return f'{len(migration_files)}_migration_{int(time.time())}.txt'


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
    query = ExecuteQuery(query_class.get_table_columns_query(table_name)).execute(read=True)
    columns = list(map(lambda x: x[0] if type(x[0]) == str else x[1], query))
    return columns
