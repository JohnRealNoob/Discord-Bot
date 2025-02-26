import sqlite3
from utils import check_file_exists
from .setup_db import create_table
from typing import Literal, get_args
import os

__all__ = ["update", "get"]

PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "data", "bot.db")
check_file_exists(PATH)
_TYPES = Literal["join_channel_id", "leave_channel_id", "join_image", "leave_image"]

async def insert_guild_id(guild_id: int = None) -> None:
    if not guild_id:
        raise TypeError("Missing argument") 
    
    conn = sqlite3.connect(PATH)
    cursor = conn.cursor()

    cursor.execute("INSERT OR IGNORE INTO channels (guild_id) VALUES (?)", (guild_id,))

    conn.commit()
    conn.close()

async def check_table() -> bool:
    conn = sqlite3.connect(PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='channels'")
    table_exists = cursor.fetchone() is not None

    if not table_exists:
        await create_table() 
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='channels'")
        table_exists = cursor.fetchone() is not None
    
    conn.close()
    return table_exists

async def update(guild_id: int = None, data=None, type_: _TYPES = None) -> None:
    if not guild_id or not data or not type_:
        raise TypeError("Missing argument") 
    
    options = get_args(_TYPES)
    assert type_ in options, f"'{type_}' is not in options"
    
    conn = sqlite3.connect(PATH)
    cursor = conn.cursor()

    table_exists = await check_table()

    try:
        await insert_guild_id(guild_id)
    except Exception as e:
        raise Exception(f"Failed to insert guild_id: {e}") from e
    
    if table_exists:
        try:
            query = f"UPDATE channels SET {type_} = ? WHERE guild_id = ?"
            cursor.execute(query, (data, guild_id))
        except Exception as e:
            raise Exception(f"Failed to update: {e}") from e
    else:
        raise LookupError("SQL table doesn't exist")
    
    conn.commit()
    conn.close()

async def get(guild_id: int = None, type_: _TYPES = None):
    if not guild_id or not type_:
        raise TypeError("Missing argument") 
    
    options = get_args(_TYPES)
    assert type_ in options, f"'{type_}' is not in options"

    conn = sqlite3.connect(PATH)
    cursor = conn.cursor()

    table_exists = await check_table()

    if table_exists:
        try:
            query = f"SELECT {type_} FROM channels WHERE guild_id = ?"
            cursor.execute(query, (guild_id,))
            result = cursor.fetchone()
            channel_id = result[0] if result else None
        except Exception as e:
            raise Exception(f"Failed to get: {e}") from e
    else:
        raise LookupError("SQL table doesn't exist")
    
    conn.close()

    return channel_id
