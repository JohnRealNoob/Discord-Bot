import os
import json

__all__ = ["check_file_exists", "load_json", "write_json"]

def check_file_exists(dirname=None, filename=None, file_path=None):
    if file_path is None:
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", dirname, filename)
    else:
        path = file_path

    try:
        with open(path, "x") as file:
            return path
    except FileExistsError:
        return path
    
def load_json(file_path: str):
    check_file_exists(file_path=file_path)
    try:
        with open(file_path, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}
    
def write_json(file_path: str, data):
    check_file_exists(file_path=file_path)
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)
