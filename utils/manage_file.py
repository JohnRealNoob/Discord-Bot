import os
import json
import aiofiles

__all__ = ["check_file_exists", "load_json", "write_json"]

def check_file_exists(dirname=None, filename=None, file_path=None):
    if file_path is None:
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", dirname, filename)
    else:
        path = file_path

    try:
        with open(path, "x"):
            return path
    except FileExistsError:
        return path

async def load_json(file_path):
    async with aiofiles.open(file_path, 'r') as f:
        return json.loads(await f.read())
    
async def write_json(file_path, data):
    async with aiofiles.open(file_path, 'w') as f:
        await f.write(json.dumps(data, indent=4))