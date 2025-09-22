import os
import dotenv


class Config:
    def __init__(self) -> None:
        dotenv.load_dotenv("./.env")
        self.HOST = os.environ["HOST"]
        self.USER = os.environ["USER"]
        self.PASSWORD = os.environ["PASSWORD"]
        self.DATABASE_NAME = os.environ["DATABASE_NAME"]
        self.PORT = os.environ["PORT"]
