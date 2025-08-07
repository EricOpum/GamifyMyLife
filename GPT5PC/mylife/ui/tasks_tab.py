import datetime as dt
import uuid
import tkinter as tk
from tkinter import ttk, messagebox

from ..models import Task
from ..persistence import save_state
from ..config import DATA_FILE, CATEGORIES, SLIDER_KEYS, CAT_EMOJI


class TasksTab:
    def __init__(self, app, notebook):
        self.app = app
        self.frame = ttk.Frame(notebook, style="Bg.TFrame")
        notebook.add(self.frame, text="Aufgaben")

        outer = ttk.Frame(self.frame, padding=10, style="Bg.TFrame")
        outer.pack(fill="both", expand=True)

        left = ttk.Frame(outer, style="Bg.TFrame")
        left.pack(side="left", fill="y")
        right = ttk.Frame(outer, style="Bg.TFrame")
        right.pack(side="left", fill="both", expand=True, padx=(10, 0))

        ttk.Label(left, text="Neue Aufgabe", style="SubTitle.TLabel").pack(anchor="w", pady=(0, 6))

        self.title_var = tk.StringVar()
        ttk.Label(left, text="Titel", style="SubTitle.TLabel").pack(anchor="w")
        ttk.Entry(left, textvariable=self.title_var, width=28).pack(anchor="w", pady=(0, 6))

        ttk.Label(left, text="Kategorie", style="SubTitle.TLabel").pack(anchor="w")
        self.category_var = tk.StringVar(value=CATEGORIES[0])
        ttk.Combobox(left, textvariable=self.category_var, values=CATEGORIES, state="readonly", width=25).pack(anchor="w", pady=(0, 6))

        ttk.Label(left, text="Fälligkeit", style="SubTitle.TLabel").pack(anchor="w")
        self.due_var = tk.StringVar(value=dt.date.today().isoformat())
        try:
            from tkcalendar import DateEntry  # type: ignore
            self.has_cal = True
        except Exception:
            self.has_cal = False
        if self.has_cal:
            from tkcalendar import DateEntry  # type: ignore
            self.due_entry = DateEntry(left, date_pattern="yyyy-mm-dd", width=22)
            self.due_entry.set_date(dt.date.today())
            self.due_entry.pack(anchor="w", pady=(0, 6))
        else:
            ttk.Entry(left, textvariable=self.due_var, width=28).pack(anchor="w", pady=(0, 6))

        ttk.Label(left, text="Wiederholung", style="SubTitle.TLabel").pack(anchor="w")
        self.repeat_var = tk.StringVar(value="Keine")
        ttk.Combobox(left, textvariable=self.repeat_var, values=["Keine", "Täglich", "Wöchentlich"], state="readonly", width=25).pack(anchor="w", pady=(0, 6))

        ttk.Label(left, text="Anzahl (Duplikate)", style="SubTitle.TLabel").pack(anchor="w")
        self.count_var = tk.IntVar(value=1)
        ttk.Spinbox(left, from_=1, to=20, textvariable=self.count_var, width=6).pack(anchor="w", pady=(0, 6))

        self.slider_value_labels = {}
        self.slider_vars = {k: tk.IntVar(value=0) for k in SLIDER_KEYS}
        for k in SLIDER_KEYS:
            ttk.Label(left, text=k, style="SubTitle.TLabel").pack(anchor="w")
            s = ttk.Scale(left, from_=0, to=10, orient="horizontal", variable=self.slider_vars[k])
            s.pack(anchor="w", fill="x")
            lbl = ttk.Label(left, text="0", style="SubTitle.TLabel")
            lbl.pack(anchor="w", pady=(0, 6))
            self.slider_value_labels[k] = lbl
            s.configure(command=lambda _v=None, key=k: self._on_slider_move(key))

        ttk.Button(left, text="Aufgabe hinzufügen", style="Game.TButton", command=self.add_task_clicked).pack(anchor="w", pady=8)

        topbar = ttk.Frame(right, style="Bg.TFrame")
        topbar.pack(fill="x")
        ttk.Label(topbar, text="Offene Aufgaben", style="SubTitle.TLabel").pack(side="left")
        ttk.Button(topbar, text="Erledigt markieren", style="Game.TButton", command=self.complete_selected).pack(side="right")

        self.task_tree = ttk.Treeview(right, columns=("cat", "due", "rep", "u", "a", "d"), show="headings", selectmode="browse")
        for cid, text in zip(["cat","due","rep","u","a","d"], ["Kategorie","Fällig","Wdh.","Überw.","Anstr.","Dauer"]):
            self.task_tree.heading(cid, text=text)
        self.task_tree.pack(fill="both", expand=True, pady=(6, 0))

        btnbar = ttk.Frame(right, style="Bg.TFrame")
        btnbar.pack(fill="x", pady=6)
        ttk.Button(btnbar, text="Löschen", style="Game.TButton", command=self.delete_selected).pack(side="left")
        ttk.Button(btnbar, text="Für heute verschieben", style="Game.TButton", command=self.defer_selected_today).pack(side="left", padx=6)

    def _on_slider_move(self, key: str):
        lbl = self.slider_value_labels.get(key)
        if lbl is not None:
            lbl.configure(text=str(int(self.slider_vars[key].get())))

    def _build_task_objects(self, title, category, due, repeat, sliders, count):
        return [Task(id=str(uuid.uuid4()), title=title, category=category, due_date=due, repeat=repeat, sliders=sliders.copy()) for _ in range(max(1, int(count)))]

    def add_task_clicked(self):
        title = self.title_var.get().strip()
        if not title:
            messagebox.showwarning("Gamify MyLife", "Bitte einen Titel eingeben.")
            return
        category = self.category_var.get()
        if self.has_cal:
            _d = self.due_entry.get_date()
            try:
                import datetime as dt
                if hasattr(_d, "isoformat"):
                    due = _d.isoformat()
                else:
                    due = dt.datetime.strptime(str(_d), "%Y-%m-%d").date().isoformat()
            except Exception:
                due = dt.date.today().isoformat()
        else:
            due = self.due_var.get().strip()
        repeat = self.repeat_var.get()
        sliders = {k: int(self.slider_vars[k].get()) for k in SLIDER_KEYS}
        count = int(self.count_var.get())

        new_tasks = self._build_task_objects(title, category, due, repeat, sliders, count)
        self.app.state.tasks.extend(new_tasks)
        save_state(DATA_FILE, self.app.state)

        self.title_var.set("")
        self.count_var.set(1)
        for v in self.slider_vars.values():
            v.set(0)
        for k in SLIDER_KEYS:
            self._on_slider_move(k)
        self.app.refresh_all()

    def _selected_task(self):
        sel = self.task_tree.selection()
        if not sel:
            return None
        tid = sel[0]
        for t in self.app.state.tasks:
            if t.id == tid:
                return t
        return None

    def complete_selected(self):
        t = self._selected_task()
        if not t:
            messagebox.showinfo("Gamify MyLife", "Bitte eine Aufgabe auswählen.")
            return
        self.app.complete_task(t)

    def delete_selected(self):
        t = self._selected_task()
        if not t:
            return
        if messagebox.askyesno("Gamify MyLife", f"Aufgabe '{t.title}' löschen?"):
            self.app.state.tasks = [x for x in self.app.state.tasks if x.id != t.id]
            save_state(DATA_FILE, self.app.state)
            self.app.refresh_all()

    def defer_selected_today(self):
        t = self._selected_task()
        if not t:
            return
        import datetime as dt
        t.due_date = dt.date.today().isoformat()
        save_state(DATA_FILE, self.app.state)
        self.app.refresh_all()

    def refresh(self):
        self.task_tree.delete(*self.task_tree.get_children())
        import datetime as dt
        today = dt.date.today().isoformat()
        active = [t for t in self.app.state.tasks if t.active]
        active.sort(key=lambda t: (t.due_date != today, t.due_date or "", t.category, t.title))
        for t in active:
            cat_disp = f"{CAT_EMOJI.get(t.category,'')} {t.category}"
            self.task_tree.insert("", "end", iid=t.id, values=(cat_disp, t.due_date or "", t.repeat, t.sliders["Überwindung"], t.sliders["Anstrengung"], t.sliders["Dauer"]))
