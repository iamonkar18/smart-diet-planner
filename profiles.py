import json
import os
from datetime import datetime
from utils import DATA_DIR, ensure_data_dir

USERS_FILE = os.path.join(DATA_DIR, "users.json")


def load_users():
    ensure_data_dir()
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, "r") as f:
        return json.load(f)


def save_users(users: dict):
    ensure_data_dir()
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)


def get_usernames():
    users = load_users()
    return list(users.keys())


def get_user(username: str):
    users = load_users()
    return users.get(username)


def create_user(username: str, name: str, age: int, gender: str, height_cm: float, veg_default: bool):
    users = load_users()
    if username in users:
        raise ValueError("Username already exists")
    users[username] = {
        "username": username,
        "name": name,
        "age": age,
        "gender": gender,
        "height_cm": height_cm,
        "veg_default": veg_default,
        "created_at": datetime.now().isoformat(),
    }
    save_users(users)
    return users[username]

