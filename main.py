from asyncmongo import AsyncMongoClient
from asyncmongo.collection import Collection
import asyncio


async def main():
    client = await AsyncMongoClient.create()
    exampleDB = client.exampleDB
    collection: Collection = exampleDB.collection

    await collection.insert_one({"name": "Roshan"})
    print("Hello ")

asyncio.run(main())
