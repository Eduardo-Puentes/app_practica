from dataclasses import dataclass


@dataclass
class Machine:
    id: int | None
    name: str
    line: str
    status: str  # 'operational' | 'maintenance' | 'offline'