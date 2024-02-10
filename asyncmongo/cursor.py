from collections import deque


class Cursor:
    def __init__(
        self,
        collection,
        skip: int = 0,
        limit: int = 0,
        batch_size: int = 0,
        filter: dict | None = None,
    ):
        self._collection = collection
        self._skip = skip
        self._limit = limit
        self._batch_size = batch_size
        self._filter = filter

        self._id: str | None = None  # id of the cursor
        self._data: deque = deque()
        self._connection = None
        self._killed: bool = False

    def __aiter__(self) -> "Cursor":
        return self

    def _create_command(self):
        if self._id and self._id != 0:
            return {"getMore": self._id, "collection": self._collection._name}

        return {"find": self._collection._name}

    async def _refresh(self):
        if self._killed:
            return False

        cmd = self._create_command()
        if not self._connection:
            self._connection = self._collection._database._get_connection()
        res = await self._connection.command(
            command=cmd, database_name=self._collection._database.name
        )

        self._id = res["cursor"]["id"]
        if self._id == 0:
            self._killed = True

        results = list(res["cursor"].values())
        self._data.extend(results[0])

        return len(self._data)

    async def __anext__(self):
        if len(self._data):
            return self._data.popleft()

        is_refreshed = await self._refresh()

        if not is_refreshed:
            raise StopAsyncIteration

        return self._data.popleft()
