import logging
import unittest
import sys

from orm.db_migrations import ExecuteMigrations, PopulateMigrationFile
from orm.utils import get_db_tables, get_table_columns, get_current_models
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
    crud = unittest.TestLoader().loadTestsFromTestCase(TestCRUD)
    queryset = unittest.TestLoader().loadTestsFromTestCase(TestQuerySets)
    suite= unittest.TestSuite([crud, queryset])
    runner = unittest.TextTestRunner()
    runner.run(suite)



if __name__ == '__main__':
    if len(sys.argv) > 1:
        manager_arg = sys.argv[1]
        if manager_arg == 'makemigrations':
            makemigrations()
        elif manager_arg == 'migrate':
            migrate()
        elif manager_arg == 'double':
            makemigrations()
            migrate()
        elif manager_arg == 'dbtables':
            show_db_schema()
        elif manager_arg == 'models':
            logger.info(f'{get_current_models()}')
        elif manager_arg == 'test':
            test()
            
        else:
            sys.stdout.write("Invalid command")
    else:
        sys.stdout.write("No command provided")
