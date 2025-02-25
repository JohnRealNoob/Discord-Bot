import sqlite3
from utils import check_file_exists
from setup_db import create_table
from typing import Literal, get_args
import os
__all__ = ["update","get"]

PATH = path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "bot.db")
check_file_exists(PATH)
_TYPES = Literal["join_channel_id", "leave_channel_id", "join_image", "leave_image"]

async def insert_guild_id(guild_id: int = None) -> None:
    if not guild_id:
        raise TypeError("Misisng argument") 
    
    conn = sqlite3.connect(PATH)
    cursor = conn.cursor()

    cursor.execute("INSERT OR IGNORE INTO channels (guild_id) VALUES ?", guild_id)

    conn.commit()
    conn.close()

async def check_table():
    conn = sqlite3.connect(PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT channels FROM sqlite_master WHERE type='table' AND name='users'")

    table_exists = cursor.fetchone() is not None

    if table_exists is None:
        await create_table()
        cursor.execute("SELECT channels FROM sqlite_master WHERE type='table' AND name='users'")
        table_exists = cursor.fetchone() is not None
    
    conn.close()

    return table_exists

async def update(guild_id: int = None, data = None, type_: _TYPES = None) -> None:
    if not guild_id or not data or not type_:
        raise TypeError("Misisng argument") 
    
    options = get_args(_TYPES)
    assert type_ in options, f"'{type_}' is not in options"
    
    conn = sqlite3.connect(PATH)
    cursor = conn.cursor()

    table_exisit = await check_table()

    try:
        await insert_guild_id(guild_id)
    except Exception as e:
        raise Exception from e
    
    if table_exisit:
        try:
            query = f"UPDATE channels SET {type_} = ? WHERE guild_id = ?"
            cursor.execute(query, data, guild_id)
        except Exception as e:
            raise Exception from e
    else:
        raise LookupError("SQL table doesn't exisits")
    
    conn.commit()
    conn.close()

async def get(guild_id: int = None, type_: _TYPES = None):
    if not guild_id or not type_:
        raise TypeError("Misisng argument") 
    
    options = get_args(_TYPES)
    assert type_ in options, f"'{type_}' is not in options"

    conn = sqlite3.connect(PATH)
    cursor = conn.cursor()

    table_exisit = await check_table()

    if table_exisit:
        try:
            query = f"SELECT {type_} FROM channels WHERE guild_id = ?"
            data = cursor.execute(query, guild_id)
        except Exception as e:
            raise Exception from e
    else:
        raise LookupError("SQL table doesn't exisits")
    
    channel_id = data.fetchone() is not None

    conn.commit()
    conn.close()

    return channel_id
