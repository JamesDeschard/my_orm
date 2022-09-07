import importlib
import inspect
import logging

from connect import DBStatus
from settings import DB_SETTINGS

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('UTILS')


def get_current_models():
    # Add all models from settings.py
    import models 
    module_name = 'models'
    
    classes = dict()
    for name, cls in inspect.getmembers(importlib.import_module(module_name), inspect.isclass):
        if cls.__module__ == module_name:
            classes[name] = cls
    return classes


def get_db_tables():
    return DBStatus(DB_SETTINGS).get_all_tables()


def get_table_columns(table_name):
    return DBStatus(DB_SETTINGS).get_table_columns(table_name)


if __name__ == '__main__':
    tables = get_db_tables()
    for table in tables:
        logger.info(table, get_table_columns(table))
    