import pytest

import asyncmongo.client


@pytest.mark.asyncio
async def test_list_all_collection_names():
    client = await asyncmongo.client.AsyncMongoClient.create()
    db = client.exampleDB
    names = await db.list_collection_names()
    assert isinstance(names, list)
