import logging
import logging.handlers
import os
from utils.manage_file import check_file_exists

def setup_logging():
    # Set up logging
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "logs", "discord.log")
    dir_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "logs")
    
    check_file_exists(file_path=path, dir_path=dir_path)

    logger = logging.getLogger('discord')
    logger.setLevel(logging.DEBUG)
    logging.getLogger('discord.http').setLevel(logging.INFO)

    handler = logging.handlers.RotatingFileHandler(
        filename = path,
        encoding='utf-8',
        maxBytes=32 * 1024 * 1024,  # 32 MiB
        backupCount=5,  # Rotate through 5 files
    )
    dt_fmt = '%Y-%m-%d %H:%M:%S'
    formatter = logging.Formatter('[{asctime}] [{levelname:<8}] {name}: {message}', dt_fmt, style='{')
    handler.setFormatter(formatter)
    logger.addHandler(handler)