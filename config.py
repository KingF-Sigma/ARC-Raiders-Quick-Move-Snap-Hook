import json
import os

DEFAULT_CONFIG = {
    "hotkey": "F6",
    "enabled": True,
    "delay_ms": 50,
    "safe_pocket_slot_1": {"x": 500, "y": 800},
    "quick_use_slot_1": {"x": 960, "y": 900}
}

CONFIG_FILE = "config.json"

def load_config():
    if not os.path.exists(CONFIG_FILE):
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return DEFAULT_CONFIG

def save_config(config_data):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config_data, f, indent=4)