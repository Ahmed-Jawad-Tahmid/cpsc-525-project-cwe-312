# python3 app/main.py

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

        kwargs["show"] = None
        super().__init__(master, **kwargs)

        self.normal_color = self.cget("foreground") or "black"
        self.has_placeholder = False

        self.bind("<FocusIn>", self._on_focus_in)
        self.bind("<FocusOut>", self._on_focus_out)
        self.bind("<Key>", self._on_key)

        self._show_placeholder()

    def _show_placeholder(self):
        self.delete(0, tk.END)
        self.insert(0, self.placeholder)
        self.configure(foreground=self.placeholder_color, show=None)
        self.has_placeholder = True

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
        if self.has_placeholder and event.keysym not in (
            "Shift_L", "Shift_R", "Control_L", "Control_R",
            "Alt_L", "Alt_R", "Caps_Lock", "Num_Lock"
        ):
            self._clear_placeholder()

    def get(self, *args, **kwargs):
        if self.has_placeholder:
            return ""
        return super().get(*args, **kwargs)


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Notes")
        self.geometry("700x500")
        self.resizable(False, False)

        # theme
        self.bg = "#f5f7fa"
        self.panel = "#ffffff"
        self.input_bg = "#ffffff"
        self.fg = "#1f2937"
        self.acc = "#1976d2"

        self.configure(bg=self.bg)

        self.style = ttk.Style(self)
        try:
            self.style.theme_use("clam")
        except Exception:
            pass

        self.style.configure("TFrame", background=self.panel)
        self.style.configure("Card.TFrame", background=self.panel)
        self.style.configure("TLabel", background=self.panel, foreground=self.fg)
        self.style.configure("TEntry", fieldbackground=self.input_bg,
                             background=self.input_bg, foreground=self.fg)
        self.style.configure("Accent.TButton", foreground="white", background=self.acc)

        self.container = ttk.Frame(self, style="Card.TFrame")
        self.container.pack(fill="both", expand=True)

        self.frames = {}
        for F in (LoginFrame, RegisterFrame, UserDashboardFrame, AdminDashboardFrame):
            frame = F(self.container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(LoginFrame)

    def show_frame(self, page):
        self.frames[page].tkraise()

    def login_success(self, username, role):
        self.active_user = username
        if role == "admin":
            self.frames[AdminDashboardFrame].refresh()
            self.show_frame(AdminDashboardFrame)
        else:
            self.frames[UserDashboardFrame].refresh()
            self.show_frame(UserDashboardFrame)


class LoginFrame(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        card = ttk.Frame(self, padding=40)
        card.pack(expand=True)

        ttk.Label(card, text="Login", font=("Arial", 20, "bold")).pack(pady=20)

        self.username_entry = PlaceholderEntry(card, width=35, placeholder="Username")
        self.username_entry.pack(pady=8)

        self.password_entry = PlaceholderEntry(card, width=35, placeholder="Password", show="*")
        self.password_entry.pack(pady=8)

        ttk.Button(card, text="Login", style="Accent.TButton",
                   command=self.login).pack(pady=10)

    def login(self):
        success, role = login_user(
            self.username_entry.get().strip(),
            self.password_entry.get().strip()
        )
        if success:
            self.controller.login_success(self.username_entry.get(), role)
        else:
            messagebox.showerror("Error", "Invalid credentials")


class RegisterFrame(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        card = ttk.Frame(self, padding=40)
        card.pack(expand=True)

        ttk.Label(card, text="Register", font=("Arial", 20, "bold")).pack(pady=20)

        self.username_entry = PlaceholderEntry(card, width=35, placeholder="Username")
        self.username_entry.pack(pady=8)

        self.password_entry = PlaceholderEntry(card, width=35, placeholder="Password", show="*")
        self.password_entry.pack(pady=8)

        self.confirm_entry = PlaceholderEntry(card, width=35, placeholder="Confirm Password", show="*")
        self.confirm_entry.pack(pady=8)

        ttk.Button(card, text="Register", style="Accent.TButton",
                   command=self.register).pack(pady=10)

    def register(self):
        if self.password_entry.get() != self.confirm_entry.get():
            messagebox.showerror("Error", "Passwords do not match")
            return

        success, msg = register_user(
            self.username_entry.get(),
            self.password_entry.get()
        )

        if success:
            messagebox.showinfo("Success", msg)
            self.controller.show_frame(LoginFrame)
        else:
            messagebox.showerror("Error", msg)


class UserDashboardFrame(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        card = ttk.Frame(self, padding=30)
        card.pack(expand=True)

        ttk.Label(card, text="Your Notes", font=("Arial", 20, "bold")).pack()

        self.listbox = tk.Listbox(
            card,
            height=12,
            width=60,
            bg=controller.input_bg,
            fg=controller.fg
        )
        self.listbox.pack(pady=10)

        # double click open
        self.listbox.bind("<Double-Button-1>", lambda e: self.open_note_popup())
        self.listbox.bind("<Return>", lambda e: self.open_note_popup())

        btns = ttk.Frame(card)
        btns.pack()

        ttk.Button(btns, text="Add Note", style="Accent.TButton",
                   command=self.add_note_popup).grid(row=0, column=0, padx=5)
        ttk.Button(btns, text="Edit Note",
                   command=self.edit_note_popup).grid(row=0, column=1, padx=5)
        ttk.Button(btns, text="Delete Note",
                   command=self.delete_note).grid(row=0, column=2, padx=5)
        ttk.Button(btns, text="Logout",
                   command=self.logout).grid(row=0, column=3, padx=5)

    def refresh(self):
        self.listbox.delete(0, tk.END)
        for note in get_user_notes(self.controller.active_user):
            self.listbox.insert(tk.END, note["title"])

    def add_note_popup(self):
        win = tk.Toplevel(self)
        win.configure(bg=self.controller.bg)

        frame = ttk.Frame(win, padding=12)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Title").pack(anchor="w")
        title_entry = ttk.Entry(frame)
        title_entry.pack(fill="x")

        ttk.Label(frame, text="Content").pack(anchor="w")
        content_text = tk.Text(
            frame,
            bg=self.controller.input_bg,
            fg=self.controller.fg,
            insertbackground=self.controller.fg,
            height=15
        )
        content_text.pack(fill="both", expand=True)

        def save():
            add_note(self.controller.active_user,
                     title_entry.get(),
                     content_text.get("1.0", tk.END))
            self.refresh()
            win.destroy()

        ttk.Button(frame, text="Save", command=save).pack(pady=8)

    def edit_note_popup(self):
        sel = self.listbox.curselection()
        if not sel:
            return

        index = sel[0]
        note = get_user_notes(self.controller.active_user)[index]

        win = tk.Toplevel(self)
        win.configure(bg=self.controller.bg)

        frame = ttk.Frame(win, padding=12)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Title").pack(anchor="w")
        title_entry = ttk.Entry(frame)
        title_entry.insert(0, note["title"])
        title_entry.pack(fill="x")

        ttk.Label(frame, text="Content").pack(anchor="w")
        content_text = tk.Text(
            frame,
            bg=self.controller.input_bg,
            fg=self.controller.fg,
            insertbackground=self.controller.fg,
            height=15
        )
        content_text.insert("1.0", note["content"])
        content_text.pack(fill="both", expand=True)

        def save():
            edit_note(self.controller.active_user, index,
                      title_entry.get(),
                      content_text.get("1.0", tk.END))
            self.refresh()
            win.destroy()

        ttk.Button(frame, text="Save Changes", command=save).pack(pady=8)

    def open_note_popup(self):
        sel = self.listbox.curselection()
        if not sel:
            return

        index = sel[0]
        note = get_user_notes(self.controller.active_user)[index]

        win = tk.Toplevel(self)
        win.configure(bg=self.controller.bg)

        frame = ttk.Frame(win, padding=12)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text=note["title"], font=("Arial", 14, "bold")).pack(anchor="w")

        content = tk.Text(
            frame,
            bg=self.controller.input_bg,
            fg=self.controller.fg,
            insertbackground=self.controller.fg,
            height=15
        )
        content.insert("1.0", note["content"])
        content.configure(state="disabled")
        content.pack(fill="both", expand=True)

    def delete_note(self):
        sel = self.listbox.curselection()
        if sel and messagebox.askyesno("Confirm", "Delete note?"):
            delete_note(self.controller.active_user, sel[0])
            self.refresh()

    def logout(self):
        self.controller.show_frame(LoginFrame)


class AdminDashboardFrame(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        card = ttk.Frame(self, padding=30)
        card.pack(expand=True)

        ttk.Label(card, text="Admin Dashboard", font=("Arial", 20, "bold")).pack()

        self.tree = ttk.Treeview(card, columns=("hash"), show="headings")
        self.tree.heading("hash", text="Password Hash")
        self.tree.pack()

    def refresh(self):
        self.tree.delete(*self.tree.get_children())
        for u in view_all_users():
            self.tree.insert("", tk.END,
                             values=(f"{u['username']} : {u['password_hash']}"))


if __name__ == "__main__":
    app = App()
    app.mainloop()
