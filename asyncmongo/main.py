from client import AsyncMongoClient

import asyncio


async def main():
    client = await AsyncMongoClient.create("localhost", 27017)
    db = client.exampleDB

    names = await db.list_collection_names()
    print(names)



asyncio.run(main())
