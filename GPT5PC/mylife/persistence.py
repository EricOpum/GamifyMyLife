import json
import os
from dataclasses import asdict
from .models import AppState, Task, CompletionLog, EncounterLog, Profile


def load_state(path: str) -> AppState:
    if not os.path.exists(path):
        return AppState()
    try:
        with open(path, "r", encoding="utf-8") as f:
            raw = json.load(f)
        profile = Profile(**raw.get("profile", {}))
        tasks = [Task(**t) for t in raw.get("tasks", [])]
        log_entries = []
        for e in raw.get("log", []):
            enc = e.get("encounter")
            enc_obj = EncounterLog(**enc) if enc else None
            log_entries.append(CompletionLog(
                timestamp=e.get("timestamp", ""),
                task_id=e.get("task_id", ""),
                task_title=e.get("task_title", ""),
                category=e.get("category", ""),
                xp_cat=e.get("xp_cat", 0),
                xp_global=e.get("xp_global", 0),
                encounter=enc_obj,
            ))
        return AppState(profile=profile, tasks=tasks, log=log_entries)
    except Exception:
        return AppState()


def save_state(path: str, state: AppState) -> None:
    raw = {
        "profile": asdict(state.profile),
        "tasks": [asdict(t) for t in state.tasks],
        "log": [
            {
                "timestamp": l.timestamp,
                "task_id": l.task_id,
                "task_title": l.task_title,
                "category": l.category,
                "xp_cat": l.xp_cat,
                "xp_global": l.xp_global,
                "encounter": asdict(l.encounter) if l.encounter else None,
            }
            for l in state.log
        ],
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(raw, f, ensure_ascii=False, indent=2)
