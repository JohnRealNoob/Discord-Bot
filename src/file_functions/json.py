import json
import os

class ChannelJson:
    
    filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "data", "channel.json")

    @classmethod
    def load(cls, channel_type: str):
        # Load JSON data safely
        try:
            with open(cls.filename, "r") as file:
                data = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            return False
        
        try:
            channel_id = data[channel_type]
        except Exception:
            return False
        
        return channel_id
    
    @classmethod
    def write(cls, channel_type: str, channel_id: int):
        # Load JSON data safely
        try:
            with open(cls.filename, "r") as file:
                data = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            data = {}  # Initialize if file doesn't exist or is empty

        data[channel_type] = channel_id

        # Write back to JSON file
        with open(cls.filename, "w") as file:
            json.dump(data, file, indent=4)
