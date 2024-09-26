import os
from pathlib import Path

from dotenv import load_dotenv

env_path = Path('..') / '.env'
load_dotenv(dotenv_path=env_path)

db_host = os.environ.get('POSTGRES_SERVER', 'localhost')
db_port = os.environ.get('POSTGRES_PORT', '5432')
db_user = os.environ.get('POSTGRES_USER', 'postgres')
db_pass = os.environ.get('POSTGRES_PASSWORD', '<PASSWORD>')
db_db = os.environ.get('POSTGRES_DB', 'postgres')

db_url = f"postgresql+asyncpg://{db_user}:{db_pass}@{db_host}:{db_port}/{db_db}"
