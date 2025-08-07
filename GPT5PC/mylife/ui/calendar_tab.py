import datetime as dt
import tkinter as tk
from tkinter import ttk

from ..config import CAT_EMOJI


class CalendarTab:
    def __init__(self, app, notebook):
        self.app = app
        self.frame = ttk.Frame(notebook, style="Bg.TFrame")
        notebook.add(self.frame, text="Kalender")

        outer = ttk.Frame(self.frame, padding=10, style="Bg.TFrame")
        outer.pack(fill="both", expand=True)

        self.has_cal = False
        try:
            from tkcalendar import Calendar  # type: ignore
            self.has_cal = True
        except Exception:
            pass

        if self.has_cal:
            from tkcalendar import Calendar  # type: ignore
            left = ttk.Frame(outer, style="Bg.TFrame")
            left.pack(side="left", fill="y")
            right = ttk.Frame(outer, style="Bg.TFrame")
            right.pack(side="left", fill="both", expand=True, padx=(10, 0))

            self.cal = Calendar(left, selectmode="day")
            self.cal.pack()
            self.cal.bind("<<CalendarSelected>>", lambda e: self._populate_day_list(self._get_cal_iso()))

            ttk.Label(right, text="Aufgaben am ausgewählten Tag", style="SubTitle.TLabel").pack(anchor="w")
            self.day_list = tk.Listbox(right)
            self.day_list.pack(fill="both", expand=True, pady=(6, 0))
        else:
            ttk.Label(outer, text="Kalender", style="SubTitle.TLabel").pack(anchor="w")
            self.day_list = tk.Listbox(outer, height=18)
            self.day_list.pack(fill="both", expand=True, pady=(6, 0))

    def _get_cal_iso(self) -> str:
        try:
            d = self.cal.selection_get()
            if isinstance(d, dt.date):
                return d.isoformat()
        except Exception:
            pass
        try:
            s = self.cal.get_date()
            if isinstance(s, dt.date):
                return s.isoformat()
            s = str(s)
            for fmt in ("%Y-%m-%d", "%d.%m.%Y", "%m/%d/%Y", "%d/%m/%Y", "%d.%m.%y", "%m/%d/%y"):
                try:
                    return dt.datetime.strptime(s, fmt).date().isoformat()
                except Exception:
                    continue
            return dt.date.today().isoformat()
        except Exception:
            return dt.date.today().isoformat()

    def _populate_day_list(self, ymd: str | None = None):
        self.day_list.delete(0, "end")
        if ymd is None:
            ymd = dt.date.today().isoformat()
        items = [t for t in self.app.state.tasks if t.active and (t.due_date == ymd)]
        items.sort(key=lambda x: (x.category, x.title))
        for t in items:
            s = f"[{CAT_EMOJI.get(t.category, '')} {t.category}] {t.title}  (U:{t.sliders['Überwindung']} A:{t.sliders['Anstrengung']} D:{t.sliders['Dauer']})"
            self.day_list.insert("end", s)

    def refresh(self):
        if self.has_cal:
            self._populate_day_list(self._get_cal_iso())
        else:
            self._populate_day_list(dt.date.today().isoformat())
