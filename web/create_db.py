import time
import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError

# Import the declarative Base from models so we can create/drop tables
from models import Base


def wait_for_postgres(engine, max_retries: int = 30, delay: float = 1.0):
    attempt = 0
    while attempt < max_retries:
        try:
            with engine.connect() as conn:
                conn.execute('SELECT 1')
                print('Database is available')
                return True
        except OperationalError:
            attempt += 1
            print(f'Waiting for database... ({attempt}/{max_retries})', file=sys.stderr)
            time.sleep(delay)
    return False


if __name__ == '__main__':
    # Build DB URL from environment (matches config.BaseConfig)
    DB_USER = os.getenv('POSTGRES_USER', 'postgres')
    DB_PASS = os.getenv('POSTGRES_PASSWORD', 'postgres')
    DB_NAME = os.getenv('POSTGRES_DB', 'postgres')
    DB_PORT = os.getenv('DATABASE_PORT', '5432')
    DB_HOST = os.getenv('POSTGRES_HOST', os.getenv('DB_HOST', 'postgres'))

    database_uri = f'postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
    engine = create_engine(database_uri)

    ok = wait_for_postgres(engine)
    if not ok:
        print('Timed out waiting for the database', file=sys.stderr)
        sys.exit(1)

    OVERWRITE = os.getenv('OVERWRITE_DB', 'true').lower() in ('1', 'true', 'yes')

    try:
        if OVERWRITE:
            print('Dropping existing tables (OVERWRITE_DB=True)...')
            with engine.connect() as conn:
                conn.execute("DROP SCHEMA public CASCADE; CREATE SCHEMA public;")
            print('Dropped tables and recreated schema')

        print('Creating tables...')
        Base.metadata.create_all(bind=engine)
        print('Tables created')
    except Exception as e:
        print('Error creating tables:', e, file=sys.stderr)
        sys.exit(1)
