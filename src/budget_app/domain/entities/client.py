from dataclasses import dataclass


@dataclass(frozen=True)
class Client:
    client_id: str
    client_name: str
