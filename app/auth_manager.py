import hashlib
from storage_manager import load_users, save_users

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"    

# Hashing 

def weak_hash(password: str) -> str:
    """
    Hash the password using SHA-256 WITHOUT salt.
    """
    return hashlib.sha256(password.encode()).hexdigest()

# Helper functions

def user_exists(username):
    users = load_users()
    return any(u["username"] == username for u in users)

def get_user(username):
    users = load_users()
    for u in users:
        if u["username"] == username:
            return u
    return None

# Registration

def register_user(username, password):
    if username == ADMIN_USERNAME:
        return False, "Username reserved for admin."

    if user_exists(username):
        return False, "User already exists."

    hashed = weak_hash(password)    # store weak hash
    users = load_users()
    users.append({"username": username, "password": hashed})
    save_users(users)

    return True, "Registration successful."

# Login

def login_user(username, password):
    # Admin: compare plaintext (intentionally inconsistent)
    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        return True, "admin"

    user = get_user(username)
    if not user:
        return False, None

    hashed_input = weak_hash(password)

    if user["password"] == hashed_input:
        return True, "user"

    return False, None