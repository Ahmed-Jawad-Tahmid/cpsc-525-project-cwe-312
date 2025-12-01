# app/admin_manager.py

from storage_manager import load_users, save_users
from auth_manager import weak_hash, ADMIN_USERNAME


# View all users (username + weak hashed password)

def view_all_users():
    """
    Returns list of user dictionaries:
    [{"username": "...", "password": "<weak_hash>"}]
    Admin only.
    """
    users = load_users()
    return users


# Admin resets/changes another user's password

def reset_user_password(username, new_password):
    """
    Admin-only action:
    Change ANY user's password to a new plaintext password.
    Stored with weak SHA-256 hashing (still vulnerable).
    """
    if username == ADMIN_USERNAME:
        return False, "Admin password cannot be changed here."

    users = load_users()
    for u in users:
        if u["username"] == username:
            u["password"] = weak_hash(new_password)
            save_users(users)
            return True, f"Password for '{username}' has been updated."

    return False, "User not found."
