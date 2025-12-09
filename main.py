import asyncio
import logging
import os
import time
from asyncio import ALL_COMPLETED

import aiohttp
from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from config import DBConfig
from db import DataBase
from parser import AsyncSpimexWebParser, parse_exel, read_data, AsyncSpimexXlsDownloader

if __name__ == "__main__":
    parser = AsyncSpimexWebParser()
    downloader = AsyncSpimexXlsDownloader()
    DATABASE_URL = DBConfig.DB_URL
    engine = create_async_engine(
        DATABASE_URL, echo=True, future=True, pool_size=20, max_overflow=10
    )
    database = DataBase(engine)
    AsyncSessionLocal = sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    metadata = MetaData()
    logger = logging.getLogger(__name__)

    async def main():
        start_time = time.time()
        page = 1

        try:
            session = await parser.open_session()
            await database.init_db()

            while True:
                html = await parser.fetch_page(session, page)
                links = await parser.get_links(html)
                if links is None:
                    break

                tasks = [
                    asyncio.create_task(downloader.async_download_files(link, session))
                    for link in links
                ]
                await asyncio.gather(*tasks)
                current_files = os.listdir("xls_files")[-len(tasks) :]

                parse_tasks = [
                    asyncio.create_task(parse_exel("xls_files/" + file))
                    for file in current_files
                ]
                done, _ = await asyncio.wait(parse_tasks, return_when=ALL_COMPLETED)

                trade_tasks = [
                    asyncio.create_task(read_data(data.result())) for data in done
                ]
                done, _ = await asyncio.wait(trade_tasks, return_when=ALL_COMPLETED)

                current_trade_data = []
                for data in done:
                    current_trade_data.extend(data.result())

                recording_tasks = [
                    asyncio.create_task(database.add_data(AsyncSessionLocal, data=data))
                    for data in current_trade_data
                ]
                result = await asyncio.gather(*recording_tasks)
                page += 1

        except aiohttp.ClientConnectionError as e:
            logging.warning(f"Соединение не удалось - {e}")
        except asyncio.TimeoutError as e:
            logging.warning(f"Таймаут: {e}")
        except aiohttp.InvalidURL as e:
            logging.warning(f"Неверный URL: {e}")
        except aiohttp.ClientResponseError as e:
            logging.warning(f"HTTP {e.status}: {e.message}")

        finally:
            await parser.close_session()
            end_time = time.time()
            total_time = (end_time - start_time) / 60
            print("время работы программы - ", total_time)


asyncio.run(main())
