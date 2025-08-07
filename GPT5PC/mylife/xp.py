from typing import Tuple, Dict
import random

def xp_needed_for_level(level: int) -> int:
    return int(100 * (1.15 ** (level - 1)) + 25 * (level - 1))


def level_from_total_xp(total_xp: int) -> Tuple[int, int, int]:
    level = 1
    remaining = total_xp
    while True:
        need = xp_needed_for_level(level)
        if remaining >= need:
            remaining -= need
            level += 1
        else:
            return level, remaining, need


def task_xp(sliders: Dict[str, int]) -> int:
    u = sliders.get("Überwindung", 0)
    a = sliders.get("Anstrengung", 0)
    d = sliders.get("Dauer", 0)
    base = 10 + 1.3 * u + 1.1 * a + 0.9 * d
    jitter = random.uniform(0.9, 1.1)
    return int(round(base * jitter))


def add_xp(profile, category: str, xp_gain: int):
    profile.category_xp[category] = profile.category_xp.get(category, 0) + xp_gain
    profile.global_xp += xp_gain
    cat_level = level_from_total_xp(profile.category_xp[category])
    glob_level = level_from_total_xp(profile.global_xp)
    return cat_level, glob_level
