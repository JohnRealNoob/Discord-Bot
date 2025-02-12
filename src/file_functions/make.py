import os

dir_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "data")

def check_dir_file(name: str):
    filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "data", name)
    """Creates a directory and a file inside it if they do not exist."""
    # Ensure the directory exists
    os.makedirs(dir_path, exist_ok=True)

    # Create the full file path
    file_path = os.path.join(dir_path, filename)

    # Create the file if it doesn't exist
    if not os.path.exists(file_path):
        with open(file_path, "w") as file:
            file.write(None)
        print(f"File created: {file_path}")
    else:
        print(f"File already exists: {file_path}")