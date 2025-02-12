import json
import os
from make import check_dir_file
class ChannelJson:
    name = "channel.json"
    dir_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "data")
    filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "data", name)

    @classmethod
    def load(cls, key_type: str):
        check_dir_file(cls.name)
        # Load JSON data safely
        try:
            with open(cls.filename, "r") as file:
                data = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            return None
        
        try:
            info = data[key_type]
        except Exception:
            return None
        
        return info
    
    @classmethod
    def write(cls, key_type: str, info: int):
        check_dir_file(cls.name)
        # Load JSON data safely
        try:
            with open(cls.filename, "r") as file:
                data = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            data = {}  # Initialize if file doesn't exist or is empty

        data[key_type] = info

        # Write back to JSON file
        with open(cls.filename, "w") as file:
            json.dump(data, file, indent=4)
