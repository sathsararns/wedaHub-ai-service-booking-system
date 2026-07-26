import asyncio

from app.core.database import db


async def test():
    print(await db.list_collection_names())


asyncio.run(test())