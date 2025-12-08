import asyncio

from parser import AsyncSpimexWebParser

if __name__ == '__main__':
    parser = AsyncSpimexWebParser()


    links_list = []

    async def main():
        session = await parser.open_session()
        num = 1
        while num < 2:
            await asyncio.sleep(.5)
            await asyncio.create_task(parser.fetch_page(session=session, page=num))

            num += 1
        await parser.close_session()
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

    asyncio.run(main())


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
