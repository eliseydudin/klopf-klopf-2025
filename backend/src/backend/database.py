import psycopg2


class Database:
    """Класс датабазы проекта"""

    def __init__(
        self, host: str, user: str, password: str, database: str, port: int = 5432
    ):
        self.conn = psycopg2.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            port=port,
            options="-c client_encoding=UTF8",
        )

    def cursor(self):
        return self.conn.cursor()

    def close(self):
        """Закрытие соединения с базой данных"""
        self.conn.close()

    def commit(self):
        self.conn.commit()

    def rollback(self):
        self.conn.rollback()

    def insert(self, table: str, data: dict) -> None | int:
        with self.cursor() as cursor:
            columns = ", ".join(data.keys())
            placeholders = ", ".join([f"%({k})s" for k in data.keys()])

            cursor.execute(
                "INSERT INTO %s (%s) VALUES (%s) RETURNING id",
                (table, columns, placeholders),
            )
            self.commit()

            result = cursor.fetchone()
            if result is None:
                return None
            else:
                return result[0]

    def update(
        self, table: str, data: dict, condition: str, condition_params: tuple
    ) -> int:
        with self.cursor() as cursor:
            set_clause = ", ".join([f"{k} = %s" for k in data.keys()])

            params = list(data.values())
            if condition_params:
                params.extend(condition_params)

            cursor.execute("UPDATE %s SET %s WHERE %s", (table, set_clause, condition))
            self.commit()

            return cursor.rowcount

    def execute_raw(self, sql: str, params: tuple = ()):
        with self.cursor() as cursor:
            cursor.execute(sql, params)
            return cursor.fetchall()
