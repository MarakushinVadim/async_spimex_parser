import asyncio
import logging
import os
import time
from asyncio import ALL_COMPLETED

from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from config import DBConfig
from db import init_db, add_data
from models import Base
from parser import AsyncSpimexWebParser, parse_exel, read_data, AsyncSpimexXlsDownloader

if __name__ == '__main__':
    parser = AsyncSpimexWebParser()
    downloader = AsyncSpimexXlsDownloader()
    DATABASE_URL = DBConfig.DB_URL
    engine = create_async_engine(DATABASE_URL, echo=True, future=True, pool_size=20, max_overflow=10)
    AsyncSessionLocal = sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    metadata = MetaData()
    logger = logging.getLogger(__name__)





    async def main():
        start_time = time.time()


        session = await parser.open_session()
        page = 1

        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        while True:
            html = await parser.fetch_page(session, page)
            links = await parser.get_links(html)
            if links is None:
                break

            tasks = [asyncio.create_task(downloader.async_download_files(link, session)) for link in links]
            await asyncio.gather(*tasks)
            current_files = os.listdir('xls_files')[-len(tasks):]

            parse_tasks = [asyncio.create_task(parse_exel('xls_files/' + file)) for file in current_files]
            done, _ = await asyncio.wait(parse_tasks, return_when=ALL_COMPLETED)

            trade_tasks = [asyncio.create_task(read_data(data.result())) for data in done]
            done, _ = await asyncio.wait(trade_tasks, return_when=ALL_COMPLETED)

            current_trade_data = []
            for data in done:
                current_trade_data.extend(data.result())

            recording_tasks = [asyncio.create_task(add_data(AsyncSessionLocal, data=data)) for data in current_trade_data]
            result = await asyncio.gather(*recording_tasks)
            logger.info('Цикл успешно завершен')

            page += 1

        await parser.close_session()
        end_time = time.time()
        total_time = (end_time - start_time) / 60
        print('время работы программы - ', total_time)


        # parsed_data = await parse_exel('bulletin_file.xls')
        # trade_list = await read_data(parsed_data)
        # records = [asyncio.create_task(add_data(AsyncSessionLocal, data=data)) for data in trade_list]
        # await asyncio.gather(*records)
        # print(trade_list[0])



asyncio.run(main())



























    # links_list = []

    # async def main():
        # session = await parser.open_session()

        # num = 1
        # while num < 2:
        #     await asyncio.sleep(.5)
        #     await asyncio.create_task(parser.fetch_page(session=session, page=num))
        #
        #     num += 1
        # await parser.close_session()



        # tasks = [asyncio.create_task(parser.get_links(session=session, page=num + 1)) for num in range(403)]
        # done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_EXCEPTION)
        # for task in done:
        #     print(task)


        # async with asyncio.TaskGroup() as tg:
        #     session = await parser.open_session()
        #     try:
        #         [tg.create_task(parser.get_links(session=session, page=num + 1)) for num in range(403)]
        #     except Exception as e:
        #         print(e)
        #     # finally:
            #     await parser.close_session()

    # asyncio.run(main())


# Opening new session...<aiohttp.client.ClientSession object at 0x0000011B79D1A510


###############################################################################

    # async def main():
    #
    #     queue_links = asyncio.Queue()
    #     queue_files = asyncio.Queue()
    #
    #
    #
    #     # while not queue.empty():
    #     #     queue.put()
