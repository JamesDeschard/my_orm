import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


DB_SETTINGS = {
    'host':"localhost", 
    'dbname': '#####', 
    'user':'#####',
    'password':'#####', 
    'port':'5432'
}


CURRENT_MODELS = [
    'models',  
]

if __name__ == '__main__':
    pass
