import re

from sqlalchemy import URL

LINKS_PATTERN: re.Pattern[str] = re.compile(r"^/files/trades/result/upload/reports/oil_xls/oil_xls_202([543]).*")

class DBConfig:
    USER_NAME = '****'  # Введите имя пользователя постгрес
    PASSWORD = "*****" # Введите пароль пользователя постгрес
    DATABASE_NAME = 'spimex_trading_results'  # Введите название базы данных
    DB_URL = URL.create(
        drivername="postgresql+asyncpg",
        username=USER_NAME,
        password=PASSWORD,
        host="localhost",
        port=5432,
        database=DATABASE_NAME
    )

