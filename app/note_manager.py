from storage_manager import load_notes, save_notes

# Load all notes for a user

def get_user_notes(username):
    """
    Returns a list of notes for this user.
    If user has no notes yet, returns an empty list.
    """
    notes = load_notes()
    return notes.get(username, [])


# Add a note for a user

def add_note(username, note_text):
    """
    Append a new note to the user's list of notes.
    """
    notes = load_notes()

    if username not in notes:
        notes[username] = []

    notes[username].append(note_text)
    save_notes(notes)

    return True, "Note added successfully."

def edit_note(username, index, new_text):
    """
    Edit an existing note for a user.
    Replace its content with new_text.
    """
    notes = load_notes()

    if username not in notes:
        return False, "User has no notes."

    user_notes = notes[username]

    if index < 0 or index >= len(user_notes):
        return False, "Invalid note index."

    old_content = user_notes[index]
    user_notes[index] = new_text

    notes[username] = user_notes
    save_notes(notes)

    return True, f"Updated note from: {old_content[:30]}..."


# Delete a note by index

def delete_note(username, index):
    """
    Delete a note given its index in the user's note list.
    """
    notes = load_notes()

    if username not in notes:
        return False, "User has no notes."

    user_notes = notes[username]

    if index < 0 or index >= len(user_notes):
        return False, "Invalid note index."

    removed = user_notes.pop(index)
    notes[username] = user_notes
    save_notes(notes)

    return True, f"Deleted note: {removed[:30]}..."


# Get all notes across all users (for Admin only)

def get_all_notes():
    """
    Returns the entire notes dictionary.
    Admin only.
    """
    notes = load_notes()
    return notes



