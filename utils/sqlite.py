import sqlite3
from utils import check_file_exists

__all__ = ["insert_channel", "get_channel"]

PATH = check_file_exists("data", "bot.db")

def check_table(table_name: str):
    connection = sqlite3.connect(PATH)
    cursor = connection.cursor()

    cursor.execute("SELECT ? FROM sqlite_master WHERE type='table' AND name='users'", table_name)

    table_exists = cursor.fetchone() is not None

    return table_exists


def insert_channel(guild_id = None, join = None ,channel = None) -> None:
    connection = sqlite3.connect(PATH)
    cursor = connection.cursor()

    table_exists = check_table("channels")

    if not guild_id:
        return False
    
    if table_exists:
        if join:
            cursor.execute("INSERT INTO channels (guild_id, join_channel_id) VALUES (?, ?)",  guild_id, channel)
        elif not join:
            cursor.execute("INSERT INTO channels (guild_id, leave_channel_id) VALUES (?, ?)", guild_id, channel)
        else:
            return False
    else:
        return False

    connection.commit() 
    connection.close()

def get_channel(guild_id = None, join = None):
    if not guild_id or not type:
        return False
    
    connection = sqlite3.connect(PATH)
    cursor = connection.cursor()
    if join:
        channel = cursor.execute("SELECT join_channel_id FROM channels WHERE guild_id = ?", guild_id)
    else:
        channel = cursor.execute("SELECT leave_channel_id FROM channels WHERE guild_id = ?", guild_id)
    
    channel_id = channel.fetchone() is not None

    connection.commit()
    connection.close()

    return channel_id