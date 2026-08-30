from __future__ import annotations

from tests._scene_ast import function_contains_text_literal, get_self_method_calls


def test_outro_contains_thanks_text(scene_analysis):
    outro = scene_analysis.get_method("show_outro")
    assert function_contains_text_literal(outro, "Спасибо за внимание"), (
        "В show_outro() не найден текст 'Спасибо за внимание'."
    )


def test_outro_does_not_reset_camera(scene_analysis):
    outro = scene_analysis.get_method("show_outro")
    move_camera_calls = get_self_method_calls(outro, "move_camera")
    assert not move_camera_calls, (
        "В show_outro() найден move_camera(). По текущему ТЗ финал должен начинаться из последнего 3D-ракурса без сброса камеры внутри outro."
    )