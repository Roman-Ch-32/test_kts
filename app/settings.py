import os


db_host = os.environ.get('POSTGRES_SERVER', 'localhost')
db_port = os.environ.get('POSTGRES_PORT', '5432')
db_user = os.environ.get('POSTGRES_USER', 'admin')
db_pass = os.environ.get('POSTGRES_PASSWORD', 'admin')
db_db = os.environ.get('POSTGRES_DB', 'admin')

db_url = f"postgresql+asyncpg://{db_user}:{db_pass}@{db_host}:{db_port}/{db_db}"
