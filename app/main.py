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

        center = ttk.Frame(self)
        center.pack(expand=True)   # expands and centers vertically AND horizontally

        ttk.Label(center, text="Login", font=("Arial", 18)).pack(pady=15)

        self.username_entry = ttk.Entry(center, width=30)
        self.username_entry.pack(pady=5)
        self.username_entry.insert(0, "Username")

        self.password_entry = ttk.Entry(center, width=30)
        self.password_entry.pack(pady=5)
        self.password_entry.insert(0, "Password")

        ttk.Button(center, text="Login", width=20, command=self.login).pack(pady=5)
        ttk.Button(center, text="Create new account", width=20,
           command=lambda: controller.show_frame(RegisterFrame)).pack(pady=5)



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

        # Username entry
        self.username_entry = ttk.Entry(self, width=30)
        self.username_entry.pack(pady=5)
        self.username_entry.insert(0, "Choose Username")

        # Password entry
        self.password_entry = ttk.Entry(self, width=30)
        self.password_entry.pack(pady=5)
        self.password_entry.insert(0, "Choose Password")

        # Confirm password entry
        self.confirm_entry = ttk.Entry(self, width=30)
        self.confirm_entry.pack(pady=5)
        self.confirm_entry.insert(0, "Retype Password")

        ttk.Button(self, text="Register", command=self.register).pack(pady=10)
        ttk.Button(self, text="Back to Login", command=lambda: controller.show_frame(LoginFrame)).pack()

    def register(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        confirm = self.confirm_entry.get().strip()

        if password != confirm:
            messagebox.showerror("Error", "Passwords do not match!")
            return

        success, msg = register_user(username, password)

        if success:
            messagebox.showinfo("Success", msg)
            self.controller.show_frame(LoginFrame)
        else:
            messagebox.showerror("Error", msg)

class UserDashboardFrame(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        center = ttk.Frame(self)
        center.pack(expand=True)

        ttk.Label(center, text="Your Notes", font=("Arial", 18)).pack(pady=10)

        self.listbox = tk.Listbox(center, height=10, width=50)
        self.listbox.pack(pady=10)

        btn_frame = ttk.Frame(center)
        btn_frame.pack()

        ttk.Button(btn_frame, text="Add Note", command=self.add_note_popup).grid(row=0, column=0, padx=5)
        ttk.Button(btn_frame, text="Edit Note", command=self.edit_note_popup).grid(row=0, column=1, padx=5)
        ttk.Button(btn_frame, text="Delete Note", command=self.delete_note).grid(row=0, column=2, padx=5)
        ttk.Button(btn_frame, text="Logout", command=self.logout).grid(row=0, column=3, padx=5)

    def refresh(self):
        self.listbox.delete(0, tk.END)
        notes = get_user_notes(self.controller.active_user)
        for note in notes:
            self.listbox.insert(tk.END, note["title"])   
            
    def add_note_popup(self):
        win = tk.Toplevel(self)
        win.title("Add Note")
        win.geometry("400x300")

        ttk.Label(win, text="Title").pack()
        title_entry = ttk.Entry(win, width=40)
        title_entry.pack(pady=5)

        ttk.Label(win, text="Content").pack()
        content_text = tk.Text(win, width=45, height=15)
        content_text.pack()

        def save_note():
            title = title_entry.get().strip()
            content = content_text.get("1.0", tk.END).strip()

            if not title:
                messagebox.showerror("Error", "Title cannot be empty.")
                return

            add_note(self.controller.active_user, title, content)
            self.refresh()
            win.destroy()

        ttk.Button(win, text="Save", command=save_note).pack(pady=5)
    
    def edit_note_popup(self):
        sel = self.listbox.curselection()
        if not sel:
            messagebox.showerror("Error", "Select a note to edit.")
            return

        index = sel[0]
        notes = get_user_notes(self.controller.active_user)
        note = notes[index]

        win = tk.Toplevel(self)
        win.title("Edit Note")
        win.geometry("400x300")

        ttk.Label(win, text="Title").pack()
        title_entry = ttk.Entry(win, width=40)
        title_entry.insert(0, note["title"])
        title_entry.pack(pady=5)

        ttk.Label(win, text="Content").pack()
        content_text = tk.Text(win, width=45, height=15)
        content_text.insert("1.0", note["content"])
        content_text.pack()

        def save_edit():
            new_title = title_entry.get().strip()
            new_content = content_text.get("1.0", tk.END).strip()

            if not new_title:
                messagebox.showerror("Error", "Title cannot be empty.")
                return

            edit_note(self.controller.active_user, index, new_title, new_content)
            self.refresh()
            win.destroy()

        ttk.Button(win, text="Save Changes", command=save_edit).pack(pady=5)

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
