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

class DataBase:
    """Класс датабазы проекта"""
    def __init__(self, host:str, user:str, password:str, database:str, port:int = 5432):
        self.connection_params = {
            'host': host,
            'database': database,
            'user': user,
            'password': password,
            'port': port,
            'options': "-c client_encoding=UTF8"
        }
        
        self.conn = None
        self.cursor = None

    def connect(self):
        """Соединение с базой данных"""
        try:
            self.conn = psycopg2.connect(**self.connection_params)
            self.cursor = self.conn.cursor()
        except Exception as e:
            print(f"[ERROR] DataBase connection error: {e}")
    
    def close(self):
        """Закрытие соединения с базой данных"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()

    def execute(self, query:str, params:dict, commit:bool = False):
        try:
            self.cursor.execute(query, params)

            if query.strip().upper().startswith("SELECT"):
                return self.cursor.fatchall()
            if commit:
                self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            print(f"[ERROR] DataBase execution error: {e}")
            raise

    def commit(self):
        if self.conn:
            self.conn.commit()

    def rollback(self):
        if self.conn:
            self.conn.rollback()

    def insert(self, table:str, data:dict):
        columns = ', '.join(data.keys())
        placeholders = ', '.join([f'%({k})s' for k in data.keys()])
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders}) RETURNING id"

        self.execute(query, data)
        self.commit()
        return self.cursor.fetchone()[0]

    def update(self, table:str, data:dict, condition:str, condition_params:tuple) -> int:

        set_clause = ', '.join([f"{k} = %s" for k in data.keys()])
        query = f"UPDATE {table} SET {set_clause} WHERE {condition}"
        
        params = list(data.values())
        if condition_params:
            params.extend(condition_params)

        self.cursor.execute(query, params)
        self.commit()
        return self.cursor.rowcount