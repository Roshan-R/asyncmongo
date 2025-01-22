from asyncmongo.collection import Collection
from asyncmongo.connection import AsyncMongoConnection


class Database:
    """
    Represents a MongoDB database, providing access to collections and database-level operations.
    """

    def __init__(self, client, name: str) -> None:
        """
        Initializes a Database instance.

        Args:
            client: The client instance managing the connection to the MongoDB server.
            name (str): The name of the database.
        """

        self._name = name
        self._client = client

    def __getattr__(self, name: str) -> Collection:
        """
        Dynamically accesses a collection by name.

        Args:
            name (str): The name of the collection to access.

        Returns:
            Collection: The collection instance for the specified name.
        """

        return Collection(self, name)

    @property
    def name(self):
        """
        The name of the database.

        Returns:
            str: The name of the database.
        """

        return self._name

    def _get_connection(self) -> AsyncMongoConnection:
        """
        Retrieves the connection instance associated with the database.

        Returns:
            AsyncMongoConnection: The connection instance.
        """

        return self._client.connection

    async def list_collection_names(self) -> list[str]:
        """
        Lists all collection names in the database.

        Returns:
            list[str]: A list of collection names.

        Raises:
            Any exception that occurs during the command execution.
        """

        conn = self._get_connection()
        _cmd = {"listCollections": 1, "cursor": {}}
        resp = await conn.command(self._name, _cmd)
        names = [item["name"] for item in resp["cursor"]["firstBatch"]]
        return names
