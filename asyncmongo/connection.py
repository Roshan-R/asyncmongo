import asyncio
import ctypes
from asyncio.streams import StreamReader, StreamWriter

import bson

from asyncmongo.auth import MongoCredential, try_authenticate
from asyncmongo.message import OP_MSG
from .client_options import ClientOptions


class AsyncMongoConnection:
    def __init__(self):
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
        self = cls()
        self.options = options
        self.reader, self.writer = await asyncio.open_connection(host, port)
        if options.username and options.password:
            await self._authenticate()

        print(f"Connected to mongodb at {host} port {port}")
        return self

    async def _authenticate(self):
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
        self.writer.write(payload)
        await self.writer.drain()
        return await self.read()

    async def read(self) -> list | None:
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
        documents = bson.decode(documents_data)

        if not documents:
            return None

        return documents

    async def command(self, database_name: str, command: dict):
        command.update({"$db": database_name})
        payload = OP_MSG.new(command)
        return await self.send(payload)
