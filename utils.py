import importlib
import inspect

from connect import DBStatus
from settings import DB_SETTINGS


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

    print(get_db_tables())
    for table in get_db_tables():
        print(get_table_columns(table))

    