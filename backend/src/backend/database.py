import psycopg2
from .config import host, user, password, db_name


def check():
    try:
        connection = psycopg2.connect(
            host=host,
            user=user,
            password=password,
            database=db_name,
            options="-c client_encoding=UTF8",
        )
        with connection.cursor() as cursor:
            cursor.execute("SELECT version()")
            print(cursor.fetchone())

    except Exception as ex:
        print(f"[INFO] Error while working with PostgreSQL: {ex}")
    finally:
        pass
