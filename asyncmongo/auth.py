from .utils.saslprep import saslprep
import hashlib
import hmac
import os
import typing
from base64 import standard_b64encode, standard_b64decode
from collections import namedtuple

from asyncmongo.exceptions import AuthenticationFailedError

from .utils import _xor


MongoCredential = namedtuple(
    "MongoCredential",
    ["mechanism", "source", "username", "password", "mechanism_properties", "cache"],
)
"""A hashable namedtuple of values used for authentication."""


async def try_authenticate(connection, credentials: MongoCredential):
    username = credentials.username
    user = username.encode("utf-8").replace(b"=", b"=3D").replace(b",", b"=2C")
    nonce = standard_b64encode(os.urandom(32))
    first_bare = b"n=" + user + b",r=" + nonce

    payload = b"n,," + bytes(first_bare)

    cmd = {
        "saslStart": 1,
        "mechanism": credentials.mechanism,
        "payload": payload,
        "autoAuthorize": 1,
        "options": {"skipEmptyExchange": True},
    }

    try:
        resp = await connection.command(command=cmd, database_name=credentials.source)
    except Exception as e:
        raise AuthenticationFailedError(e)

    print(resp)
    server_first = resp["payload"]

    # make as a new function parse
    parsed = dict(
        typing.cast(typing.Tuple[bytes, bytes], item.split(b"=", 1))
        for item in resp.get("payload").split(b",")
    )

    iterations = int(parsed[b"i"])
    if iterations < 4096:
        raise Exception("Server returned an invalid iteration count.")

    salt = parsed[b"s"]
    rnonce = parsed[b"r"]
    without_proof = b"c=biws,r=" + rnonce
    client_key, csalt, citerations = None, None, None
    data = saslprep(credentials.password).encode("utf-8")

    _hmac = hmac.HMAC
    digestmod = hashlib.sha256

    # Salt and / or iterations could change for a number of different
    # reasons. Either changing invalidates the cache.
    if not client_key or salt != csalt or iterations != citerations:
        salted_pass = hashlib.pbkdf2_hmac(
            "sha256", data, standard_b64decode(salt), iterations
        )
        client_key = _hmac(salted_pass, b"Client Key", digestmod).digest()
        # server_key = _hmac(salted_pass, b"Server Key", digestmod).digest()
        # cache.data = (client_key, server_key, salt, iterations)
    stored_key = digestmod(client_key).digest()
    auth_msg = b",".join((first_bare, server_first, without_proof))
    client_sig = _hmac(stored_key, auth_msg, digestmod).digest()
    client_proof = b"p=" + standard_b64encode(_xor(client_key, client_sig))
    client_final = b",".join((without_proof, client_proof))
    # server_sig = standard_b64encode(_hmac(server_key, auth_msg, digestmod).digest())
    cmd = {
        "saslContinue": 1,
        "conversationId": resp["conversationId"],
        "payload": client_final,
    }
    resp = await connection.command(command=cmd, database_name="admin")

    if not resp.get("done"):
        raise Exception("Could not authenticate with server")
