import sys
import tkinter as tk
from mylife.ui.app import MyLifeApp
from mylife.persistence import save_state
from mylife.config import DATA_FILE


def main():
    if "--selftest" in sys.argv:
        from tests.test_xp import run_selftests
        run_selftests()
        print("Self-tests passed.")
        return

    root = tk.Tk()
    app = MyLifeApp(root)

    def on_close():
        try:
            save_state(DATA_FILE, app.state)
        except Exception:
            pass
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_close)
    root.mainloop()


if __name__ == "__main__":
    main()
