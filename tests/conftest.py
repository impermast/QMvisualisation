from __future__ import annotations

import os
from pathlib import Path

import pytest

from tests._scene_ast import SceneAnalysis, load_scene_analysis


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--scene-path",
        action="store",
        default=None,
        help="Путь к Python-файлу Manim-сцены для AST-проверки.",
    )


@pytest.fixture(scope="session")
def scene_path(pytestconfig: pytest.Config) -> Path:
    cli_value = pytestconfig.getoption("scene_path")
    env_value = os.environ.get("QM_SCENE_PATH")
    raw_path = cli_value or env_value
    if not raw_path:
        pytest.fail("Не передан путь к сцене. Используйте --scene-path или QM_SCENE_PATH.")
    path = Path(raw_path).resolve()
    if not path.exists():
        pytest.fail(f"Файл сцены не найден: {path}")
    return path


@pytest.fixture(scope="session")
def scene_analysis(scene_path: Path) -> SceneAnalysis:
    return load_scene_analysis(scene_path)
