import hashlib

# Imports storage helpers to read/write the users list from persistent storage
from storage_manager import load_users, save_users

# Defines the reserved admin username used for privileged login.
ADMIN_USERNAME = "admin"

# Defines the hard-coded admin password (separate from stored users.pkl users).
ADMIN_PASSWORD = "admin123"

# Returns a weak SHA-256 hash of the password with no salt
def weak_hash(password: str) -> str:
    """
    Hash the password using SHA-256 WITHOUT salt.
    This is intentionally done to demonstrate CWE 312 for the project.
    """
    return hashlib.sha256(password.encode()).hexdigest()

# Loads users from storage and normalizes the result to a list of user dicts
def load_user_list():
    """Helper to always get a list of user dicts."""
    users = load_users()
    # If storage_manager returns None or something weird, normalize
    if users is None:
        return []
    return users

# Registers a new user and persists their record to users.pkl
def get_user(username: str):
    """Return the user dict for a given username, or None."""
    users = load_user_list()
    for u in users:
        if u.get("username") == username:
            return u
    return None

# Returns True if a user with this username exists in storage
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
    # Hard-coded admin credentials 
    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        return True, "admin"

    user = get_user(username)
    if not user:
        return False, None

    hashed_input = weak_hash(password)

    if user.get("password") == hashed_input:
        return True, "user"

    return False, None
