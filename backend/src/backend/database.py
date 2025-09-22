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

    def update(self, table: str, data: dict, id_value: int) -> int:
        with self.cursor() as cursor:
            set_clause = ", ".join([f"`{k}` = %s" for k in data.keys()])

            params = list(data.values()) + [id_value]

            cursor.execute(f"UPDATE `{table}` SET {set_clause} WHERE `id` = %s", params)
            self.commit()
            return cursor.rowcount

    def execute_raw(self, sql: str, params: tuple = ()):
        with self.cursor() as cursor:
            cursor.execute(sql, params)
            return cursor.fetchall()


class ProjectDB:
    def __init__(
        self, host: str, user: str, password: str, database: str, port: int = 5432
    ):
        self.db = Database(
            host=host, user=user, password=password, database=database, port=port
        )
        self.table_setup()

    def table_setup(self):
        """Создание таблицы для хранения инцидентов"""
        self.db.execute_raw(
            sql="CREATE TABLE IF NOT EXIST events (id PRIMARY KEY, timestamp TIME, station VARCHAR NOT NULL, type TINYINT NOT NULL)"
        )

    def add_event(self, station: str, type: int = 0) -> None | int:
        """Добавление инцидента
        param: station название станции
        param: type тип инцидента, по умолчанию 0"""

        return self.db.insert(
            "events", {"timestamp": "LOCALTIME", "station": station, "type": type}
        )

    def get_event(self, id: int) -> dict:
        """Получение инцидента в формате словаря"""
        result = self.db.execute_raw("SELECT * FROM events WHERE id = (%s)", (id,))[0]
        return {
            "id": id,
            "timestamp": result[0],
            "station": result[1],
            "type": result[2],
        }

    def updade_event(self, id: int, data: dict) -> int:
        """Обновление инцидента по id"""
        return self.db.update("events", data, id)
