import copy
import importlib
import inspect
import itertools
import os
import time

from settings import (ACTIVATE_TESTING, BASE_MIGRATION_PATH, CURRENT_MODELS,
                      DB_SETTINGS)

from .db_connections import ExecuteQuery
from .sql_queries import DbStatusQueriesPostgres, DbStatusQueriesSqlite


def get_status_query_class():
    """
    Gets the BdQuery class corresponding to the database engine.
    """
    if DB_SETTINGS.get('db_engine') == 'psycopg2':
        return DbStatusQueriesPostgres()
    elif DB_SETTINGS.get('db_engine') == 'sqlite3':
        return DbStatusQueriesSqlite()


def check_existence_of_migration_dir():
    """
    Creates a migration directory if it does not exist.
    """
    if not os.path.isdir(BASE_MIGRATION_PATH):
        os.mkdir(BASE_MIGRATION_PATH)


def get_migration_file_name():
    """
    Set the current migration file name.
    """
    migration_files = os.listdir(BASE_MIGRATION_PATH)
    if not migration_files:
        return '0_migration_init.txt'
    else:
        return f'{len(migration_files)}_migration_{int(time.time())}.txt'


def get_current_models():
    """
    This function returns a dictionary containing all the classes defined in the
    CURRENT_MODELS list set in the settings.py file.
    """
    if ACTIVATE_TESTING:
        CURRENT_MODELS.append('tests.test_models')
    
    classes = dict()
    for module in CURRENT_MODELS:
        module_classes = inspect.getmembers(importlib.import_module(module), inspect.isclass)
        for name, cls in module_classes:
            if cls.__module__ == module:
                classes[name] = cls
    return classes


def has_relationship(class_name):  
    """
    This function returns True if the class has a ManyToMany or a ForeignKey field.
    """
    if hasattr(class_name, 'relation_tree'):
        if 'ManyToManyField' in class_name.relation_tree:
            return True
        elif 'ForeignKey' in class_name.relation_tree:
            return True
    return False


def relations():
    return ['ForeignKey', 'OneToOneField', 'ManyToManyField'] 


def get_relation_classes_without_relation_fields():
    """
    This class returns a set containing all the classes that have a relation
    but which do not have a relation field in their class definition.
    """

    related_classes = set()
    relation_fields = set()
    related_models = list()
    models = get_current_models()

    
    for _class in models.values():
        if has_relationship(_class):
            relation = next(iter(_class.relation_tree))
            r_m = _class.relation_tree.get(relation)
            relation_fields.add(copy.copy(r_m).popitem()[1])
            related_models.append(r_m.values())

    related_models = set(itertools.chain.from_iterable(related_models))
    
    for model in related_models:
        if inspect.isclass(model):
            difference = relation_fields - set(model.fields.keys())
            if difference == relation_fields:
                related_classes.add(model)
            
    return related_classes


def get_db_tables():
    """
    Returns a list of all the tables in the database.
    """
    query_class = get_status_query_class()
    query = ExecuteQuery(query_class.get_all_tables_query()).execute(read=True)
    tables = list(map(lambda x: x[0], query))
    return tables


def get_table_columns(table_name):
    """
    Returns a list of all the columns in a table.
    """
    query_class = get_status_query_class()
    query = ExecuteQuery(query_class.get_table_columns_query(table_name)).execute(read=True)
    columns = list(map(lambda x: x[0] if type(x[0]) == str else x[1], query))
    return columns