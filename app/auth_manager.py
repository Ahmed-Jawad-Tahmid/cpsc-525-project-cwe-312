import hashlib
from storage_manager import load_users, save_users

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"


def weak_hash(password: str) -> str:
    """
    Hash the password using SHA-256 WITHOUT salt.
    This is intentionally weak for the assignment.
    """
    return hashlib.sha256(password.encode()).hexdigest()


def load_user_list():
    """Helper to always get a list of user dicts."""
    users = load_users()
    # If storage_manager returns None or something weird, normalize
    if users is None:
        return []
    return users


def get_user(username: str):
    """Return the user dict for a given username, or None."""
    users = load_user_list()
    for u in users:
        if u.get("username") == username:
            return u
    return None


def user_exists(username: str) -> bool:
    return get_user(username) is not None


def register_user(username: str, password: str):
    """
    Create a new user.
    Stores BOTH:
      - 'password'      -> SHA-256 hash (used for login)
      - 'plain_password' -> plaintext (CWE-312 violation on purpose)
    """
    if not username or not password:
        return False, "Username and password cannot be empty."

    if user_exists(username):
        return False, "Username already exists."

    users = load_user_list()

    user = {
        "username": username,
        "password": weak_hash(password),   # hash for login
        "plain_password": password,        # plaintext for admin panel
        "role": "user"
    }

    users.append(user)
    save_users(users)
    return True, "User registered successfully."


def login_user(username: str, password: str):
    """
    Login logic for both admin and normal users.
    """
    # Hard-coded admin credentials (also bad, but part of the assignment)
    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        return True, "admin"

    user = get_user(username)
    if not user:
        return False, None

    hashed_input = weak_hash(password)

    if user.get("password") == hashed_input:
        return True, "user"

    return False, None
