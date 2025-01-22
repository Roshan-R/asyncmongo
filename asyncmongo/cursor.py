from collections import deque


class Cursor:
    """
    Represents a cursor for iterating over query results from a MongoDB collection.
    Supports asynchronous iteration and query options such as skip and limit.
    """

    def __init__(
        self,
        collection,
        skip: int = 0,
        limit: int = 0,
        batch_size: int = 0,
        filter: dict | None = None,
    ):
        """
        Initializes a Cursor instance.

        Args:
            collection: The collection to query.
            skip (int): Number of documents to skip. Defaults to 0.
            limit (int): Maximum number of documents to retrieve. Defaults to 0 (no limit).
            batch_size (int): Number of documents to retrieve per batch (currently unused). Defaults to 0.
            filter (dict | None): Query filter to apply. Defaults to None.
        """

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
        """
        Returns the cursor instance for asynchronous iteration.

        Returns:
            Cursor: The current cursor instance.
        """
        return self

    def _create_command(self):
        """
        Creates the MongoDB command for fetching query results.

        Returns:
            dict: The command to execute.
        """

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
        """
        Fetches the next batch of documents from the server.
        """

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
        """
        Asynchronous iterator method to fetch the next document.

        Returns:
            dict: The next document in the result set.

        Raises:
            StopAsyncIteration: If no more documents are available.
        """

        if len(self._data):
            return self._data.popleft()

        is_refreshed = await self._refresh()

        if not is_refreshed:
            raise StopAsyncIteration

        return self._data.popleft()

    def _check_okay_to_chain(self):
        """
        Checks if chaining methods like `skip` or `limit` is allowed.

        Raises:
            Exception: If the cursor has already been executed.
        """
        if self._id is not None:
            return Exception("Cannot set options after executing query")

    def skip(self, skip: int) -> "Cursor":
        """
        Sets the number of documents to skip.

        Args:
            skip (int): Number of documents to skip.

        Returns:
            Cursor: The current cursor instance.

        Raises:
            TypeError: If `skip` is not an integer.
            ValueError: If `skip` is negative.
        """

        if not isinstance(skip, int):
            raise TypeError("Skip must be an integer")
        if skip < 0:
            raise ValueError("Skip must be >= 0")

        self._check_okay_to_chain()

        self._skip = skip
        return self

    def limit(self, limit) -> "Cursor":
        """
        Sets the maximum number of documents to retrieve.

        Args:
            limit (int): Maximum number of documents to retrieve.

        Returns:
            Cursor: The current cursor instance.

        Raises:
            TypeError: If `limit` is not an integer.
        """

        if not isinstance(limit, int):
            raise TypeError("limit must be an integer")

        self._check_okay_to_chain()

        self._limit = limit
        return self
