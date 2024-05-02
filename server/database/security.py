from __future__ import annotations
from typing import Optional
import dataclasses
import random
import string

from sqlalchemy import Engine, Select, func, select
from sqlalchemy.orm import Session

from database.connection import (  # type: ignore
    get_connection_source,
    AdminBase as _AdminBase
)


_loaded_admins: list[AdminDB] = []


def clear_loaded_admins() -> None:
    global _loaded_admins
    _loaded_admins.clear()


def get_loaded_admins() -> list[AdminDB]:
    return _loaded_admins.copy()


@dataclasses.dataclass
class AdminDB:
    id: int
    name: str
    key: str


def add_admin_key(name: str, connection_source: Optional[Engine] = None) -> str:
    if connection_source is None:
        connection_source = get_connection_source()
    """Add an admin to the database and return the key."""
    _create_admin_table_if_it_does_not_exist(connection_source)
    with Session(connection_source) as session:
        existing_admin = session.query(_AdminBase).filter(_AdminBase.name == name).first()
        if existing_admin is not None:
            return _admin_already_exists_msg(existing_admin.name)
        else:
            key = _generate_key()
            admin = _AdminBase(name=name, key=key)
            session.add(admin)
            session.commit()
            return _admin_added_msg(name, key)


def _admin_added_msg(name: str, key: str) -> str:
    return f"Admin '{name}' added with key:\n\n{key}\n\n"


def _admin_already_exists_msg(name: str) -> str:
    return f"Admin with name '{name}' already exists."


def _create_admin_table_if_it_does_not_exist(connection_source: Engine) -> None:
    with connection_source.connect() as connection:
        if not connection_source.dialect.has_table(connection, _AdminBase.__tablename__):
            _AdminBase.metadata.create_all(connection_source)


def get_admin(key: str) -> AdminDB | None:
    loaded_admins = get_loaded_admins()
    for admin in loaded_admins:
        if admin.key == key:
            return admin

    source = get_connection_source()
    if source is None:
        return None

    _create_admin_table_if_it_does_not_exist(source)

    with Session(get_connection_source()) as session:
        result = session.execute(select(_AdminBase).where(_AdminBase.key == key)).first()
        if result is None:
            return None
        else:
            admin_base: _AdminBase = result[0]
            admin = AdminDB(id=admin_base.id, name=admin_base.name, key=admin_base.key)
            _loaded_admins.append(admin)
            return admin


def admin_selection(key: str) -> Select:
    return select(_AdminBase).where(_AdminBase.key == key)


def number_of_admin_keys(connection: Optional[Engine] = None) -> int:
    if connection is None:
        connection = get_connection_source()
    with Session(connection) as session:
        try:
            return session.query(func.count(_AdminBase.__table__.c.id)).scalar()
        except:
            return 0


def _generate_key() -> str:  # pragma: no cover
    return "".join(random.choice(string.ascii_letters) for _ in range(30))
