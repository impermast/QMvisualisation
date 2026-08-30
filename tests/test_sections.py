from __future__ import annotations

from tests._scene_ast import get_next_sections


EXPECTED_SECTIONS = ["theory", "visual_2d", "transition_3d", "outro"]


def test_construct_sections_order(scene_analysis):
    construct = scene_analysis.get_method("construct")
    actual_sections = get_next_sections(construct)
    assert actual_sections == EXPECTED_SECTIONS, (
        "Секции в construct() должны быть ровно "
        f"{EXPECTED_SECTIONS}, получено: {actual_sections}. "
        "Проверь отсутствие пропусков, лишних секций и нарушение порядка next_section()."
    )
