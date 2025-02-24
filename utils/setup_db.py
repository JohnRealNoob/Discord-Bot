import sqlite3
from utils import check_file_exists


def create_table() -> None:

    path = check_file_exists("data", "bot.db")
    connection = sqlite3.connect(path)

    cursor = connection.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS channels (
        guild_id INTEGER PRIMARY KEY,
        join_channel_id INTEGER DEFAULT NULL,
        leave_channel_id INTEGER DEFAULT NULL
    )''')
    
    connection.commit()
    connection.close()

if __name__ == "__main__":
    create_table()