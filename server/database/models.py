import dataclasses


@dataclasses.dataclass
class AdminDB:
    id: int
    name: str
    key: str
