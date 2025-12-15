import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

from admin_manager import view_all_users, reset_user_password
from note_manager import get_all_notes


class UsersPanel(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        ttk.Label(self, text="User Management", font=("Segoe UI", 14, "bold")).pack(pady=10)

        # Now show username, plaintext password, and hash
        columns = ("username", "plain", "hash")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=10)
        self.tree.heading("username", text="Username")
        self.tree.heading("plain", text="Plaintext Password")
        self.tree.heading("hash", text="Password Hash (weak)")

        self.tree.column("username", width=150, anchor="w")
        self.tree.column("plain", width=200, anchor="w")
        self.tree.column("hash", width=380, anchor="w")

        self.tree.pack(fill="both", expand=True, padx=10, pady=5)

        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=10)

        ttk.Button(btn_frame, text="Refresh Users", command=self.refresh).grid(row=0, column=0, padx=5)
        ttk.Button(btn_frame, text="Reset Selected User Password", command=self.reset_selected).grid(row=0, column=1, padx=5)

        self.refresh()

    def refresh(self):
        # Clear table
        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            users = view_all_users()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load users: {e}")
            return

        for u in users:
            username = u.get("username", "")
            plain = u.get("plain_password", "<not stored>")
            pw_hash = u.get("password", "")
            self.tree.insert("", "end", values=(username, plain, pw_hash))

    def get_selected_username(self):
        selected = self.tree.selection()
        if not selected:
            return None
        values = self.tree.item(selected[0], "values")
        if not values:
            return None
        return values[0]

    def reset_selected(self):
        username = self.get_selected_username()
        if not username:
            messagebox.showwarning("No selection", "Please select a user first.")
            return

        new_pass = simpledialog.askstring("Reset Password",
                                          f"Enter new password for '{username}':",
                                          show="*")
        if not new_pass:
            return

        success, msg = reset_user_password(username, new_pass)
        if success:
            messagebox.showinfo("Success", msg)
            self.refresh()
        else:
            messagebox.showerror("Error", msg)


class NotesPanel(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        main_frame = ttk.Frame(self)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Users list
        user_frame = ttk.Frame(main_frame)
        user_frame.grid(row=0, column=0, sticky="nswe", padx=(0, 10))

        ttk.Label(user_frame, text="Users", font=("Segoe UI", 12, "bold")).pack(anchor="w")
        self.user_list = tk.Listbox(user_frame, height=15)
        self.user_list.pack(fill="both", expand=True)

        # Notes list
        notes_frame = ttk.Frame(main_frame)
        notes_frame.grid(row=0, column=1, sticky="nswe", padx=(0, 10))

        ttk.Label(notes_frame, text="Notes", font=("Segoe UI", 12, "bold")).pack(anchor="w")
        self.notes_list = tk.Listbox(notes_frame, height=15)
        self.notes_list.pack(fill="both", expand=True)

        # Note content
        content_frame = ttk.Frame(main_frame)
        content_frame.grid(row=0, column=2, sticky="nswe")

        ttk.Label(content_frame, text="Note Content", font=("Segoe UI", 12, "bold")).pack(anchor="w")
        self.content_text = tk.Text(content_frame, wrap="word", height=15, width=40)
        self.content_text.pack(fill="both", expand=True)

        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.columnconfigure(2, weight=2)
        main_frame.rowconfigure(0, weight=1)

        ttk.Button(self, text="Refresh Notes", command=self.refresh).pack(pady=(0, 10))

        self.notes_dict = {}

        self.user_list.bind("<<ListboxSelect>>", self.on_user_select)
        self.notes_list.bind("<<ListboxSelect>>", self.on_note_select)

        self.refresh()

    def refresh(self):
        try:
            self.notes_dict = get_all_notes()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load notes: {e}")
            return

        self.user_list.delete(0, tk.END)
        for username in sorted(self.notes_dict.keys()):
            self.user_list.insert(tk.END, username)

        self.notes_list.delete(0, tk.END)
        self.content_text.delete("1.0", tk.END)

    def on_user_select(self, event=None):
        selection = self.user_list.curselection()
        if not selection:
            return

        idx = selection[0]
        username = self.user_list.get(idx)

        self.notes_list.delete(0, tk.END)
        self.content_text.delete("1.0", tk.END)

        notes = self.notes_dict.get(username, [])
        for i, note in enumerate(notes):
            title = note.get("title", f"Note {i}")
            self.notes_list.insert(tk.END, title)

    def on_note_select(self, event=None):
        user_sel = self.user_list.curselection()
        note_sel = self.notes_list.curselection()
        if not user_sel or not note_sel:
            return

        user_idx = user_sel[0]
        note_idx = note_sel[0]

        username = self.user_list.get(user_idx)
        notes = self.notes_dict.get(username, [])
        if note_idx < 0 or note_idx >= len(notes):
            return

        note = notes[note_idx]
        content = note.get("content", "")

        self.content_text.delete("1.0", tk.END)
        self.content_text.insert(tk.END, content)


class AdminApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Admin Panel - Notes App")
        self.geometry("950x520")
        self.resizable(False, False)

        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except Exception:
            pass

        container = ttk.Frame(self)
        container.pack(fill="both", expand=True)

        notebook = ttk.Notebook(container)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        self.users_panel = UsersPanel(notebook)
        self.notes_panel = NotesPanel(notebook)

        notebook.add(self.users_panel, text="Users")
        notebook.add(self.notes_panel, text="Notes")


if __name__ == "__main__":
    app = AdminApp()
    app.mainloop()
