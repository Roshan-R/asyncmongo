from asyncmongo.connection import AsyncMongoConnection
from asyncmongo.database import Database
from asyncmongo.uri_parser import parse_uri

from .client_options import ClientOptions


class AsyncMongoClient:
    """
    Represents an asynchronous MongoDB client, providing connection management and database access.
    """

    connection: AsyncMongoConnection

    @classmethod
    async def create(
        cls, host: str | None = "localhost", port: int | None = 27017
    ) -> "AsyncMongoClient":
        """
        Creates an instance of AsyncMongoClient, initializing the connection to MongoDB.

        Args:
            host (str | None): The hostname or URI of the MongoDB server. Defaults to "localhost".
                              If a URI is provided, it will be parsed to extract connection details.
            port (int | None): The port number for the MongoDB server. Defaults to 27017.
                              Ignored if `host` is a URI.

        Returns:
            AsyncMongoClient: An instance of the MongoDB client.

        """
        self = cls()

        # Case where host is a URI
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
        """
        Accesses a database instance using attribute-style access.

        Args:
            name (str): The name of the database to access.

        Returns:
            Database: A Database instance representing the specified database.
        """
        return Database(client=self, name=name)
