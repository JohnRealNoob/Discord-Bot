import sqlite3
from utils.manage_file import check_file_exists
import os
import asyncio

PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "data", "bot.db")

async def create_table() -> None:

    check_file_exists(PATH)
    connection = sqlite3.connect(PATH)

    cursor = connection.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS channels (
        guild_id INTEGER PRIMARY KEY,
        join_channel_id INTEGER DEFAULT NULL,
        leave_channel_id INTEGER DEFAULT NULL,
        join_image TEXT DEFAULT NULL,
        leave_image TEXT DEFAULT NULL 
    )''')
    
    connection.commit()
    connection.close()

async def main():
    await create_table()
if __name__ == "__main__":
    asyncio.run(main())