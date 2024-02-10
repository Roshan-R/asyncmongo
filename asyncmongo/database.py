from asyncmongo.mongo_types import OP_MSG
from asyncmongo.connection import AsyncMongoConnection


class Database:
    def __init__(self, client, name: str) -> None:
        self._command = {"$db": name}
        self._client = client

    def _get_connection(self) -> AsyncMongoConnection:
        return self._client.connection

    async def list_collection_names(self) -> list[str]:
        conn = self._get_connection()
        _cmd = {"listCollections": 1, "cursor": {}}
        _cmd.update(self._command)
        resp = await conn.send(OP_MSG.new(_cmd))
        names = [item["name"] for item in resp[0]["cursor"]["firstBatch"]]
        return names
