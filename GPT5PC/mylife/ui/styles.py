from tkinter import ttk

def apply_styles():
    style = ttk.Style()
    try:
        style.theme_use("clam")
    except Exception:
        pass
    style.configure("Title.TLabel", font=("Segoe UI", 14, "bold"), foreground="#ffd166", background="#0b0c16")
    style.configure("SubTitle.TLabel", font=("Segoe UI", 11, "bold"), foreground="#e6e6f0", background="#0b0c16")
    style.configure("Bg.TFrame", background="#0b0c16")
    style.configure("TNotebook", background="#0b0c16")
    style.configure("TNotebook.Tab", padding=(14, 8))
    style.configure("Game.TButton", font=("Segoe UI", 10, "bold"))
