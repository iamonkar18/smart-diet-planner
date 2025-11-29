import os
import pandas as pd
from utils import DATA_DIR, ensure_data_dir, load_csv, save_csv, today_str

def weight_file(username: str) -> str:
    return os.path.join(DATA_DIR, f"weight_{username}.csv")


def calories_file(username: str) -> str:
    return os.path.join(DATA_DIR, f"calories_{username}.csv")


def notes_file(username: str) -> str:
    return os.path.join(DATA_DIR, f"notes_{username}.csv")


def save_weight(username: str, weight: float):
    path = weight_file(username)
    df = load_csv(path, default_columns=["date","weight"])
    df = pd.concat([df, pd.DataFrame([{"date": today_str(), "weight": weight}])], ignore_index=True)
    save_csv(df, path)


def load_weight(username: str) -> pd.DataFrame:
    path = weight_file(username)
    return load_csv(path, default_columns=["date","weight"])


def save_calories(username: str, target: float, actual: float):
    path = calories_file(username)
    df = load_csv(path, default_columns=["date","target_cal","actual_cal"])
    df = pd.concat(
        [df, pd.DataFrame([{"date": today_str(), "target_cal": target, "actual_cal": actual}])],
        ignore_index=True
    )
    save_csv(df, path)


def load_calories(username: str) -> pd.DataFrame:
    path = calories_file(username)
    return load_csv(path, default_columns=["date","target_cal","actual_cal"])


def save_note(username: str, note: str):
    if not note.strip():
        return
    path = notes_file(username)
    df = load_csv(path, default_columns=["date","note"])
    df = pd.concat(
        [df, pd.DataFrame([{"date": today_str(), "note": note.strip()}])],
        ignore_index=True
    )
    save_csv(df, path)


def load_notes(username: str) -> pd.DataFrame:
    path = notes_file(username)
    return load_csv(path, default_columns=["date","note"])

