import datetime as dt
import uuid
from tkinter import ttk, messagebox

from ..models import Task
from ..persistence import load_state, save_state
from ..config import DATA_FILE


class SettingsTab:
    def __init__(self, app, notebook):
        self.app = app
        self.frame = ttk.Frame(notebook, style="Bg.TFrame")
        notebook.add(self.frame, text="Settings")

        outer = ttk.Frame(self.frame, padding=10, style="Bg.TFrame")
        outer.pack(fill="both", expand=True)
        ttk.Label(outer, text="Speicherort: ./data.json", style="SubTitle.TLabel").pack(anchor="w")
        ttk.Button(outer, text="Daten neu laden", command=self.reload_data).pack(anchor="w", pady=4)
        ttk.Button(outer, text="Daten sichern (Speichern)", command=self.save_now).pack(anchor="w", pady=4)
        ttk.Button(outer, text="Demo-Daten hinzufügen", command=self.add_demo_data).pack(anchor="w", pady=12)
        ttk.Button(outer, text="Alle Aufgaben reaktivieren", command=self.reactivate_all).pack(anchor="w", pady=4)
        ttk.Button(outer, text="🚨 ALLE DATEN LÖSCHEN (Hard Reset)", command=self.hard_reset).pack(anchor="w", pady=(18,4))

    def reload_data(self):
        self.app.state = load_state(DATA_FILE)
        self.app.refresh_all()

    def save_now(self):
        save_state(DATA_FILE, self.app.state)
        messagebox.showinfo("Gamify MyLife", "Gespeichert.")

    def reactivate_all(self):
        for t in self.app.state.tasks:
            t.active = True
        save_state(DATA_FILE, self.app.state)
        self.app.refresh_all()

    def hard_reset(self):
        import os
        if not messagebox.askyesno("Gamify MyLife", "Wirklich ALLE Daten löschen? Dies kann nicht rückgängig gemacht werden."):
            return
        try:
            if os.path.exists(DATA_FILE):
                os.remove(DATA_FILE)
        except Exception as ex:
            messagebox.showerror("Gamify MyLife", f"Konnte Datei nicht löschen: {ex}")
            return
        from ..models import AppState
        self.app.state = AppState()
        save_state(DATA_FILE, self.app.state)
        self.app.refresh_all()
        messagebox.showinfo("Gamify MyLife", "Zurückgesetzt. Willkommen zurück!")

    def add_demo_data(self):
        if self.app.state.tasks:
            if not messagebox.askyesno("Gamify MyLife", "Demo-Aufgaben zu bestehenden hinzufügen?"):
                return
        today = dt.date.today().isoformat()
        demos = [
            Task(id=str(uuid.uuid4()), title="Workout 30 Min", category="Fitness", due_date=today, repeat="Täglich", sliders={"Überwindung":4, "Anstrengung":6, "Dauer":5}),
            Task(id=str(uuid.uuid4()), title="1h Lesen (Fach)", category="Intelligenz", due_date=today, repeat="Täglich", sliders={"Überwindung":3, "Anstrengung":5, "Dauer":6}),
            Task(id=str(uuid.uuid4()), title="Smalltalk an der Kasse", category="Charisma", due_date=today, repeat="Keine", sliders={"Überwindung":6, "Anstrengung":3, "Dauer":2}),
            Task(id=str(uuid.uuid4()), title="Schreibtisch 10 Min", category="Disziplin", due_date=today, repeat="Täglich", sliders={"Überwindung":2, "Anstrengung":2, "Dauer":2}),
            Task(id=str(uuid.uuid4()), title="Skizze zeichnen", category="Kreativität", due_date=today, repeat="Wöchentlich", sliders={"Überwindung":2, "Anstrengung":4, "Dauer":5}),
        ]
        self.app.state.tasks.extend(demos)
        save_state(DATA_FILE, self.app.state)
        self.app.refresh_all()
