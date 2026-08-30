from __future__ import annotations

from tests._scene_ast import get_fixed_label_protection, has_camera_motion


def test_transition_3d_labels_are_camera_safe(scene_analysis):
    transition = scene_analysis.get_method("transition_to_3d")
    label_names = {"x_label", "re_label", "im_label"}
    if not has_camera_motion(transition):
        return

    protected = get_fixed_label_protection(transition, label_names)
    missing = sorted(label_names - protected)
    assert not missing, (
        "При вращении камеры 3D-подписи должны быть защищены через "
        "add_fixed_orientation_mobjects() или add_fixed_in_frame_mobjects(). "
        f"Не защищены: {missing}."
    )
