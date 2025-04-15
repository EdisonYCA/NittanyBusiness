import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'database.db')
STATIC_BACKUP_PATH = os.path.join(BASE_DIR, 'db_utils', 'static_backup')

class Config:
    FLASK_ENV = 'development'
    DB_PATH = DB_PATH
    STATIC_BACKUP_PATH = STATIC_BACKUP_PATH