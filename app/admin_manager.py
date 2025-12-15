# Imports persistence helpers to load and save the users list from storage.
from storage_manager import load_users, save_users

# Imports the weak hashing function and the reserved admin username constant.
from auth_manager import weak_hash, ADMIN_USERNAME

def view_all_users():
    """
    Returns list of user dictionaries.
    Each user ideally has:
      - username
      - password        (hash)
      - plain_password  (plaintext; may be missing for old users)
      - role
    """
    users = load_users()
    if users is None:
        return []
    return users


def reset_user_password(username: str, new_password: str):
    """
    Change ANY user's password to a new plaintext password.
    Updates BOTH:
      - 'password'       (hash)
      - 'plain_password' (plaintext for admin panel)
    """
    users = load_users()
    if users is None:
        return False, "No users found."

    for u in users:
        if u.get("username") == username:
            if username == ADMIN_USERNAME:
                return False, "Admin password cannot be changed here."

            u["password"] = weak_hash(new_password)
            u["plain_password"] = new_password
            save_users(users)
            return True, f"Password for '{username}' has been updated."

    return False, "User not found."
