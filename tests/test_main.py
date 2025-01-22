from asyncmongo import AsyncMongoClient
from asyncmongo.collection import Collection
from asyncmongo.cursor import Cursor
import asyncio


async def main():
    client = await AsyncMongoClient.create()
    exampleDB = client.exampleDB
    collection: Collection = exampleDB.collection

    await collection.drop_collection()

    await collection.insert_one({"name": "James", "age": 21})
    await collection.insert_one({"name": "Michael", "age": 28})
    await collection.insert_one({"name": "Robert", "age": 26})
    await collection.insert_one({"name": "David", "age": 29})

    cursor: Cursor = collection.find({"age": {"$gt": 25}})
    async for x in cursor:
        print(x)


asyncio.run(main())
