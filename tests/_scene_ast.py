from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


SHOW_ANIMATIONS = {"FadeIn", "Create", "Write", "GrowFromCenter", "GrowArrow"}
HIDE_ANIMATIONS = {"FadeOut", "Uncreate", "Unwrite", "ShrinkToCenter"}
TRANSFORM_ANIMATIONS = {"ReplacementTransform", "FadeTransform", "Transform", "TransformMatchingShapes"}
CAMERA_MOVES = {"move_camera", "begin_ambient_camera_rotation", "set_camera_orientation"}
FIXED_LABEL_METHODS = {"add_fixed_orientation_mobjects", "add_fixed_in_frame_mobjects"}


@dataclass(frozen=True)
class SceneAnalysis:
    path: Path
    source: str
    tree: ast.Module
    scene_class: ast.ClassDef

    @property
    def scene_class_name(self) -> str:
        return self.scene_class.name

    def get_method(self, name: str) -> ast.FunctionDef:
        for node in self.scene_class.body:
            if isinstance(node, ast.FunctionDef) and node.name == name:
                return node
        raise AssertionError(f"Метод '{name}' не найден в классе сцены '{self.scene_class_name}'.")

    def get_method_or_none(self, name: str) -> ast.FunctionDef | None:
        for node in self.scene_class.body:
            if isinstance(node, ast.FunctionDef) and node.name == name:
                return node
        return None


def load_scene_analysis(scene_path: str | Path) -> SceneAnalysis:
    path = Path(scene_path).resolve()
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(path))
    scene_class = find_scene_class(tree)
    return SceneAnalysis(path=path, source=source, tree=tree, scene_class=scene_class)


def find_scene_class(tree: ast.Module) -> ast.ClassDef:
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and any(_looks_like_scene_base(base) for base in node.bases):
            return node
    raise AssertionError("Не найден класс сцены, наследующийся от Scene/ThreeDScene или совместимого базового класса.")


def _looks_like_scene_base(base: ast.expr) -> bool:
    base_name = get_expr_name(base)
    return base_name is not None and base_name.split(".")[-1] in {"Scene", "ThreeDScene", "MovingCameraScene"}


def get_expr_name(node: ast.AST | None) -> str | None:
    if node is None:
        return None
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        parent = get_expr_name(node.value)
        return f"{parent}.{node.attr}" if parent else node.attr
    return None


def get_string_literal(node: ast.AST | None) -> str | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return None


def iter_calls(node: ast.AST) -> Iterable[ast.Call]:
    for child in ast.walk(node):
        if isinstance(child, ast.Call):
            yield child


def is_self_method_call(node: ast.AST, method_name: str) -> bool:
    return (
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and isinstance(node.func.value, ast.Name)
        and node.func.value.id == "self"
        and node.func.attr == method_name
    )


def get_self_method_calls(function_node: ast.FunctionDef, method_name: str) -> list[ast.Call]:
    return [call for call in iter_calls(function_node) if is_self_method_call(call, method_name)]


def get_next_sections(function_node: ast.FunctionDef) -> list[str]:
    sections: list[str] = []
    for stmt in function_node.body:
        for node in ast.walk(stmt):
            if is_self_method_call(node, "next_section"):
                if node.args:
                    value = get_string_literal(node.args[0])
                    if value is not None:
                        sections.append(value)
    return sections


def extract_names(node: ast.AST | None) -> set[str]:
    if node is None:
        return set()
    names: set[str] = set()
    for child in ast.walk(node):
        if isinstance(child, ast.Name):
            names.add(child.id)
    return names


def get_construct_helper_order(scene: SceneAnalysis) -> list[str]:
    construct = scene.get_method("construct")
    ordered_calls: list[str] = []
    for stmt in construct.body:
        for node in ast.walk(stmt):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                if isinstance(node.func.value, ast.Name) and node.func.value.id == "self":
                    if node.func.attr != "next_section":
                        ordered_calls.append(node.func.attr)
    return ordered_calls


def get_terminal_construct_helper(scene: SceneAnalysis) -> str | None:
    ordered = get_construct_helper_order(scene)
    return ordered[-1] if ordered else None


def get_play_animation_calls(function_node: ast.FunctionDef) -> list[ast.Call]:
    animation_calls: list[ast.Call] = []
    for play_call in get_self_method_calls(function_node, "play"):
        for arg in play_call.args:
            if isinstance(arg, ast.Call):
                animation_calls.append(arg)
    return animation_calls


def get_animation_name(call: ast.Call) -> str | None:
    name = get_expr_name(call.func)
    if name is None:
        return None
    return name.split(".")[-1]


def get_transition_transform_issues(function_node: ast.FunctionDef, focus_names: set[str]) -> list[str]:
    issues: list[str] = []
    for animation_call in get_play_animation_calls(function_node):
        animation_name = get_animation_name(animation_call)
        if animation_name not in {"ReplacementTransform", "FadeTransform"}:
            continue
        used_names = extract_names(animation_call)
        touched = sorted(name for name in focus_names if name in used_names)
        if touched:
            issues.append(
                f"{animation_name} используется для объектов перехода: {', '.join(touched)}"
            )
    return issues


def has_camera_motion(function_node: ast.FunctionDef) -> bool:
    for call in iter_calls(function_node):
        if isinstance(call.func, ast.Attribute) and isinstance(call.func.value, ast.Name):
            if call.func.value.id == "self" and call.func.attr in CAMERA_MOVES:
                if call.func.attr == "set_camera_orientation":
                    continue
                return True
    return False


def function_contains_text_literal(function_node: ast.FunctionDef, text: str) -> bool:
    for call in iter_calls(function_node):
        if get_expr_name(call.func) == "Text":
            for arg in call.args:
                if get_string_literal(arg) == text:
                    return True
    return False


def get_assigned_name_calls(function_node: ast.FunctionDef) -> dict[str, ast.Call]:
    assigned: dict[str, ast.Call] = {}
    for node in ast.walk(function_node):
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.Call):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    assigned[target.id] = node.value
    return assigned


def get_returned_names(function_node: ast.FunctionDef, containment: dict[str, set[str]]) -> set[str]:
    returned: set[str] = set()
    for node in ast.walk(function_node):
        if isinstance(node, ast.Return):
            returned |= expand_contained_names(extract_names(node.value), containment)
    return returned


def expand_contained_names(names: set[str], containment: dict[str, set[str]]) -> set[str]:
    expanded = set(names)
    stack = list(names)
    while stack:
        name = stack.pop()
        for child in containment.get(name, set()):
            if child not in expanded:
                expanded.add(child)
                stack.append(child)
    return expanded


def get_containment_graph(function_node: ast.FunctionDef) -> dict[str, set[str]]:
    graph: dict[str, set[str]] = {}
    for node in ast.walk(function_node):
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.Call):
            names = extract_names(node.value)
            for target in node.targets:
                if isinstance(target, ast.Name):
                    names.discard(target.id)
                    graph[target.id] = names
    return graph


def get_scene_managed_names(function_node: ast.FunctionDef) -> set[str]:
    managed: set[str] = set()
    for method_name in {"add", "remove", *FIXED_LABEL_METHODS}:
        for call in get_self_method_calls(function_node, method_name):
            for arg in call.args:
                managed |= extract_names(arg)
    return managed


def get_animation_targets(function_node: ast.FunctionDef, animation_names: set[str]) -> set[str]:
    targets: set[str] = set()
    for animation_call in get_play_animation_calls(function_node):
        animation_name = get_animation_name(animation_call)
        if animation_name in animation_names:
            for arg in animation_call.args:
                targets |= extract_names(arg)
    return targets


def get_potential_lifecycle_issues(function_node: ast.FunctionDef, terminal: bool = False) -> list[str]:
    if terminal:
        return []

    assigned = get_assigned_name_calls(function_node)
    containment = get_containment_graph(function_node)
    shown = get_animation_targets(function_node, SHOW_ANIMATIONS)
    hidden = get_animation_targets(function_node, HIDE_ANIMATIONS)
    returned = get_returned_names(function_node, containment)
    managed = get_scene_managed_names(function_node)

    issues: list[str] = []
    for name, call in assigned.items():
        constructor_name = get_expr_name(call.func)
        if name not in shown:
            continue
        if name in hidden or name in returned or name in managed:
            continue
        if constructor_name is None:
            continue
        issues.append(
            f"Локальный объект '{name}' показан в методе '{function_node.name}', но не скрыт, не возвращён и не передан под явное управление сцене."
        )
    return issues


def get_fixed_label_protection(function_node: ast.FunctionDef, label_names: set[str]) -> set[str]:
    protected: set[str] = set()
    for method_name in FIXED_LABEL_METHODS:
        for call in get_self_method_calls(function_node, method_name):
            for arg in call.args:
                names = extract_names(arg)
                protected |= {name for name in label_names if name in names}
    return protected
