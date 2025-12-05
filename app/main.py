
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

from auth_manager import login_user, register_user
from note_manager import get_user_notes, add_note, edit_note, delete_note
from admin_manager import view_all_users, reset_user_password

class PlaceholderEntry(ttk.Entry):
    def __init__(self, master=None, placeholder="Placeholder", color="gray", show=None, **kwargs):
        self.placeholder = placeholder
        self.placeholder_color = color
        self.real_show = show

        # if a show character is specified, disable it initially to show placeholder
        kwargs["show"] = None

        super().__init__(master, **kwargs)

        # store normal fg color
        self.normal_color = self.cget("foreground") or "black"

        # state
        self.has_placeholder = False

        # events
        self.bind("<FocusIn>", self._on_focus_in)
        self.bind("<FocusOut>", self._on_focus_out)
        self.bind("<Key>", self._on_key)

        self._show_placeholder()

    # Display placeholder
    def _show_placeholder(self):
        self.delete(0, tk.END)
        self.insert(0, self.placeholder)
        self.configure(foreground=self.placeholder_color, show=None)
        self.has_placeholder = True

    # Clear placeholder
    def _clear_placeholder(self):
        if self.has_placeholder:
            self.delete(0, tk.END)
            self.configure(foreground=self.normal_color)
            if self.real_show is not None:
                self.configure(show=self.real_show)
            self.has_placeholder = False

    def _on_focus_in(self, event):
        self._clear_placeholder()

    def _on_focus_out(self, event):
        if not self.get():
            self._show_placeholder()

    def _on_key(self, event):
        # on first meaningful key press clear placeholder so typed chars don't append to it
        if self.has_placeholder:
            # ignore pure modifier keys
            if event.keysym not in ("Shift_L", "Shift_R", "Control_L", "Control_R",
                                    "Alt_L", "Alt_R", "Caps_Lock", "Num_Lock"):
                self._clear_placeholder()

    def get(self, *args, **kwargs):
        # return empty string when placeholder is visible so callers (login/register) don't see placeholder text
        if getattr(self, "has_placeholder", False):
            return ""
        return super().get(*args, **kwargs)

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Notes")
        self.geometry("700x500")
        self.resizable(False, False)

        # theme palette 
        self.bg = "#f5f7fa"        
        self.panel = "#ffffff"     
        self.input_bg = "#ffffff"  
        self.fg = "#1f2937"        
        self.acc = "#1976d2"       

        # window back
        self.configure(bg=self.bg)

        # ttk style setup
        self.style = ttk.Style(self)
        try:
            self.style.theme_use("clam")
        except Exception:
            pass

        # General frame back
        self.style.configure("TFrame", background=self.panel)
        self.style.configure("Card.TFrame", background=self.panel)

        # Labels
        self.style.configure("TLabel", background=self.panel, foreground=self.fg, font=("Segoe UI", 11))
        self.style.configure("Header.TLabel", background=self.panel, foreground=self.fg,
                             font=("Segoe UI", 18, "bold"))

        # Entries / inputs
        self.style.configure("TEntry", fieldbackground=self.input_bg, background=self.input_bg, foreground=self.fg)

        # Btns
        self.style.configure("TButton", padding=6, relief="flat", background=self.panel, foreground=self.fg)
        self.style.configure("Accent.TButton", foreground="white", background=self.acc)
        self.style.map("Accent.TButton",
                       background=[("active", "#125ea6")],
                       foreground=[("!disabled", "white")])

        self.style.configure("Treeview", background=self.panel, fieldbackground=self.panel, foreground=self.fg)
        self.style.configure("Treeview.Heading", background=self.panel, foreground=self.fg)

        
        self.option_add("*Listbox.background", self.input_bg)
        self.option_add("*Listbox.foreground", self.fg)
        self.option_add("*Text.background", self.input_bg)
        self.option_add("*Text.foreground", self.fg)
        self.option_add("*Entry.background", self.input_bg)
        self.option_add("*Entry.foreground", self.fg)

        # container for frames
        self.container = ttk.Frame(self, style="Card.TFrame")
        self.container.pack(fill="both", expand=True)
        self.container.configure(style="TFrame")

        self.frames = {}
        
        # initialize frames
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

# Login frame
# Login frame
class LoginFrame(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        center_container = ttk.Frame(self)
        center_container.pack(expand=True)

        card = ttk.Frame(center_container, style="Card.TFrame", padding=40)
        card.pack(padx=30, pady=30)

        ttk.Label(card, text="Login", font=("Arial", 20, "bold")).pack(pady=(0, 25))

        self.username_entry = PlaceholderEntry(card, width=35, placeholder="Username")
        self.username_entry.pack(pady=8)

        self.password_entry = PlaceholderEntry(card, width=35, placeholder="Password", show="*")
        self.password_entry.pack(pady=8)
        self.password_entry.bind("<Return>", lambda event: self.login())

        ttk.Button(card, text="Login", width=25, style="Accent.TButton", command=self.login).pack(pady=(15, 8))
        ttk.Button(card, text="Create new account", width=25,
                   command=lambda: controller.show_frame(RegisterFrame)).pack(pady=5)

    def login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        success, role = login_user(username, password)

        if success:
            self.controller.login_success(username, role)
        else:
            messagebox.showerror("Error", "Invalid username or password.")

# Register frame
class RegisterFrame(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        center_container = ttk.Frame(self)
        center_container.pack(expand=True)

        card = ttk.Frame(center_container, style="Card.TFrame", padding=40)
        card.pack(padx=30, pady=30)

        ttk.Label(card, text="Register", font=("Arial", 20, "bold")).pack(pady=(0, 25))

        self.username_entry = PlaceholderEntry(card, width=35, placeholder="Choose Username")
        self.username_entry.pack(pady=8)

        self.password_entry = PlaceholderEntry(card, width=35, placeholder="Choose Password", show="*")
        self.password_entry.pack(pady=8)

        self.confirm_entry = PlaceholderEntry(card, width=35, placeholder="Retype Password", show="*")
        self.confirm_entry.pack(pady=8)
        self.confirm_entry.bind("<Return>", lambda event: self.register())

        ttk.Button(card, text="Register", width=25, style="Accent.TButton", command=self.register).pack(pady=(15, 8))
        ttk.Button(card, text="Back to Login", width=25,
                   command=lambda: controller.show_frame(LoginFrame)).pack(pady=5)

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

# User dashboard frame
class UserDashboardFrame(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        center_container = ttk.Frame(self)
        center_container.pack(expand=True)

        card = ttk.Frame(center_container, style="Card.TFrame", padding=30)
        card.pack(padx=30, pady=30)

        ttk.Label(card, text="Your Notes", font=("Arial", 20, "bold")).pack(pady=(0, 15))

        self.listbox = tk.Listbox(card, height=12, width=60)
        self.listbox.pack(pady=10)

        # open note on double-click and on Return
        self.listbox.bind("<Double-Button-1>", lambda e: self.open_note_popup())
        self.listbox.bind("<Return>", lambda e: self.open_note_popup())

        # open note on double-click and on Return
        self.listbox.bind("<Double-Button-1>", lambda e: self.open_note_popup())
        self.listbox.bind("<Return>", lambda e: self.open_note_popup())

        # open note on double-click and on Return
        self.listbox.bind("<Double-Button-1>", lambda e: self.open_note_popup())
        self.listbox.bind("<Return>", lambda e: self.open_note_popup())

        btn_frame = ttk.Frame(card)
        btn_frame.pack(pady=(10, 0))

        ttk.Button(btn_frame, text="Add Note", style="Accent.TButton", command=self.add_note_popup).grid(row=0, column=0, padx=5, pady=5)
        ttk.Button(btn_frame, text="Edit Note", command=self.edit_note_popup).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(btn_frame, text="Delete Note", command=self.delete_note).grid(row=0, column=2, padx=5, pady=5)
        ttk.Button(btn_frame, text="Logout", command=self.logout).grid(row=0, column=3, padx=5, pady=5)

    def refresh(self):
        self.listbox.delete(0, tk.END)
        notes = get_user_notes(self.controller.active_user)
        for note in notes:
            self.listbox.insert(tk.END, note["title"])

    def add_note_popup(self):
        win = tk.Toplevel(self)
        win.title("Add Note")
        win.geometry("550x450")
        win.resizable(True, True)
        # make window background match app
        win.configure(bg=self.controller.bg)

        # use a card frame inside the toplevel so ttk styles apply consistently
        frame = ttk.Frame(win, style="Card.TFrame", padding=12)
        frame.pack(fill="both", expand=True, padx=12, pady=12)

        ttk.Label(frame, text="Title").pack(anchor="w")
        title_entry = ttk.Entry(frame, width=40)
        title_entry.pack(pady=5, fill="x")

        ttk.Label(frame, text="Content").pack(anchor="w")
        content_text = tk.Text(frame, width=45, height=15)
        content_text.pack(fill="both", expand=True)

        def save_note():
            title = title_entry.get().strip()
            content = content_text.get("1.0", tk.END).strip()

            if not title:
                messagebox.showerror("Error", "Title cannot be empty.")
                return

            add_note(self.controller.active_user, title, content)
            self.refresh()
            win.destroy()

        title_entry.bind("<Return>", lambda event: save_note())
        content_text.bind("<Control-Return>", lambda event: save_note())

        ttk.Button(frame, text="Save", command=save_note).pack(pady=8)

        # focus title for convenience
        title_entry.focus_set()

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
        win.geometry("550x450")
        win.resizable(True, True)

        ttk.Label(frame, text="Title").pack(anchor="w")
        title_entry = ttk.Entry(frame, width=40)
        title_entry.insert(0, note["title"])
        title_entry.pack(pady=5, fill="x")

        ttk.Label(frame, text="Content").pack(anchor="w")
        content_text = tk.Text(frame, width=45, height=15)
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

        title_entry.bind("<Return>", lambda event: save_edit())
        content_text.bind("<Control-Return>", lambda event: save_edit())

        ttk.Button(frame, text="Save Changes", command=save_edit).pack(pady=8)

        title_entry.focus_set()

    def open_note_popup(self):
        # open selected note in a read-only viewer with option to edit
        sel = self.listbox.curselection()
        if not sel:
            return
        index = sel[0]
        notes = get_user_notes(self.controller.active_user)
        note = notes[index]

        win = tk.Toplevel(self)
        win.title(note["title"] or "Note")
        win.geometry("500x400")
        win.resizable(True, True)
        win.configure(bg=self.controller.bg)

        frame = ttk.Frame(win, style="Card.TFrame", padding=12)
        frame.pack(fill="both", expand=True, padx=12, pady=12)

        ttk.Label(frame, text=note["title"], font=("Arial", 14, "bold")).pack(anchor="w")

        content_text = tk.Text(frame, width=45, height=15)
        content_text.insert("1.0", note["content"])
        content_text.configure(state="disabled")
        content_text.pack(fill="both", expand=True, pady=(6, 6))

        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill="x")

        ttk.Button(btn_frame, text="Edit", command=lambda: (win.destroy(), self.edit_note_popup())).pack(side="left", padx=4)
        ttk.Button(btn_frame, text="Close", command=win.destroy).pack(side="right", padx=4)

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

class AdminDashboardFrame(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        center_container = ttk.Frame(self)
        center_container.pack(expand=True)

        card = ttk.Frame(center_container, style="Card.TFrame", padding=30)
        card.pack(padx=30, pady=30)

        ttk.Label(card, text="Admin Dashboard", font=("Arial", 20, "bold")).pack(pady=(0, 15))

        self.tree = ttk.Treeview(card, columns=("hash"), show="headings", height=10)
        self.tree.heading("hash", text="Password Hash")
        self.tree.column("hash", width=450)
        self.tree.pack(pady=10)

        btn_frame = ttk.Frame(card)
        btn_frame.pack(pady=(10, 0))

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

if __name__ == "__main__":
    app = App()
    app.mainloop()