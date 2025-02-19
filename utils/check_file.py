import os

def file_exists(filename: str):

    file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", filename)

    try:
        with open(file_path, "x") as file:
            return False
    except FileExistsError:
        return True