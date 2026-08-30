from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python tests/run_tests.py <scene_path>")
        return 2

    repo_root = Path(__file__).resolve().parents[1]
    scene_path = (repo_root / sys.argv[1]).resolve() if not Path(sys.argv[1]).is_absolute() else Path(sys.argv[1]).resolve()
    if not scene_path.exists():
        print(f"Scene file not found: {scene_path}")
        return 2

    env = os.environ.copy()
    env["QM_SCENE_PATH"] = str(scene_path)
    command = [sys.executable, "-m", "pytest", str(Path(__file__).resolve().parent), "-q", "--scene-path", str(scene_path)]
    completed = subprocess.run(command, cwd=repo_root, env=env)
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
