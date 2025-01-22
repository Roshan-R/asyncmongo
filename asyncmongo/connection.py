import asyncio
import ctypes
from asyncio.streams import StreamReader, StreamWriter

import bson

from asyncmongo.auth import MongoCredential, try_authenticate
from asyncmongo.message import OP_MSG
from .client_options import ClientOptions


class AsyncMongoConnection:
    """
    Manages an asynchronous connection to a MongoDB server,
    enabling communication and authentication for database operations.
    """

    def __init__(self):
        """
        Initializes an AsyncMongoConnection instance with uninitialized reader, writer, and options.
        """
        self.reader: StreamReader | None = None
        self.writer: StreamWriter | None = None
        self.options: ClientOptions | None = None

    @classmethod
    async def create(
        cls,
        host: str | None = "localhost",
        port: int | None = 27017,
        options: ClientOptions | None = None,
    ) -> "AsyncMongoConnection":
        """
        Establishes an asynchronous connection to a MongoDB server.

        Args:
            host (str | None): Hostname or IP address of the MongoDB server. Defaults to "localhost".
            port (int | None): Port number of the MongoDB server. Defaults to 27017.
            options (ClientOptions | None): Optional client options for authentication.

        Returns:
            AsyncMongoConnection: An instance of the connection.

        """
        self = cls()
        self.options = options
        self.reader, self.writer = await asyncio.open_connection(host, port)
        if options and options.username and options.password:
            await self._authenticate()

        print(f"Connected to MongoDB at {host} port {port}")
        return self

    async def _authenticate(self):
        """
        Authenticates the connection using the provided credentials.

        Raises:
            Exception: If authentication fails.
        """
        creds = MongoCredential(
            mechanism="SCRAM-SHA-256",
            source=self.options.database,
            username=self.options.username,
            password=self.options.password,
            mechanism_properties="",
            cache="",
        )
        await try_authenticate(self, credentials=creds)

    async def send(self, payload: bytes) -> list | None:
        """
        Sends a payload to the MongoDB server and reads the response.

        Args:
            payload (bytes): The serialized payload to send.

        Returns:
            list | None: The parsed response documents, or None if no data is received.
        """
        self.writer.write(payload)
        await self.writer.drain()
        return await self.read()

    async def read(self) -> list | None:
        """
        Reads a response from the MongoDB server.

        Returns:
            list | None: A list of BSON documents parsed from the server response, or None if no data is received.
        """
        op_msg_size = ctypes.sizeof(OP_MSG)
        header_data = await self.reader.read(op_msg_size)
        if not header_data:
            print("No data received for header")
            return None

        op_msg = OP_MSG.from_buffer_copy(header_data)

        # Calculate the size of the documents field
        documents_size = op_msg.messageLength - op_msg_size
        if documents_size <= 0:
            print("No documents present or invalid message length")
            return None

        # Read the documents data
        documents_data = await self.reader.read(documents_size)
        if not documents_data:
            print("No data received for documents")
            return None

        # Parse the BSON documents
        documents = bson.loads(documents_data)

        if not documents:
            return None

        return documents

    async def command(self, database_name: str, command: dict) -> list | None:
        """
        Sends a command to the MongoDB server.

        Args:
            database_name (str): The name of the database for the command.
            command (dict): The command to execute.

        Returns:
            list | None: The response from the server, parsed as a list of BSON documents.
        """
        command.update({"$db": database_name})
        payload = OP_MSG.new(command)
        return await self.send(payload)
