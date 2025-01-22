from asyncmongo.collection import Collection
from asyncmongo.connection import AsyncMongoConnection


class Database:
    def __init__(self, client, name: str) -> None:
        self._name = name
        self._client = client

    def __getattr__(self, name: str) -> Collection:
        return Collection(self, name)

    @property
    def name(self):
        return self._name

    def _get_connection(self) -> AsyncMongoConnection:
        return self._client.connection

    async def list_collection_names(self) -> list[str]:
        conn = self._get_connection()
        _cmd = {"listCollections": 1, "cursor": {}}
        resp = await conn.command(self._name, _cmd)
        names = [item["name"] for item in resp["cursor"]["firstBatch"]]
        return names
