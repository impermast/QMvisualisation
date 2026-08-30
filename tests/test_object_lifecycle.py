from __future__ import annotations

from tests._scene_ast import get_potential_lifecycle_issues, get_terminal_construct_helper


def test_local_scene_objects_are_not_forgotten(scene_analysis):
    terminal_helper = get_terminal_construct_helper(scene_analysis)
    issues: list[str] = []
    for method_name in ["show_theory", "show_2d_scene", "transition_to_3d", "show_outro"]:
        method = scene_analysis.get_method_or_none(method_name)
        if method is None:
            continue
        issues.extend(get_potential_lifecycle_issues(method, terminal=method_name == terminal_helper))

    assert not issues, (
        "Найдены локальные объекты сцены, которые показаны, но не завершили жизненный цикл явно. "
        f"Потенциальные проблемы: {issues}"
    )
