import os

def check_file_exists(dirname: str, filename: str):

    file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", filename)

    try:
        with open(file_path, "x") as file:
            return file_path
    except FileExistsError:
        return file_path