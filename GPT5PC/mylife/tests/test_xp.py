import random
from mylife.xp import xp_needed_for_level, level_from_total_xp, task_xp, add_xp
from mylife.models import Profile


def run_selftests():
    test_xp_math()
    test_task_xp()
    test_add_xp()


def test_xp_math():
    assert xp_needed_for_level(1) == 100
    assert xp_needed_for_level(2) > 100
    assert level_from_total_xp(0) == (1, 0, 100)
    lvl2 = level_from_total_xp(100)
    assert lvl2[0] == 2 and lvl2[1] == 0


def test_task_xp():
    sliders = {"Überwindung": 5, "Anstrengung": 5, "Dauer": 5}
    random.seed(0)
    val = task_xp(sliders)
    assert 24 <= val <= 29


def test_add_xp():
    p = Profile()
    before = p.global_xp
    add_xp(p, "Fitness", 10)
    assert p.global_xp == before + 10
    assert p.category_xp["Fitness"] >= 10
