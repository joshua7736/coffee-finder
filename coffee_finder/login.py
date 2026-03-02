"""Login and Registration UI for Coffee Finder."""
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Tuple, Optional
from .auth import register_user, login_user, user_exists


class LoginWindow:
    """Login and registration window."""
    
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Coffee Finder - Login")
        self.window.geometry("400x300")
        self.window.resizable(False, False)
        
        # Center window
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (self.window.winfo_width() // 2)
        y = (self.window.winfo_screenheight() // 2) - (self.window.winfo_height() // 2)
        self.window.geometry(f"+{x}+{y}")
        
        self.username = None
        self.authenticated = False
        
        self._show_login_view()
    
    def _show_login_view(self):
        """Show login screen."""
        # Clear window
        for widget in self.window.winfo_children():
            widget.destroy()
        
        # Title
        title = ttk.Label(self.window, text="Coffee Finder Login", font=("Arial", 16, "bold"))
        title.pack(pady=20)
        
        # Username
        ttk.Label(self.window, text="Username:").pack(pady=(10, 0))
        self.login_username = ttk.Entry(self.window, width=30)
        self.login_username.pack()
        self.login_username.focus()
        
        # Password
        ttk.Label(self.window, text="Password:").pack(pady=(10, 0))
        self.login_password = ttk.Entry(self.window, width=30, show="*")
        self.login_password.pack()
        
        # Buttons
        button_frame = tk.Frame(self.window)
        button_frame.pack(pady=20)
        
        login_btn = tk.Button(button_frame, text="Login", command=self._on_login, width=15)
        login_btn.pack(side=tk.LEFT, padx=5)
        
        register_btn = tk.Button(button_frame, text="Create Account", command=self._show_register_view, width=15)
        register_btn.pack(side=tk.LEFT, padx=5)
        
        # Bind Enter key
        self.login_password.bind("<Return>", lambda e: self._on_login())
    
    def _on_login(self):
        """Handle login button."""
        username = self.login_username.get().strip()
        password = self.login_password.get()
        
        if not username or not password:
            messagebox.showerror("Error", "Username and password required")
            return
        
        success, message = login_user(username, password)
        if success:
            self.username = username
            self.authenticated = True
            self.window.destroy()
        else:
            messagebox.showerror("Login Failed", message)
    
    def _show_register_view(self):
        """Show registration screen."""
        # Clear window
        for widget in self.window.winfo_children():
            widget.destroy()
        
        # Title
        title = ttk.Label(self.window, text="Create Account", font=("Arial", 16, "bold"))
        title.pack(pady=20)
        
        # Email
        ttk.Label(self.window, text="Email:").pack(pady=(5, 0))
        self.reg_email = ttk.Entry(self.window, width=30)
        self.reg_email.pack()
        self.reg_email.focus()
        
        # Username
        ttk.Label(self.window, text="Username:").pack(pady=(5, 0))
        self.reg_username = ttk.Entry(self.window, width=30)
        self.reg_username.pack()
        
        # Password
        ttk.Label(self.window, text="Password (min 6 chars):").pack(pady=(5, 0))
        self.reg_password = ttk.Entry(self.window, width=30, show="*")
        self.reg_password.pack()
        
        # Confirm Password
        ttk.Label(self.window, text="Confirm Password:").pack(pady=(5, 0))
        self.reg_confirm = ttk.Entry(self.window, width=30, show="*")
        self.reg_confirm.pack()
        
        # Buttons
        button_frame = tk.Frame(self.window)
        button_frame.pack(pady=20)
        
        register_btn = tk.Button(button_frame, text="Register", command=self._on_register, width=15)
        register_btn.pack(side=tk.LEFT, padx=5)
        
        back_btn = tk.Button(button_frame, text="Back", command=self._show_login_view, width=15)
        back_btn.pack(side=tk.LEFT, padx=5)
        
        # Bind Enter key
        self.reg_confirm.bind("<Return>", lambda e: self._on_register())
    
    def _on_register(self):
        """Handle register button."""
        email = self.reg_email.get().strip()
        username = self.reg_username.get().strip()
        password = self.reg_password.get()
        confirm = self.reg_confirm.get()
        
        if password != confirm:
            messagebox.showerror("Error", "Passwords do not match")
            return
        
        success, message = register_user(username, email, password)
        if success:
            messagebox.showinfo("Success", message + "\nPlease log in with your credentials")
            self._show_login_view()
        else:
            messagebox.showerror("Registration Failed", message)
    
    def show(self):
        """Show the login window and return (success, username)."""
        self.window.mainloop()
        return self.authenticated, self.username


def show_login() -> Tuple[bool, Optional[str]]:
    """Show login window and return (authenticated, username)."""
    login = LoginWindow()
    return login.show()
