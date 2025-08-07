from mylife.config import CAT_EMOJI, CATEGORIES, BOSS_NAMES, ENEMY_NAMES


def test_emoji_mapping_has_global():
    assert CAT_EMOJI.get("Global", "🌍")


def test_enemy_names_nonempty():
    for n in BOSS_NAMES + ENEMY_NAMES:
        assert isinstance(n, str) and n.strip()


def test_categories_consistency():
    assert all(isinstance(c, str) and c for c in CATEGORIES)
