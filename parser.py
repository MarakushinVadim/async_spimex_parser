import re
import logging
from datetime import datetime

import aiofiles
import aiohttp
import pandas as pd
from bs4 import BeautifulSoup

from config import LINKS_PATTERN
from models import Trade

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

file_counter = 1

class AsyncSpimexXlsDownloader:
    @staticmethod
    async def async_download_files(link, session):
        global file_counter
        response = await session.get(link)
        content = await response.read()
        async with aiofiles.open(f'xls_files/file_{file_counter}.xls', "wb") as file:
            await file.write(content)
        file_counter += 1
        logging.info(f"Файл успешно асинхронно скачан: {link}")



class AsyncSpimexWebParser:

    def __init__(self):
        self.session = None
        self.base_url = "https://spimex.com/markets/oil_products/trades/results/?page=page-"

    async def open_session(self):
        if self.session is None:
            self.session = aiohttp.ClientSession()
            print(f'Opening new session...{self.session}')
        return self.session


    async def close_session(self):
        if self.session:
            await self.session.close()
            self.session = None
    #
    # async def get_count_pages(self):
    #     async with self.open_session() as

    async def fetch_page(self, session, page):
        url = f'{self.base_url}{page}'

        async with session.get(url) as response:
            if response.status == 200:
                html = await response.text()
                logger.info(f'Страница {page} загружена')
                return html


    @staticmethod
    async def get_links(html):
        soup = BeautifulSoup(html, 'html.parser')
        links = soup.find_all(
            "a",
            attrs={
                "class": "accordeon-inner__item-title link xls",
                "href": re.compile(LINKS_PATTERN),
            },
        )
        logger.info(f'Найдено {len(links)} ссылок')
        if len(links) == 0:
            logger.info('Скрипт по поиску ссылок отработал')
            return None
        href_links = ['https://spimex.com'+link['href'] for link in links]
        return href_links



# parser = AsyncSpimexWebParser()
#
# async def main():
#     task = asyncio.create_task(parser.get_links())
#     await task
#
# asyncio.run(main())

async def parse_exel(file_path):
    exel_file = pd.read_excel(file_path)
    date = datetime.strptime(
        exel_file.iloc[2]["Форма СЭТ-БТ"].replace("Дата торгов: ", ""),
        "%d.%m.%Y",
    )
    row_number = (
            int(
                exel_file[
                    exel_file["Форма СЭТ-БТ"]
                    == "Единица измерения: Метрическая тонна"
                    ].index[0]
            )
            + 2
    )
    exel_file = pd.read_excel(
        file_path, usecols="B:F,O", skiprows=row_number
    )
    exel_file = exel_file[
        exel_file["Количество\nДоговоров,\nшт."] != "-"
        ].dropna()
    exel_file = exel_file[exel_file["Количество\nДоговоров,\nшт."] != None]
    logging.info("Данные успешно прочитаны из Excel файла")
    return [exel_file, date]


async def read_data(parsed_data: list):
    trade_list = []
    entries_list = parsed_data[0]
    for entry in range(len(entries_list)):
        try:
            trade = Trade(
                exchange_product_id=entries_list.iloc[entry]["Код\nИнструмента"],
                exchange_product_name=entries_list.iloc[entry][
                    "Наименование\nИнструмента"
                ],
                oil_id=entries_list.iloc[entry]["Код\nИнструмента"][:4],
                delivery_basis_id=entries_list.iloc[entry]["Код\nИнструмента"][4:7],
                delivery_basis_name=entries_list.iloc[entry]["Базис\nпоставки"],
                delivery_type_id=entries_list.iloc[entry]["Код\nИнструмента"][-1],
                volume=int(
                    entries_list.iloc[entry][
                        "Объем\nДоговоров\nв единицах\nизмерения"
                    ]
                ),
                total=int(entries_list.iloc[entry]["Обьем\nДоговоров,\nруб."]),
                count=int(entries_list.iloc[entry]["Количество\nДоговоров,\nшт."]),
                date=parsed_data[1],
            )
            trade_list.append(trade)
        except ValueError as e:
            logging.error(f"Ошибка преобразования типов в записи {entry + 1}: {e}")
        except KeyError as e:
            logging.error(f"Отсутствующий ключ в записи {entry + 1}: {e}")
        except Exception as e:
            logging.error(f"Неизвестная ошибка в записи {entry + 1}: {e}")
        except IndexError as e:
            logging.error(f'Таблица не найдена {e}')
    return trade_list