import sqlite3
from utils import check_file_exists

PATH = check_file_exists("data", "bot.db")

def create_table() -> None:
    connection = sqlite3.connect(PATH)
    cursor = connection.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS channels (
        guild_id INTEGER PRIMARY KEY,
        join_channel_id INTEGER DEFAULT NULL,
        leave_channel_id INTEGER DEFAULT NULL
    )''')
    
    connection.commit()
    connection.close()

def check_table(table_name: str):
    connection = sqlite3.connect(PATH)
    cursor = connection.cursor()

    cursor.execute("SELECT ? FROM sqlite_master WHERE type='table' AND name='users'", table_name)

    table_exists = cursor.fetchone() is not None

    return table_exists


def insert_channel(guild_id = None, join_channel = None, leave_channel = None) -> None:
    connection = sqlite3.connect(PATH)
    cursor = connection.cursor()

    table_exists = check_table("channels")

    if not guild_id:
        return False
    
    if table_exists:
        if not join_channel:
            cursor.execute("INSERT INTO channels (guild_id, join_channel_id) VALUES (?, ?)",  guild_id, join_channel)
        elif not leave_channel:
            cursor.execute("INSERT INTO channels (guild_id, leave_channel_id) VALUES (?, ?)", guild_id, leave_channel)
        else:
            return False
    else:
        return False

    connection.commit() 
    connection.close()

def update_channel(guild_id = None, join = None):
    if not guild_id or not type:
        return False
    
    connection = sqlite3.connect(PATH)
    cursor = connection.cursor()
    if join:
        channel = cursor.execute("SELECT join_channel_id FROM channels WHERE guild_id = ?", guild_id)
    else:
        channel = cursor.execute("SELECT leave_channel_id FROM channels WHERE guild_id = ?", guild_id)
    
    channel_id = channel.fetchone()

    connection.commit()
    connection.close()

    return channel_id