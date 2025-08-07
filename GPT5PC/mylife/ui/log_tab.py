from tkinter import ttk


class LogTab:
    def __init__(self, app, notebook):
        self.app = app
        self.frame = ttk.Frame(notebook, style="Bg.TFrame")
        notebook.add(self.frame, text="Log")
        outer = ttk.Frame(self.frame, padding=10, style="Bg.TFrame")
        outer.pack(fill="both", expand=True)

        cols = ("time", "title", "cat", "xp", "enc")
        self.log_tree = ttk.Treeview(outer, columns=cols, show="headings")
        for cid, text in zip(cols, ("Zeitpunkt","Aufgabe","Kategorie","XP","Encounter")):
            self.log_tree.heading(cid, text=text)
        self.log_tree.pack(fill="both", expand=True)

    def refresh(self):
        self.log_tree.delete(*self.log_tree.get_children())
        for e in self.app.state.log[-200:]:
            enc = "—"
            if e.encounter:
                kind = "Boss" if e.encounter.kind == "boss" else "Fight"
                enc = f"{kind}:{e.encounter.result} ({e.encounter.enemy_name})"
            self.log_tree.insert("", "end", values=(e.timestamp, e.task_title, e.category, f"+{e.xp_cat}", enc))
