from asyncmongo.connection import AsyncMongoConnection
from asyncmongo.database import Database
from asyncmongo.uri_parser import parse_uri

from .client_options import ClientOptions


class AsyncMongoClient:
    connection: AsyncMongoConnection

    @classmethod
    async def create(
        cls, host: str | None = "localhost", port: int | None = 27017
    ) -> "AsyncMongoClient":
        self = cls()

        # case where host is a uri
        if "://" in host:
            uri_dict = parse_uri(host)
            host, port = uri_dict.get("nodelist")
            options = ClientOptions(
                username=uri_dict.get("username"),
                password=uri_dict.get("password"),
                database=uri_dict.get("database"),
                options=uri_dict.get("options"),
            )
        else:
            options = ClientOptions()

        self.connection = await AsyncMongoConnection.create(host, port, options)
        return self

    def __getattr__(self, name: str) -> Database:
        return Database(client=self, name=name)
