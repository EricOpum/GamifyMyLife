from tkinter import ttk
from ..config import CATEGORIES, CAT_EMOJI
from ..xp import level_from_total_xp


class StatsTab:
    def __init__(self, app, notebook):
        self.app = app
        self.frame = ttk.Frame(notebook, style="Bg.TFrame")
        notebook.add(self.frame, text="Stats")
        outer = ttk.Frame(self.frame, padding=10, style="Bg.TFrame")
        outer.pack(fill="both", expand=True)

        ttk.Label(outer, text="Fortschritt", style="SubTitle.TLabel").pack(anchor="w")
        self.stats_frames = {}
        for c in CATEGORIES + ["Global"]:
            frm = ttk.Frame(outer, style="Bg.TFrame")
            frm.pack(fill="x", pady=6)
            ttk.Label(frm, text=f"{CAT_EMOJI.get(c, '🌍')} {c}", width=18, style="SubTitle.TLabel").pack(side="left")
            p = ttk.Progressbar(frm, maximum=100)
            p.pack(side="left", fill="x", expand=True, padx=6)
            from tkinter import StringVar
            txt = StringVar()
            ttk.Label(frm, textvariable=txt, width=22, style="SubTitle.TLabel").pack(side="left")
            self.stats_frames[c] = (p, txt)

    def refresh(self):
        for c in list(self.stats_frames.keys()):
            if c == "Global":
                total = self.app.state.profile.global_xp
            else:
                total = self.app.state.profile.category_xp.get(c, 0)
            lvl, into, need = level_from_total_xp(total)
            pct = int(100 * into / max(1, need))
            pbar, txt = self.stats_frames[c]
            pbar.configure(value=pct)
            txt.set(f"Lvl {lvl}  ({into}/{need} XP)")
