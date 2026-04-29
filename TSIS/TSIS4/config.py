import json
import os

SETTINGS_PATH = "C:/Users/Bull/Desktop/PP_2/Practice1/TSIS/TSIS4/settings.json"

def load_settings():
    if not os.path.exists(SETTINGS_PATH):
        default = {"snake_color": [0, 255, 0], "grid_overlay": True, "sound": True}
        save_settings(default)
        return default
    with open(SETTINGS_PATH, "r") as f:
        return json.load(f)

def save_settings(data):
    with open(SETTINGS_PATH, "w") as f:
        json.dump(data, f, indent=4)