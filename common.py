import json
import pathlib


def load_settings(path: str = "settings.json"):
    settings_path = pathlib.Path(path).absolute()


    data: dict = {}
    if settings_path.exists() and settings_path.stat().st_size > 0:
        try:
            with open(settings_path, "r") as source:
                data = json.load(source)
        except:
            # It can happen that the write process fails 
            return {}

    return data

def write_settings(new_data: dict, path: str = "settings.json"):
    with open(path, "w") as source:
            json.dump(new_data, source)