import json
import os

class ChannelJson:
    
    filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "data", "channel.json")

    @classmethod
    def load(cls, key_type: str):
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
