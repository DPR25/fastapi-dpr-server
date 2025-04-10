import json


def load_json(file_path):
    """
    Loads a JSON file and returns the data as a Python dictionary.

    :param file_path: The path to the JSON file.
    :return: The data in the JSON file as a dictionary.
    """
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        print(f"Error: The file at {file_path} was not found.")
        return None
    except json.JSONDecodeError:
        print(f"Error: The file at {file_path} is not a valid JSON file.")
        return None