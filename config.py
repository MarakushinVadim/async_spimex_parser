import os
import re

from sqlalchemy import URL
import dotenv

dotenv.load_dotenv()

LINKS_PATTERN: re.Pattern[str] = re.compile(
    r"^/files/trades/result/upload/reports/oil_xls/oil_xls_202([543]).*"
)


class DBConfig:
    USER_NAME = os.getenv("USER_NAME")  # Введите имя пользователя постгрес
    PASSWORD = os.getenv("PASSWORD")  # Введите пароль пользователя постгрес
    DATABASE_NAME = os.getenv("DATABASE_NAME")  # Введите название базы данных
    DB_URL = URL.create(
        drivername="postgresql+asyncpg",
        username=USER_NAME,
        password=PASSWORD,
        host="localhost",
        port=5432,
        database=DATABASE_NAME,
    )
