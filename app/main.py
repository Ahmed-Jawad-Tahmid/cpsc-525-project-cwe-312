import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

from auth_manager import login_user, register_user
from note_manager import get_user_notes, add_note, edit_note, delete_note
from admin_manager import view_all_users, reset_user_password


# Main Application Window

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Notes")
        self.geometry("600x400")
        self.resizable(False, False)

        self.active_user = None
        self.active_role = None

        self.container = ttk.Frame(self)
        self.container.pack(fill="both", expand=True)

        self.frames = {}

        for F in (LoginFrame, RegisterFrame, UserDashboardFrame, AdminDashboardFrame):
            frame = F(self.container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(LoginFrame)

    def show_frame(self, page):
        frame = self.frames[page]
        frame.tkraise()

    def login_success(self, username, role):
        self.active_user = username
        self.active_role = role

        if role == "admin":
            self.frames[AdminDashboardFrame].refresh()
            self.show_frame(AdminDashboardFrame)
        else:
            self.frames[UserDashboardFrame].refresh()
            self.show_frame(UserDashboardFrame)


# Login Frame

class LoginFrame(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)

        self.controller = controller

        ttk.Label(self, text="Login", font=("Arial", 18)).pack(pady=15)

        self.username_entry = ttk.Entry(self, width=30)
        self.username_entry.pack(pady=5)
        self.username_entry.insert(0, "Username")

        self.password_entry = ttk.Entry(self, width=30, show="*")
        self.password_entry.pack(pady=5)
        self.password_entry.insert(0, "Password")

        ttk.Button(self, text="Login", command=self.login).pack(pady=10)
        ttk.Button(self, text="Create new account", command=lambda: controller.show_frame(RegisterFrame)).pack()

    def login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        success, role = login_user(username, password)

        if success:
            self.controller.login_success(username, role)
        else:
            messagebox.showerror("Error", "Invalid username or password.")


# Register Frame

class RegisterFrame(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)

        self.controller = controller

        ttk.Label(self, text="Register", font=("Arial", 18)).pack(pady=15)

        self.username_entry = ttk.Entry(self, width=30)
        self.username_entry.pack(pady=5)
        self.username_entry.insert(0, "Choose Username")

        self.password_entry = ttk.Entry(self, width=30, show="*")
        self.password_entry.pack(pady=5)
        self.password_entry.insert(0, "Choose Password")

        ttk.Button(self, text="Register", command=self.register).pack(pady=10)
        ttk.Button(self, text="Already have an account?", command=lambda: controller.show_frame(LoginFrame)).pack()

    def register(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        success, msg = register_user(username, password)

        if success:
            messagebox.showinfo("Success", msg)
            self.controller.show_frame(LoginFrame)
        else:
            messagebox.showerror("Error", msg)


# User Dashboard Frame

class UserDashboardFrame(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        ttk.Label(self, text="Your Notes", font=("Arial", 18)).pack(pady=10)

        self.listbox = tk.Listbox(self, height=10, width=50)
        self.listbox.pack(pady=10)

        btn_frame = ttk.Frame(self)
        btn_frame.pack()

        ttk.Button(btn_frame, text="Add Note", command=self.add_note).grid(row=0, column=0, padx=5)
        ttk.Button(btn_frame, text="Edit Note", command=self.edit_note).grid(row=0, column=1, padx=5)
        ttk.Button(btn_frame, text="Delete Note", command=self.delete_note).grid(row=0, column=2, padx=5)
        ttk.Button(btn_frame, text="Logout", command=self.logout).grid(row=0, column=3, padx=5)

    def refresh(self):
        self.listbox.delete(0, tk.END)
        notes = get_user_notes(self.controller.active_user)
        for n in notes:
            self.listbox.insert(tk.END, n)

    def add_note(self):
        new_note = simpledialog.askstring("New Note", "Enter your note:")
        if new_note:
            add_note(self.controller.active_user, new_note)
            self.refresh()

    def edit_note(self):
        sel = self.listbox.curselection()
        if not sel:
            messagebox.showerror("Error", "Select a note to edit.")
            return

        old_text = self.listbox.get(sel[0])

        new_text = simpledialog.askstring("Edit Note", "Update note:", initialvalue=old_text)
        if new_text:
            edit_note(self.controller.active_user, sel[0], new_text)
            self.refresh()

    def delete_note(self):
        sel = self.listbox.curselection()
        if not sel:
            messagebox.showerror("Error", "Select a note to delete.")
            return

        confirm = messagebox.askyesno("Confirm", "Delete selected note?")
        if confirm:
            delete_note(self.controller.active_user, sel[0])
            self.refresh()

    def logout(self):
        self.controller.active_user = None
        self.controller.show_frame(LoginFrame)


# Admin Dashboard Frame

class AdminDashboardFrame(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        ttk.Label(self, text="Admin Dashboard", font=("Arial", 18)).pack(pady=10)

        self.tree = ttk.Treeview(self, columns=("hash"), show="headings")
        self.tree.heading("hash", text="Password Hash")
        self.tree.column("hash", width=400)
        self.tree.pack(pady=10)

        btn_frame = ttk.Frame(self)
        btn_frame.pack()

        ttk.Button(btn_frame, text="Reset User Password", command=self.reset_pw).grid(row=0, column=0, padx=5)
        ttk.Button(btn_frame, text="Logout", command=self.logout).grid(row=0, column=1, padx=5)

    def refresh(self):
        self.tree.delete(*self.tree.get_children())
        users = view_all_users()
        for u in users:
            self.tree.insert("", tk.END, values=(f"{u['username']} : {u['password_hash']}"))

    def reset_pw(self):
        username = simpledialog.askstring("Reset Password", "Enter username:")
        if not username:
            return

        new_pass = simpledialog.askstring("New Password", f"Enter new password for {username}:")
        if not new_pass:
            return

        success, msg = reset_user_password(username, new_pass)
        if success:
            messagebox.showinfo("Success", msg)
            self.refresh()
        else:
            messagebox.showerror("Error", msg)

    def logout(self):
        self.controller.active_user = None
        self.controller.show_frame(LoginFrame)


# Run the app
if __name__ == "__main__":
    app = App()
    app.mainloop()
