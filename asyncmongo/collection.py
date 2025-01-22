from asyncmongo.cursor import Cursor


class Collection:
    """
    Represents a MongoDB collection, providing methods to perform CRUD operations.
    """

    def __init__(self, database, name: str):
        """
        Initializes a Collection instance.

        Args:
            database: The database instance containing this collection.
            name (str): Name of the collection.
        """
        self._name = name
        self._database = database

    async def insert_one(self, doc) -> dict:
        """
        Inserts a single document into the collection.

        Args:
            doc (dict): The document to insert.

        Returns:
            dict: The result of the insert operation.
        """
        cmd = {"insert": self._name, "ordered": True, "documents": [doc]}
        conn = self._database._get_connection()
        return await conn.command(command=cmd, database_name=self._database.name)

    def find(self, filter: dict | None = None, skip: int = 0, limit: int = 0) -> Cursor:
        """
        Queries the collection for documents matching a filter.

        Args:
            filter (dict | None): The filter criteria. Defaults to None (no filtering).
            skip (int): Number of documents to skip. Defaults to 0.
            limit (int): Maximum number of documents to return. Defaults to 0 (no limit).

        Returns:
            Cursor: A cursor to iterate over the results.
        """
        return Cursor(self, filter=filter, skip=skip, limit=limit)

    async def find_one(self, filter: dict | None = None, skip: int = 0) -> dict | None:
        """
        Queries the collection for a single document matching a filter.

        Args:
            filter (dict | None): The filter criteria. Defaults to None (no filtering).
            skip (int): Number of documents to skip. Defaults to 0.

        Returns:
            dict | None: The first document matching the filter, or None if no match is found.
        """
        if filter is not None and not isinstance(filter, dict):
            filter = {"_id": filter}

        res = self.find(filter, skip, limit=1)

        async for each in res:
            return each

        return None

    async def drop_collection(self):
        """
        Drops the collection from the database.

        Returns:
            None
        """
        conn = self._database._get_connection()
        cmd = {"drop": self._name}
        await conn.command(command=cmd, database_name=self._database.name)

    async def update_one(self, filter: dict, doc: dict):
        """
        Updates a single document in the collection.

        Args:
            filter (dict): The filter criteria to find the document to update.
            doc (dict): The updated document. `_id` will be removed if present.

        Returns:
            None
        """
        doc.pop("_id", None)
        conn = self._database._get_connection()
        cmd = {"update": self._name, "updates": [{"q": filter, "u": doc}]}
        await conn.command(command=cmd, database_name=self._database.name)
