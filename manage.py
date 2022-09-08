import logging
import sys
import unittest

import settings

from orm.db_migrations import ExecuteMigrations, PopulateMigrationFile
from orm.utils import get_current_models, get_db_tables, get_table_columns
from tests.orm_test import TestCRUD
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
        crud = unittest.TestLoader().loadTestsFromTestCase(TestCRUD)
        queryset = unittest.TestLoader().loadTestsFromTestCase(TestQuerySets)
        suite= unittest.TestSuite([crud, queryset])
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
            
        else:
            sys.stdout.write("Invalid command")
    else:
        sys.stdout.write("No command provided")
