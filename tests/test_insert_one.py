import pytest

import asyncmongo.client


@pytest.mark.asyncio
async def test_insert_one():
    client = await asyncmongo.client.AsyncMongoClient.create()
    db = client.exampleDB
    products = db.products
    resp = await products.insert_one({"x": 100})
    assert resp["ok"] == 1.0
