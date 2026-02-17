from __future__ import annotations

from typing import List, Optional
from app.db import get_conn
from app.models import Machine

VALID_STATUS = {"operational", "maintenance", "offline"}


def _validate_machine(name: str, line: str, status: str) -> None:
    if not name or not name.strip():
        raise ValueError("Machine name is required.")
    if not line or not line.strip():
        raise ValueError("Production line is required.")
    if status not in VALID_STATUS:
        raise ValueError(f"Status must be one of: {', '.join(sorted(VALID_STATUS))}")


def list_machines() -> List[Machine]:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT id, name, line, status FROM machines ORDER BY id DESC"
        ).fetchall()
        return [Machine(id=row["id"], name=row["name"], line=row["line"], status=row["status"]) for row in rows]


def create_machine(name: str, line: str, status: str) -> int:
    _validate_machine(name, line, status)
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO machines (name, line, status) VALUES (?, ?, ?)",
            (name.strip(), line.strip(), status),
        )
        conn.commit()
        return int(cur.lastrowid)


def update_machine(machine_id: int, name: str, line: str, status: str) -> None:
    _validate_machine(name, line, status)
    with get_conn() as conn:
        cur = conn.execute(
            "UPDATE machines SET name=?, line=?, status=? WHERE id=?",
            (name.strip(), line.strip(), status, machine_id),
        )
        if cur.rowcount == 0:
            raise ValueError("Machine not found.")
        conn.commit()


def delete_machine(machine_id: int) -> None:
    with get_conn() as conn:
        cur = conn.execute("DELETE FROM machines WHERE id=?", (machine_id,))
        if cur.rowcount == 0:
            raise ValueError("Machine not found.")
        conn.commit()


def get_machine(machine_id: int) -> Optional[Machine]:
    with get_conn() as conn:
        row = conn.execute(
            "SELECT id, name, line, status FROM machines WHERE id=?",
            (machine_id,),
        ).fetchone()
        if not row:
            return None
        return Machine(id=row["id"], name=row["name"], line=row["line"], status=row["status"])