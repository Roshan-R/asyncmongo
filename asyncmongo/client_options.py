from dataclasses import dataclass


@dataclass
class ClientOptions:
    username: str | None = None
    password: str | None = None
    database: str | None = None
    options: dict | None = None
