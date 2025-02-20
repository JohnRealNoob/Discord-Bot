import os
import json

__all__ = ["check_file_exists", "load_json"]

def check_file_exists(dirname=None, filename=None, path=None):
    if not path:
        file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", dirname, filename)
    else:
        file_path = path

    try:
        with open(file_path, "x") as file:
            return file_path
    except FileExistsError:
        return file_path
    
def load_json(file_path: str):
    check_file_exists(path=file_path)
    try:
        with open(file_path, "r") as file:
            data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return None

    return data