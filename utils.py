import json

def read_or_create_file(file_path: str, default_content=None):
    if default_content is None:
        default_content = {}
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            content = json.load(file)
    except FileNotFoundError:
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(default_content, file, indent=4)
        content = default_content
    return content