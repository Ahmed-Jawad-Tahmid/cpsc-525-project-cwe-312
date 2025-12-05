# storage_manager.py
import os
import pickle

# Paths to storage files
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STORAGE_DIR = os.path.join(BASE_DIR, "storage")

USERS_FILE = os.path.join(STORAGE_DIR, "users.pkl")
NOTES_FILE = os.path.join(STORAGE_DIR, "notes.pkl")

def initialize_storage():
    """Ensure storage directory and pickle files exist."""
    if not os.path.exists(STORAGE_DIR):
        os.makedirs(STORAGE_DIR)

    # Initialize users.pkl
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, "wb") as f:
            pickle.dump([], f)

    # Initialize notes.pkl
    if not os.path.exists(NOTES_FILE):
        with open(NOTES_FILE, "wb") as f:
            pickle.dump({}, f)

# USERS
def load_users():
    """Return list of dicts: [{username, password}, ...]."""
    try:
        with open(USERS_FILE, "rb") as f:
            return pickle.load(f)
    except Exception:
        return []

def save_users(users_list):
    """Save the full list of user dictionaries."""
    with open(USERS_FILE, "wb") as f:
        pickle.dump(users_list, f)

# NOTES
def load_notes():
    """Return dict of username -> list_of_notes."""
    try:
        with open(NOTES_FILE, "rb") as f:
            return pickle.load(f)
    except Exception:
        return {}

def save_notes(notes_dict):
    """Save the full notes dictionary."""
    with open(NOTES_FILE, "wb") as f:
        pickle.dump(notes_dict, f)

# Run initialization on import
initialize_storage()
