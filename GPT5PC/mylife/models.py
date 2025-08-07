from dataclasses import dataclass, field
from typing import Dict, List, Optional
from .config import CATEGORIES

@dataclass
class Task:
    id: str
    title: str
    category: str
    due_date: Optional[str]  # YYYY-MM-DD
    repeat: str  # "Keine" | "Täglich" | "Wöchentlich"
    sliders: Dict[str, int]
    active: bool = True
    streak: int = 0

@dataclass
class Profile:
    category_xp: Dict[str, int] = field(default_factory=lambda: {c: 0 for c in CATEGORIES})
    global_xp: int = 0

@dataclass
class EncounterLog:
    timestamp: str
    kind: str  # "enemy" | "boss"
    enemy_name: str
    result: str  # "win" | "lose"
    damage_done: int
    damage_taken: int

@dataclass
class CompletionLog:
    timestamp: str
    task_id: str
    task_title: str
    category: str
    xp_cat: int
    xp_global: int
    encounter: Optional[EncounterLog] = None

@dataclass
class AppState:
    profile: Profile = field(default_factory=Profile)
    tasks: List[Task] = field(default_factory=list)
    log: List[CompletionLog] = field(default_factory=list)
