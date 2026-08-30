from __future__ import annotations

from tests._scene_ast import get_transition_transform_issues, has_camera_motion


def test_transition_has_camera_motion(scene_analysis):
    transition = scene_analysis.get_method("transition_to_3d")
    assert has_camera_motion(transition), (
        "В transition_to_3d() не найдено движение камеры. "
        "Переход 2D -> 3D должен включать move_camera() или эквивалентное движение камеры."
    )


def test_transition_avoids_scene_swap_transforms_for_main_objects(scene_analysis):
    transition = scene_analysis.get_method("transition_to_3d")
    focus_names = {"axes_2d", "axes_3d", "wave_2d", "wave_3d", "potential_2d", "potential_3d"}
    issues = get_transition_transform_issues(transition, focus_names)
    assert not issues, (
        "Переход 2D -> 3D выглядит как подмена сцены через transform основных объектов. "
        f"Найдены потенциально проблемные анимации: {issues}."
    )
