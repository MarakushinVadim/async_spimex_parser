import asyncio
import re
import logging
from typing import Optional

import aiohttp
from bs4 import BeautifulSoup

from config import LINKS_PATTERN

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# class AsyncSpimexXlsDownloader:
#     @staticmethod
#     async def async_download_files(link):
#         link_url = f"https://spimex.com{link['href']}"
#         name = asyncio.current_task().get_name()
#         response = requests.get(link_url)
#         response.raise_for_status()
#         async with aiofiles.open(f'xls_files/file_{name}.xls', "wb") as file:
#             await file.write(response.content)
#         logging.info(f"Файл успешно асинхронно скачан: {link_url}")



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
        task = asyncio.current_task()
        async with session.get(url) as response:
            if response.status == 200:
                html = await response.text()
                print(html)
                logger.info(f'Страница {page} загружена')
                return html

    async def fetch_page_(self, session, page):
        url = f'{self.base_url}{page}'
        task = asyncio.current_task()
        async with session.get(url) as response:
            if response.status == 200:
                html = await response.text()
                print(html)
                logger.info(f'Страница {page} загружена')
                return html


    @staticmethod
    async def get_links(session, page: int = 1):
        try:
            await asyncio.sleep(.1)
            async with session.get(f'https://spimex.com/markets/oil_products/trades/results/?page=page-{page}') as response:
                html = await response.text()
                print(html)
                soup = BeautifulSoup(html, 'html.parser')
                links = soup.find_all(
                    "a",
                    attrs={
                        "class": "accordeon-inner__item-title link xls",
                        "href": re.compile(LINKS_PATTERN),
                    },
                )
                print(f'Found {links} links')
                page += 1
                if len(links) == 0:
                    raise Exception(f"Все ссылки собраны")

                return links
        except Exception as e:
            print(e)


# parser = AsyncSpimexWebParser()
#
# async def main():
#     task = asyncio.create_task(parser.get_links())
#     await task
#
# asyncio.run(main())