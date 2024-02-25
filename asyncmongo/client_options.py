from dataclasses import dataclass


@dataclass
class ClientOptions:
    username: str | None
    password: str | None
    database: str | None
    options: dict | None
