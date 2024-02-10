import asyncio
from asyncio.streams import StreamReader, StreamWriter

from mongo_types import OP_MSG
import json

import bson

import ctypes


class AsyncMongoConnection:
    reader: StreamReader
    writer: StreamWriter

    @classmethod
    async def create(
        cls, host: str | None = "localhost", port: int | None = 27017
    ) -> "AsyncMongoConnection":
        self = cls()
        self.reader, self.writer = await asyncio.open_connection(host, port)
        #print("Connected to mongodb at 127.0.0.1 port 27017")
        return self

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
            return op_msg

        # Read the documents data
        documents_data = await self.reader.read(documents_size)
        if not documents_data:
            print("No data received for documents")
            return op_msg

        # Parse the BSON documents
        documents = bson.decode_all(documents_data)

        if not documents:
            return None

        return documents

