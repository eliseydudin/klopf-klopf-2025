import psycopg2
from loguru import logger
from .config import BRANCHES


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

    def update(self, table: str, data: dict, id_value: int) -> int:
        with self.cursor() as cursor:
            set_clause = ", ".join([f"`{k}` = %s" for k in data.keys()])

            params = list(data.values()) + [id_value]

            cursor.execute(f"UPDATE `{table}` SET {set_clause} WHERE `id` = %s", params)
            self.commit()
            return cursor.rowcount

    def execute_raw(self, sql: str, params: tuple = (), ignore_result: bool = False):
        try:
            with self.cursor() as cursor:
                cursor.execute(sql, params)

                if not ignore_result:
                    return cursor.fetchall()

                return None
        except psycopg2.ProgrammingError as err:
            logger.error(f"a psql error occurred: {err}")
            return None


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
            sql="CREATE TABLE IF NOT EXISTS events (id bigint GENERATED ALWAYS AS IDENTITY, timestamp TIME, station VARCHAR NOT NULL, type int NOT NULL)",
            ignore_result=True,
        )

    def add_event(self, station: str, type: int = 0) -> None | int:
        """Добавление инцидента
        param: station название станции
        param: type тип инцидента, по умолчанию 0"""

        #    "events", {"timestamp": "LOCALTIME", "station": station, "type": type}
        res = self.db.execute_raw(
            "INSERT INTO events (timestamp, station, type) VALUES(LOCALTIME(6), %s, %s) RETURNING id",
            (station, type),
        )
        self.db.commit()

        if res is None:
            return None
        else:
            return res[0][0]

    def get_event_by_id(self, id: int) -> dict | None:
        """Получение инцидента в формате словаря"""
        result = self.db.execute_raw("SELECT * FROM events WHERE id = (%s)", (id,))

        if result is None:
            return None
        else:
            result = result[0]

        return {
            "id": id,
            "timestamp": result[0],
            "station": result[1],
            "type": result[2],
        }

    def updade_event(self, id: int, data: dict) -> int:
        """Обновление инцидента по id"""
        return self.db.update("events", data, id)

    def get_events_by(
        self,
        parameter: str,
        param_value: str,
        limit: int | None,
        sort_by: str = "timestamp",
    ) -> list[dict] | None:
        logger.info(f"{param_value=}, {parameter=}")

        limit_query = f"LIMIT {abs(limit)}" if limit is not None else ""

        result = self.db.execute_raw(
            f"SELECT * FROM events WHERE ({parameter}) = (%s) {limit_query}",
            (param_value,),
        )

        if result is None:
            return None
        else:
            events_list = []
            for item in result:
                events_list.append(
                    {
                        "id": item[0],
                        "timestamp": item[1],
                        "station": item[2],
                        "type": item[3],
                    }
                )
            sorted_list = sorted(events_list, key=lambda x: x[sort_by])
            return sorted_list

    def get_branch_by_station(self, station: str) -> list[str]:
        lines: list[str] = []

        for line, stations in BRANCHES.items():
            if station in stations:
                lines.append(line)

        return lines

    def get_stations_by_branch(self, branch: str) -> list[str]:
        return BRANCHES[branch]
