from collections import deque

from asyncmongo.exceptions import InvalidOperation


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

        cmd = {"find": self._collection._name}

        if self._filter:
            cmd.update({"filter": self._filter})
        if self._skip:
            cmd.update({"skip": self._skip})
        if self._limit:
            cmd.update({"limit": self._limit})

        return cmd

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

    def _check_okay_to_chain(self):
        if self._id is not None:
            return InvalidOperation("Cannot set options after executing query")

    def skip(self, skip: int) -> "Cursor":
        if not isinstance(skip, int):
            raise TypeError("Skip must be an integer")
        if skip < 0:
            raise ValueError("Skip must be >= 0")

        self._check_okay_to_chain()

        self._skip = skip
        return self

    def limit(self, limit) -> "Cursor":
        if not isinstance(limit, int):
            raise TypeError("limit must be an integer")

        self._check_okay_to_chain()

        self._limit = limit
        return self
