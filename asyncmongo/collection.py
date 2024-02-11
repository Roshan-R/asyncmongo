from asyncmongo.cursor import Cursor


class Collection:
    def __init__(self, database, name: str):
        self._name = name
        self._database = database

    async def insert_one(self, doc) -> dict:
        cmd = {"insert": self._name, "ordered": True, "documents": [doc]}
        conn = self._database._get_connection()
        return await conn.command(command=cmd, database_name=self._database.name)

    def find(self, filter: dict | None = None, skip: int = 0, limit: int = 0) -> Cursor:
        return Cursor(self, filter=filter, skip=skip, limit=limit)
