import asyncio

from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from db import init_db, add_data
from models import Base
from parser import AsyncSpimexWebParser, parse_exel, read_data

if __name__ == '__main__':
    parser = AsyncSpimexWebParser()
    DATABASE_URL = f'postgresql+asyncpg://user:password@localhost/dbname'
    engine = create_async_engine(DATABASE_URL, echo=True)
    AsyncSessionLocal = sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    metadata = MetaData()



    async def main():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        # await init_db(engine)
        parsed_data = await parse_exel('bulletin_file.xls')
        trade_list = await read_data(parsed_data)
        records = [asyncio.create_task(add_data(AsyncSessionLocal, data=data)) for data in trade_list]
        await asyncio.gather(*records)
        print(trade_list[0])



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
