import os


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

BASE_MIGRATION_PATH = os.path.join(BASE_DIR, 'migrations')

DB_SETTINGS = {
    # 'db_engine': 'psycopg2',
    # 'db_settings': {
    #     'host':"localhost", 
    #     'dbname': 'orm', 
    #     'user':'postgres',
    #     'password':'jiimidu77', 
    #     'port':'5432'
    # },
    'db_engine': 'sqlite3',
    'db_settings': 'db.sqlite3',   
}


# Will add the test_models to the models list
ACTIVATE_TESTING = True


CURRENT_MODELS = [
    # Add names of files containing models here
    'models',  
]