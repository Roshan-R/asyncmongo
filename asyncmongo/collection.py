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

    async def find_one(self, filter: dict | None = None, skip: int = 0) -> dict | None:
        if filter is not None and not isinstance(filter, dict):
            filter = {"_id": filter}

        res = self.find(filter, skip, limit=1)

        async for each in res:
            return each

        return None

    async def drop_collection(self):
        conn = self._database._get_connection()
        cmd = {"drop": self._name}
        await conn.command(command=cmd, database_name=self._database.name)

    async def update_one(self, filter: dict, doc: dict):
        doc.pop("_id", None)
        conn = self._database._get_connection()
        cmd = {"update": self._name, "updates": [{"q": filter, "u": doc}]}
        await conn.command(command=cmd, database_name=self._database.name)
