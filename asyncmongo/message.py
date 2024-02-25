import ctypes

from pymongo.mongo_client import bson


"""
struct Section {
        uint8 payloadType;
        union payload {
            document  document; // payloadType == 0
            struct sequence { // payloadType == 1
                             int32      size;
                             cstring    identifier;
                             document*  documents;
                             };
            };
        };

struct OP_MSG {
        struct MsgHeader {
            int32  messageLength;
            int32  requestID;
            int32  responseTo;
            int32  opCode = 2013;
            };
        uint32      flagBits;
        Section+    sections;
        [uint32     checksum;]
        };"""

"""
sample header we should go for:
    b'\x10\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xdd\x07\x00\x00'
    (16, 0, 0, 2013)
"""


class OP_MSG(ctypes.Structure):
    _pack_ = 1  # This will pack the structure without extra padding
    _fields_ = [
        ("messageLength", ctypes.c_uint32),
        ("requestID", ctypes.c_uint32),
        ("responseTo", ctypes.c_uint32),
        ("opCode", ctypes.c_uint32),
        ("flagBits", ctypes.c_uint32),
        ("sectionType", ctypes.c_int8),
        # Ignoring checksums for now
        # ("checksum", ctypes.c_uint32),
    ]

    @staticmethod
    def new(bson_doc: dict) -> bytes:
        bson_bytes = bson.encode(bson_doc)

        msg = OP_MSG()
        msg.opCode = 2013
        total_message_size = len(bytes(msg)) + len(bson_bytes)
        msg.messageLength = total_message_size

        return bytes(msg) + bson_bytes
