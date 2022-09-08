import importlib
import inspect

import settings

from .connect import DBStatus


def get_current_models():
    if settings.ACTIVATE_TESTING:
        settings.CURRENT_MODELS.append('tests.test_models')
    classes = dict()
    for module in settings.CURRENT_MODELS:
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
    return DBStatus(settings.DB_SETTINGS).get_all_tables()


def get_table_columns(table_name):
    return DBStatus(settings.DB_SETTINGS).get_table_columns(table_name)
