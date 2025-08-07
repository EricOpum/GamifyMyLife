import datetime as dt
import random
import tkinter as tk
from tkinter import ttk, messagebox

from .xp import level_from_total_xp
from .config import BOSS_NAMES, ENEMY_NAMES, CAT_EMOJI


class ActiveBattle:
    def __init__(self, root: tk.Tk, boss: bool, player_stats, on_close):
        self.root = root
        self.boss = boss
        self.player_stats = player_stats
        self.on_close = on_close

        self.window = tk.Toplevel(root)
        self.window.title("⚔️ Encounter")
        self.window.geometry("520x520")
        self.window.configure(bg="#0e0f1a")
        self.window.protocol("WM_DELETE_WINDOW", self.close)

        gl_xp = player_stats.get("global_xp", 0)
        gl_level, _, _ = level_from_total_xp(gl_xp)
        self.enemy_max_hp = 50 + int(gl_level * (80 if boss else 40))
        self.enemy_attack = 5 + int(gl_level * (6 if boss else 3))
        self.enemy_name = random.choice(BOSS_NAMES if boss else ENEMY_NAMES)
        self.enemy_hp = self.enemy_max_hp
        self.player_max_hp = 60 + int(gl_level * 25)
        self.player_hp = self.player_max_hp
        self.turn = 1
        self.total_damage_done = 0
        self.total_damage_taken = 0
        self.assist_deadline = None
        if boss:
            self.assist_deadline = dt.datetime.now() + dt.timedelta(minutes=5)

        style = ttk.Style(self.window)
        try:
            style.theme_use("clam")
        except Exception:
            pass
        style.configure("Game.TFrame", background="#0e0f1a")
        style.configure("Game.TLabel", background="#0e0f1a", foreground="#e6e6f0", font=("Segoe UI", 10))
        style.configure("GameTitle.TLabel", background="#0e0f1a", foreground="#ffd166", font=("Segoe UI", 13, "bold"))
        style.configure("HP.Horizontal.TProgressbar", troughcolor="#2a2b45", background="#ef476f")
        style.configure("MP.Horizontal.TProgressbar", troughcolor="#2a2b45", background="#06d6a0")
        style.configure("Game.TButton", font=("Segoe UI", 10, "bold"))

        frm = ttk.Frame(self.window, padding=10, style="Game.TFrame")
        frm.pack(fill="both", expand=True)

        title = ttk.Label(frm, text=f"{'👑 Boss ' if boss else '👾 Gegner '}{self.enemy_name} erscheint!", style="GameTitle.TLabel")
        title.pack(pady=6)

        hp_frame = ttk.Frame(frm, style="Game.TFrame")
        hp_frame.pack(fill="x", pady=6)
        self.enemy_hp_var = tk.StringVar()
        ttk.Label(hp_frame, textvariable=self.enemy_hp_var, style="Game.TLabel").pack(anchor="w")
        self.enemy_hp_bar = ttk.Progressbar(hp_frame, style="HP.Horizontal.TProgressbar", maximum=self.enemy_max_hp)
        self.enemy_hp_bar.pack(fill="x")

        self.player_hp_var = tk.StringVar()
        ttk.Label(hp_frame, textvariable=self.player_hp_var, style="Game.TLabel").pack(anchor="w", pady=(6,0))
        self.player_hp_bar = ttk.Progressbar(hp_frame, style="MP.Horizontal.TProgressbar", maximum=self.player_max_hp)
        self.player_hp_bar.pack(fill="x")

        self.stats_var = tk.StringVar()
        ttk.Label(frm, textvariable=self.stats_var, style="Game.TLabel").pack(anchor="w", pady=6)

        mech = (
            "📜 Kampf-Mechanik:\n"
            "• 💪 Fitness + 🛡️ Disziplin → Schaden\n"
            "• 🧠 Intelligenz → Kritische Trefferchance\n"
            "• 🎨 Kreativität → Bonus-Schaden-Chance\n"
            "• 🗣️ Charisma → Chance, gegnerischen Angriff ausfallen zu lassen\n"
        )
        ttk.Label(frm, text=mech, style="Game.TLabel").pack(anchor="w", pady=(0,6))

        self.log_box = tk.Text(frm, height=12, state="disabled", wrap="word", bg="#121428", fg="#e6e6f0")
        self.log_box.pack(fill="both", expand=True, pady=6)

        self.btn_attack = ttk.Button(frm, text="▶ Runde ausführen", style="Game.TButton", command=self.do_round)
        self.btn_attack.pack(pady=(0,6))

        if boss:
            self.assist_var = tk.StringVar(value="⏱️ Boss aktiv: Erledige in 5 Min. weitere Aufgaben → Bonus-Schaden!")
            ttk.Label(frm, textvariable=self.assist_var, style="Game.TLabel").pack(pady=4)

        self.update_stats_label()
        self.update_hp_labels()
        self.write_log("Der Kampf beginnt! Deine Stats skalieren mit deinen Levels.")

    def update_hp_labels(self):
        self.enemy_hp_var.set(f"{self.enemy_name} HP: {self.enemy_hp}/{self.enemy_max_hp}")
        self.player_hp_var.set(f"Spieler HP: {self.player_hp}/{self.player_max_hp}")
        self.enemy_hp_bar.configure(value=self.enemy_hp)
        self.player_hp_bar.configure(value=self.player_hp)

    def update_stats_label(self):
        glevel, _, _ = level_from_total_xp(self.player_stats.get("global_xp", 0))
        fitness = level_from_total_xp(self.player_stats.get("Fitness", 0))[0]
        disziplin = level_from_total_xp(self.player_stats.get("Disziplin", 0))[0]
        intel = level_from_total_xp(self.player_stats.get("Intelligenz", 0))[0]
        charisma = level_from_total_xp(self.player_stats.get("Charisma", 0))[0]
        kreativ = level_from_total_xp(self.player_stats.get("Kreativität", 0))[0]
        self.stats_var.set(
            f"🌍 Global Lvl {glevel} | 🧍 HP {self.player_hp}/{self.player_max_hp}\n"
            f"{CAT_EMOJI['Fitness']} Fit {fitness}  {CAT_EMOJI['Disziplin']} Dis {disziplin}  {CAT_EMOJI['Intelligenz']} Int {intel}  {CAT_EMOJI['Charisma']} Cha {charisma}  {CAT_EMOJI['Kreativität']} Kre {kreativ}"
        )

    def write_log(self, text: str):
        self.log_box.configure(state="normal")
        self.log_box.insert("end", f"{text}\n")
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

    def player_attack_value(self):
        fit_lvl = level_from_total_xp(self.player_stats.get("Fitness", 0))[0]
        dis_lvl = level_from_total_xp(self.player_stats.get("Disziplin", 0))[0]
        int_lvl = level_from_total_xp(self.player_stats.get("Intelligenz", 0))[0]
        kre_lvl = level_from_total_xp(self.player_stats.get("Kreativität", 0))[0]
        cha_lvl = level_from_total_xp(self.player_stats.get("Charisma", 0))[0]

        base = 6 + fit_lvl * 2 + dis_lvl
        base = int(base * random.uniform(0.9, 1.1))

        crit = random.random() < min(0.4, int_lvl * 0.02)
        if crit:
            base = int(base * 1.7)
        flair = random.random() < min(0.35, kre_lvl * 0.02)
        if flair:
            base += 6 + kre_lvl
        talkdown = random.random() < min(0.25, cha_lvl * 0.015)
        return base, crit, flair, talkdown

    def do_round(self):
        if self.enemy_hp <= 0 or self.player_hp <= 0:
            return
        self.write_log(f"— Runde {self.turn} —")
        dmg, crit, flair, talkdown = self.player_attack_value()
        self.enemy_hp = max(0, self.enemy_hp - dmg)
        self.total_damage_done += dmg
        self.write_log(f"🗡️ Du verursachst {dmg} Schaden{' (Krit!)' if crit else ''}{' (+Kreativ)' if flair else ''}.")
        self.update_hp_labels()

        if self.enemy_hp <= 0:
            self.win()
            return

        if talkdown:
            self.write_log("🗣️ Dein Charisma verunsichert den Gegner. Sein Angriff fällt aus!")
        else:
            edmg = int(self.enemy_attack * random.uniform(0.85, 1.15))
            self.player_hp = max(0, self.player_hp - edmg)
            self.total_damage_taken += edmg
            self.write_log(f"💥 {self.enemy_name} trifft dich für {edmg} Schaden.")
            self.update_hp_labels()
            if self.player_hp <= 0:
                self.lose()
                return

        self.turn += 1
        self.update_stats_label()

        if self.boss and self.assist_deadline:
            remain = max(0, int((self.assist_deadline - dt.datetime.now()).total_seconds()))
            mins = remain // 60
            secs = remain % 60
            self.assist_var.set(f"⏱️ Boss aktiv: noch {mins:02d}:{secs:02d} für Bonus-Schaden!")
            if remain <= 0:
                self.assist_deadline = None

    def apply_task_bonus(self, xp_from_task: int):
        if not self.boss or not self.assist_deadline:
            return
        if dt.datetime.now() > self.assist_deadline:
            return
        bonus = int(5 + xp_from_task * 0.6)
        self.enemy_hp = max(0, self.enemy_hp - bonus)
        self.total_damage_done += bonus
        self.write_log(f"⚡ Task-Bonus! Zusätzlicher Schaden: {bonus}")
        self.update_hp_labels()
        if self.enemy_hp <= 0:
            self.win()

    def win(self):
        self.write_log("✨ Sieg!")
        messagebox.showinfo("Gamify MyLife", "Sieg! Weiter so.")
        self.close(result="win")

    def lose(self):
        self.write_log("💀 Niederlage. Morgen wird's besser.")
        messagebox.showinfo("Gamify MyLife", "Niederlage – kein Drama. Weiter machen!")
        self.close(result="lose")

    def close(self, result: str | None = None):
        if self.on_close:
            self.on_close(result or "closed", self)
        try:
            self.window.destroy()
        except Exception:
            pass
