import datetime as dt
import random
import uuid
import tkinter as tk
from tkinter import ttk, messagebox

from ..config import APP_TITLE, DATA_FILE, CATEGORIES, CAT_EMOJI
from ..models import AppState, Task, CompletionLog, EncounterLog
from ..persistence import load_state, save_state
from ..xp import level_from_total_xp, task_xp, add_xp
from ..battle import ActiveBattle
from .styles import apply_styles
from .tasks_tab import TasksTab
from .calendar_tab import CalendarTab
from .stats_tab import StatsTab
from .log_tab import LogTab
from .settings_tab import SettingsTab


class MyLifeApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        root.title(APP_TITLE)
        root.geometry("1160x760")
        root.configure(bg="#0b0c16")

        self.state: AppState = load_state(DATA_FILE)
        self.active_battle: ActiveBattle | None = None

        apply_styles()
        self._build_ui()
        self.refresh_all()

    def _build_ui(self):
        header = ttk.Frame(self.root, style="Bg.TFrame", padding=10)
        header.pack(fill="x")
        ttk.Label(header, text="🏆 Gamify MyLife", style="Title.TLabel").pack(side="left")

        nb = ttk.Notebook(self.root)
        nb.pack(fill="both", expand=True)

        self.tasks_tab = TasksTab(self, nb)
        self.calendar_tab = CalendarTab(self, nb)
        self.stats_tab = StatsTab(self, nb)
        self.log_tab = LogTab(self, nb)
        self.settings_tab = SettingsTab(self, nb)

    # ---- domain actions ----
    def complete_task(self, t: Task):
        gain = task_xp(t.sliders)
        cat_before = level_from_total_xp(self.state.profile.category_xp.get(t.category, 0))[0]
        glob_before = level_from_total_xp(self.state.profile.global_xp)[0]
        cat_level, glob_level = add_xp(self.state.profile, t.category, gain)

        save_state(DATA_FILE, self.state)

        avg_slider = sum(t.sliders.values()) / max(1, len(t.sliders))
        chance = min(0.65, 0.30 + 0.02 * avg_slider)
        if random.random() < chance:
            gl = glob_level[0]
            boss_chance = 0.15 + (0.1 if (gl % 5 == 0) else 0)
            boss = random.random() < boss_chance
            self.start_battle(boss=boss)

        now = dt.datetime.now().isoformat(timespec="seconds")
        clog = CompletionLog(timestamp=now, task_id=t.id, task_title=t.title, category=t.category, xp_cat=gain, xp_global=gain)
        self.state.log.append(clog)

        if t.repeat == "Täglich":
            next_due = dt.date.fromisoformat(t.due_date or dt.date.today().isoformat()) + dt.timedelta(days=1)
            t.due_date = next_due.isoformat()
        elif t.repeat == "Wöchentlich":
            next_due = dt.date.fromisoformat(t.due_date or dt.date.today().isoformat()) + dt.timedelta(days=7)
            t.due_date = next_due.isoformat()
        else:
            t.active = False

        save_state(DATA_FILE, self.state)

        if level_from_total_xp(self.state.profile.category_xp[t.category])[0] > cat_before:
            messagebox.showinfo(APP_TITLE, f"{t.category}: Level up! 🎉")
        if level_from_total_xp(self.state.profile.global_xp)[0] > glob_before:
            messagebox.showinfo(APP_TITLE, "Globales Level up! 🚀")

        if self.active_battle and self.active_battle.boss:
            self.active_battle.apply_task_bonus(gain)

        self.refresh_all()

    def start_battle(self, boss: bool):
        if self.active_battle:
            return
        stats = {**self.state.profile.category_xp, "global_xp": self.state.profile.global_xp}

        def on_close(result: str, battle: ActiveBattle):
            enc = EncounterLog(
                timestamp=dt.datetime.now().isoformat(timespec="seconds"),
                kind="boss" if boss else "enemy",
                enemy_name=battle.enemy_name,
                result=result if result in ("win", "lose") else "closed",
                damage_done=battle.total_damage_done,
                damage_taken=battle.total_damage_taken,
            )
            for entry in reversed(self.state.log):
                if entry.encounter is None:
                    entry.encounter = enc
                    break
            save_state(DATA_FILE, self.state)
            self.active_battle = None
            self.refresh_all()

        self.active_battle = ActiveBattle(self.root, boss=boss, player_stats=stats, on_close=on_close)

    # ---- refresh ----
    def refresh_all(self):
        self.tasks_tab.refresh()
        self.calendar_tab.refresh()
        self.stats_tab.refresh()
        self.log_tab.refresh()
