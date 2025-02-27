import json
import aiofiles
import os

__all__ = ["check_file_exists", "load_json", "write_json"]

def check_file_exists(file_path: str=None, dir_path: str=None):
    if dir_path:
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
    try:
        with open(file_path, "x"):
            return
    except FileExistsError:
        return
async def load_json(file_path):
    async with aiofiles.open(file_path, 'r') as f:
        return json.loads(await f.read())
    
async def write_json(file_path, data):
    async with aiofiles.open(file_path, 'w') as f:
        await f.write(json.dumps(data, indent=4))