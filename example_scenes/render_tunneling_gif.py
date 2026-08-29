"""Автономная генерация GIF для scattering/tunneling MVP без Manim."""

from __future__ import annotations

import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from core.quantum_state import PlaneWaveState
from core.quantum_system import PotentialStep
from core.state_evolution import ScatteringEvolution


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "media" / "generated_gifs"
OUTPUT_PATH = OUTPUT_DIR / "tunneling_step_mvp.gif"

WIDTH = 960
HEIGHT = 540
FPS = 20
SECONDS_PER_CASE = 4
FRAMES_PER_CASE = FPS * SECONDS_PER_CASE
TOTAL_FRAMES = FRAMES_PER_CASE * 2

X_MIN = -5.0
X_MAX = 5.0
Y_MIN = -2.8
Y_MAX = 3.2
Z_MIN = -2.2
Z_MAX = 2.2
SAMPLES = 300

BACKGROUND = (8, 10, 18)
AXIS = (185, 205, 255)
GRID = (45, 58, 90)
WAVE = (255, 120, 120)
POTENTIAL = (80, 220, 140)
TEXT = (235, 240, 250)
SUBTEXT = (180, 190, 210)


def project_point(x: float, y: float, z: float) -> tuple[float, float]:
    sx = 0.78 * x + 0.36 * z
    sy = 0.88 * y - 0.22 * x + 0.56 * z
    px = 120 + (sx - (-5.2)) / (8.8 - (-5.2)) * 720
    py = 430 - (sy - (-3.8)) / (5.8 - (-3.8)) * 330
    return px, py


def build_case(title: str, k: float, u0: float) -> dict:
    state = PlaneWaveState(k=k, mass=1.0)
    system = PotentialStep(U0=u0, x0=0.0, mass=1.0)
    evolution = ScatteringEvolution(state, system)
    return {
        "title": title,
        "state": state,
        "system": system,
        "evolution": evolution,
    }


CASES = [
    build_case("Step scattering: E > U0", k=3.0, u0=2.0),
    build_case("Step tunneling tail: E < U0", k=2.0, u0=3.0),
]


def get_font(size: int):
    try:
        return ImageFont.truetype("DejaVuSans.ttf", size=size)
    except OSError:
        return ImageFont.load_default()


FONT_TITLE = get_font(28)
FONT_TEXT = get_font(20)
FONT_SMALL = get_font(16)


def draw_axes(draw: ImageDraw.ImageDraw) -> None:
    origin = project_point(X_MIN, 0.0, 0.0)
    x_end = project_point(X_MAX, 0.0, 0.0)
    y_end = project_point(0.0, Y_MAX, 0.0)
    z_end = project_point(0.0, 0.0, Z_MAX)

    for xg in np.linspace(-4, 4, 5):
        p1 = project_point(xg, Y_MIN, 0.0)
        p2 = project_point(xg, Y_MAX, 0.0)
        draw.line([p1, p2], fill=GRID, width=1)

    draw.line([origin, x_end], fill=AXIS, width=3)
    draw.line([origin, y_end], fill=AXIS, width=3)
    draw.line([origin, z_end], fill=AXIS, width=3)
    draw.text((x_end[0] + 8, x_end[1] - 8), "x", font=FONT_TEXT, fill=TEXT)
    draw.text((y_end[0] + 8, y_end[1] - 8), "Re(psi)", font=FONT_TEXT, fill=TEXT)
    draw.text((z_end[0] + 8, z_end[1] - 8), "Im(psi)", font=FONT_TEXT, fill=TEXT)


def draw_potential(draw: ImageDraw.ImageDraw, system: PotentialStep) -> None:
    xs = np.linspace(X_MIN, X_MAX, SAMPLES)
    ys = 0.75 * system.potential(xs)
    points = [project_point(float(x), float(y), 0.0) for x, y in zip(xs, ys)]
    draw.line(points, fill=POTENTIAL, width=4)


def draw_wave(draw: ImageDraw.ImageDraw, evolution: ScatteringEvolution, t: float) -> None:
    xs = np.linspace(X_MIN, X_MAX, SAMPLES)
    psi = evolution.psi(xs, t)
    pts = [project_point(float(x), float(np.real(v)), float(np.imag(v))) for x, v in zip(xs, psi)]
    draw.line(pts, fill=WAVE, width=4)


def draw_overlay(draw: ImageDraw.ImageDraw, case: dict, frame_index: int) -> None:
    evo = case["evolution"]
    relation = "E > U0" if evo.energy > case["system"].U0 else "E < U0"
    draw.text((28, 24), case["title"], font=FONT_TITLE, fill=TEXT)
    draw.text((28, 64), f"{relation}; E={evo.energy:.2f}; U0={case['system'].U0:.2f}", font=FONT_TEXT, fill=SUBTEXT)
    draw.text((28, 92), f"|R|^2={evo.reflection_probability:.3f}; |T|^2={evo.transmission_probability:.3f}", font=FONT_TEXT, fill=SUBTEXT)
    draw.text((28, 120), "Green: potential; Red: 3D projection of wavefunction", font=FONT_SMALL, fill=SUBTEXT)
    draw.text((28, HEIGHT - 34), f"frame {frame_index + 1}/{TOTAL_FRAMES}", font=FONT_SMALL, fill=SUBTEXT)


def make_frame(case: dict, local_index: int, global_index: int) -> Image.Image:
    image = Image.new("RGB", (WIDTH, HEIGHT), BACKGROUND)
    draw = ImageDraw.Draw(image)
    draw_axes(draw)
    draw_potential(draw, case["system"])
    time_value = 8.0 * local_index / max(FRAMES_PER_CASE - 1, 1)
    draw_wave(draw, case["evolution"], time_value)
    draw_overlay(draw, case, global_index)
    return image


def render() -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    frames: list[Image.Image] = []
    for case_index, case in enumerate(CASES):
        for local_index in range(FRAMES_PER_CASE):
            global_index = case_index * FRAMES_PER_CASE + local_index
            frames.append(make_frame(case, local_index, global_index))

    frames[0].save(
        OUTPUT_PATH,
        save_all=True,
        append_images=frames[1:],
        duration=math.floor(1000 / FPS),
        loop=0,
        disposal=2,
    )
    return OUTPUT_PATH


if __name__ == "__main__":
    path = render()
    print(path)