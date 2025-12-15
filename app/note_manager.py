from storage_manager import load_notes, save_notes

# Returns the list of notes for a given username
def get_user_notes(username):
    notes = load_notes()
    return notes.get(username, [])

# Adds a new note (title + content) to a user's note list and persists it
def add_note(username, title, content):
    notes = load_notes()

    if username not in notes:
        notes[username] = []

    notes[username].append({
        "title": title,
        "content": content
    })

    save_notes(notes)
    return True, "Note added."

# Updates an existing note by index for a given user and persists the change.
def edit_note(username, index, new_title, new_content):
    notes = load_notes()

    if username not in notes:
        return False, "User has no notes."

    user_notes = notes[username]

    if index < 0 or index >= len(user_notes):
        return False, "Invalid note index."

    user_notes[index] = {
        "title": new_title,
        "content": new_content
    }

    save_notes(notes)
    return True, "Note updated."

# Deletes an existing note
def delete_note(username, index):
    notes = load_notes()

    if username not in notes:
        return False, "User has no notes."

    user_notes = notes[username]

    if index < 0 or index >= len(user_notes):
        return False, "Invalid note index."

    user_notes.pop(index)
    save_notes(notes)

    return True, "Note deleted."

# Returns the full notes dictionary for administrative viewing
def get_all_notes():
    """
    Returns the entire notes dictionary.
    Admin only.
    """
    return load_notes()
