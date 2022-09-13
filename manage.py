import logging
import sys
import unittest

import settings
from orm.db_migrations import ExecuteMigrations, PopulateMigrationFile
from orm.utils import (get_current_models, get_db_tables,
                       get_relation_classes_without_relation_fields,
                       get_table_columns)
from tests.model_fields_test import TestFields
from tests.orm_base_model_test import TestCRUD, TestRelations
from tests.queryset_test import TestQuerySets

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('DB schema details ---> ')


def makemigrations():
    return PopulateMigrationFile().manager()


def migrate():
    return ExecuteMigrations().manager()


def show_db_schema():
    tables = get_db_tables()
    for table in tables:
        logger.info(f'{table} ---> {get_table_columns(table)}')


def test():
    if settings.ACTIVATE_TESTING:
        logger.info('Running tests...')
        migrations = unittest.TestLoader().loadTestsFromTestCase(TestFields)
        crud = unittest.TestLoader().loadTestsFromTestCase(TestCRUD)
        relations = unittest.TestLoader().loadTestsFromTestCase(TestRelations)
        queryset = unittest.TestLoader().loadTestsFromTestCase(TestQuerySets)
        
        suite= unittest.TestSuite([migrations, crud, queryset, relations])
        runner = unittest.TextTestRunner()
        runner.run(suite)
        logger.info('Tests completed')
    else:
        logger.info('Testing is not activated in settings.py')


if __name__ == '__main__':
    
    if len(sys.argv) > 1:
        manager_arg = sys.argv[1]
        if manager_arg == 'migrate':
            makemigrations()
            migrate()
        elif manager_arg == 'db_tables':
            show_db_schema()
        elif manager_arg == 'my_models':
            logger.info(f'{get_current_models()}')
        elif manager_arg == 'test':
            test()
        elif manager_arg == 'relations':
            print(get_relation_classes_without_relation_fields())
        else:
            sys.stdout.write("Invalid command")
    else:
        sys.stdout.write("No command provided")
