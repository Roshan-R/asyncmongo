from connection import AsyncMongoConnection

from database import Database


class AsyncMongoClient:
    connection: AsyncMongoConnection

    @classmethod
    async def create(
        cls, host: str | None = "localhost", port: int | None = 27017
    ) -> "AsyncMongoClient":
        # initialise the stuff here
        self = cls()
        self.connection = await AsyncMongoConnection.create(host, port)
        return self

    def __getattr__(self, name: str) -> Database:
        return Database(client=self, name=name)
