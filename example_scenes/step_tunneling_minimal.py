"""Минималистичная сцена о туннелировании на потенциальной ступеньке."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
from manim import *

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.quantum_state import PlaneWaveState
from core.quantum_system import PotentialStep
from core.state_evolution import ScatteringEvolution


config.background_color = "#0B0F17"

X_RANGE_2D = (-5.0, 5.0)
X_RANGE_3D = (-5.0, 5.0)
Y_RANGE = (-1.8, 3.5)
Z_RANGE = (-2.2, 2.2)
X_LENGTH = 11
Y_LENGTH = 5.2
Z_LENGTH = 4.3
WAVE_SAMPLES_2D = 600
WAVE_SAMPLES_3D = 320
POTENTIAL_SCALE = 0.8


class StepTunnelingMinimal(ThreeDScene):
    """Три последовательные части: теория, 2D-картина, плавный переход в 3D."""

    def construct(self):
        state = PlaneWaveState(k=2.0, mass=1.0)
        system = PotentialStep(U0=3.0, x0=0.0, mass=1.0)
        evolution = ScatteringEvolution(state, system)

        self.next_section("theory")
        theory_group = self.show_theory()

        self.next_section("visual_2d")
        axes, x_label, potential_graph, energy_line, wave_graph, left_hint = self.show_2d_scene(
            theory_group,
            evolution,
            system,
        )

        self.next_section("transition_3d")
        self.transition_to_3d(
            axes,
            x_label,
            potential_graph,
            energy_line,
            wave_graph,
            left_hint,
            evolution,
            system,
        )

        self.next_section("outro")
        self.show_outro()

    @property
    def x_values(self) -> np.ndarray:
        return np.linspace(X_RANGE_2D[0], X_RANGE_2D[1], WAVE_SAMPLES_2D)

    @property
    def x_values_3d(self) -> np.ndarray:
        return np.linspace(X_RANGE_3D[0], X_RANGE_3D[1], WAVE_SAMPLES_3D)

    def show_theory(self) -> VGroup:
        potential_left = MathTex(r"U(x)=0,\quad x<0", color=GREEN)
        potential_right = MathTex(r"U(x)=U_0,\quad x\ge 0", color=GREEN)
        title = VGroup(potential_left, potential_right).arrange(DOWN, aligned_edge=LEFT, buff=0.15)
        condition = MathTex(r"E<U_0", color=YELLOW)
        eq_1 = MathTex(r"\psi_I=Ae^{ikx}+Be^{-ikx}", color=WHITE)
        eq_2 = MathTex(r"\psi_{II}=Ce^{-\kappa x}", color=WHITE)
        bc_title = Text("Непрерывность при x = 0", font_size=28, color=GREY_B)
        bc_1 = MathTex(r"\psi_I(0)=\psi_{II}(0)", color=WHITE)
        bc_2 = MathTex(r"\psi_I'(0)=\psi_{II}'(0)", color=WHITE)

        formulas = VGroup(title, condition, eq_1, eq_2, bc_title, bc_1, bc_2).arrange(
            DOWN, aligned_edge=LEFT, buff=0.35
        )
        bc_title.align_to(eq_1, LEFT)
        formulas.scale(0.92)
        formulas.move_to(ORIGIN)

        self.play(FadeIn(title, shift=UP * 0.2), run_time=0.9)
        self.play(FadeIn(condition, shift=UP * 0.15), run_time=0.6)
        self.play(Write(eq_1), run_time=1.0)
        self.play(Write(eq_2), run_time=0.9)
        self.play(FadeIn(bc_title, shift=UP * 0.15), run_time=0.5)
        self.play(Write(bc_1), run_time=0.8)
        self.play(Write(bc_2), run_time=0.8)
        self.wait(0.6)
        return formulas

    def show_2d_scene(self, theory_group: VGroup, evolution: ScatteringEvolution, system: PotentialStep):
        axes = Axes(
            x_range=[X_RANGE_2D[0], X_RANGE_2D[1], 1],
            y_range=[Y_RANGE[0], Y_RANGE[1], 1],
            x_length=X_LENGTH,
            y_length=Y_LENGTH,
            tips=True,
            axis_config={"include_numbers": False, "color": GREY_B},
        )
        axes.shift(DOWN * 0.35)

        x_label = MathTex("x", color=GREY_A).scale(0.8).next_to(axes.x_axis.get_end(), RIGHT, buff=0.15)
        potential_graph = self.build_2d_potential(axes, system)
        energy_height = POTENTIAL_SCALE * evolution.energy
        energy_line = DashedLine(
            axes.c2p(-5, energy_height),
            axes.c2p(5, energy_height),
            color=YELLOW,
            dash_length=0.15,
            stroke_opacity=0.75,
        )

        psi_2d = self.build_2d_wave(axes, evolution, t=0.0)
        left_hint = MathTex(r"E<U_0", color=YELLOW).scale(0.8).next_to(energy_line, UP, buff=0.2).shift(LEFT * 3.2)

        self.play(FadeOut(theory_group), run_time=0.7)
        self.play(Create(axes), FadeIn(x_label), run_time=0.8)
        self.play(Create(potential_graph), Create(energy_line), FadeIn(left_hint), run_time=0.9)
        self.play(Create(psi_2d), run_time=1.2)

        time = ValueTracker(0.0)
        animated_wave = always_redraw(lambda: self.build_2d_wave(axes, evolution, time.get_value()))
        self.remove(psi_2d)
        self.add(animated_wave)
        self.play(time.animate.set_value(6.0), run_time=4.0, rate_func=linear)
        self.wait(0.4)
        return axes, x_label, potential_graph, energy_line, animated_wave, left_hint

    def transition_to_3d(
        self,
        axes_2d: Axes,
        x_label_2d,
        potential_2d,
        energy_line,
        wave_2d,
        left_hint,
        evolution: ScatteringEvolution,
        system: PotentialStep,
    ) -> None:
        axes_3d = ThreeDAxes(
            x_range=[X_RANGE_3D[0], X_RANGE_3D[1], 1],
            y_range=[Y_RANGE[0], Y_RANGE[1], 1],
            z_range=[Z_RANGE[0], Z_RANGE[1], 1],
            x_length=X_LENGTH,
            y_length=Y_LENGTH,
            z_length=Z_LENGTH,
            axis_config={"include_numbers": False, "color": GREY_B},
        )
        axes_3d.shift(DOWN * 0.35)

        x_label = MathTex("x", color=GREY_A).scale(0.8).move_to(axes_3d.c2p(X_RANGE_3D[1] + 0.45, 0.0, 0.0))
        re_label = MathTex(r"\operatorname{Re}\psi", color=GREY_A).scale(0.7).move_to(
            axes_3d.c2p(0.0, Y_RANGE[1] - 0.1, -0.75)
        )
        im_label = MathTex(r"\operatorname{Im}\psi", color=GREY_A).scale(0.7).move_to(
            axes_3d.c2p(0.45, 0.25, Z_RANGE[1] - 0.55)
        )

        potential_3d = self.build_3d_potential(axes_3d, system)
        initial_3d_time = 6.4
        mid_3d_time = 8.6
        final_3d_time = 10.2
        wave_3d = self.build_3d_wave(axes_3d, evolution, t=initial_3d_time)

        self.set_camera_orientation(phi=0 * DEGREES, theta=-90 * DEGREES)
        self.add_fixed_orientation_mobjects(x_label, re_label, im_label)
        self.play(
            FadeOut(axes_2d),
            FadeOut(x_label_2d),
            FadeOut(potential_2d),
            FadeOut(energy_line),
            FadeOut(left_hint),
            FadeOut(wave_2d),
            FadeIn(axes_3d),
            FadeIn(potential_3d),
            FadeIn(wave_3d),
            FadeIn(x_label),
            run_time=1.2,
        )
        self.add(axes_3d, potential_3d, wave_3d)
        self.play(FadeIn(re_label), FadeIn(im_label), run_time=0.8)

        tracker = ValueTracker(initial_3d_time)
        animated_wave_3d = always_redraw(lambda: self.build_3d_wave(axes_3d, evolution, tracker.get_value()))
        self.remove(wave_3d)
        self.add(animated_wave_3d)

        self.play(tracker.animate.set_value(mid_3d_time), run_time=1.2, rate_func=linear)
        self.move_camera(
            phi=68 * DEGREES,
            theta=-122 * DEGREES,
            added_anims=[tracker.animate.set_value(final_3d_time)],
            run_time=3.5,
        )
        self.wait(0.5)

    def show_outro(self) -> None:
        thanks = Text("Спасибо за внимание", font_size=42, color=WHITE)
        shade = Rectangle(
            width=config.frame_width,
            height=config.frame_height,
            fill_color=BLACK,
            fill_opacity=0.0,
            stroke_opacity=0.0,
        )
        self.add(shade)
        scene_mobjects = Group(*[mob for mob in self.mobjects if mob is not shade])
        self.play(
            FadeOut(scene_mobjects, shift=DOWN * 0.05),
            shade.animate.set_fill(BLACK, opacity=0.97),
            run_time=1.0,
        )
        self.play(FadeIn(thanks, shift=UP * 0.15), run_time=1.0)
        self.wait(1.0)

    def build_2d_wave(self, axes: Axes, evolution: ScatteringEvolution, t: float):
        xs = self.x_values
        psi = evolution.psi(xs, t)
        line = VMobject(color=RED)
        points = [axes.c2p(float(x), float(np.real(value))) for x, value in zip(xs, psi)]
        line.set_points_smoothly(points)
        line.set_stroke(width=4)
        return line

    def build_2d_potential(self, axes: Axes, system: PotentialStep):
        xs = self.x_values
        values = POTENTIAL_SCALE * system.potential(xs)
        line = VMobject(color=GREEN)
        points = [axes.c2p(float(x), float(y)) for x, y in zip(xs, values)]
        line.set_points_as_corners(points)
        line.set_stroke(width=4)
        return line

    def build_3d_wave(self, axes: ThreeDAxes, evolution: ScatteringEvolution, t: float):
        xs = self.x_values_3d
        psi = evolution.psi(xs, t)
        return axes.plot_line_graph(
            x_values=xs,
            y_values=np.real(psi),
            z_values=np.imag(psi),
            line_color=RED,
            add_vertex_dots=False,
            stroke_width=5,
        )

    def build_3d_potential(self, axes: ThreeDAxes, system: PotentialStep):
        xs = self.x_values_3d
        values = POTENTIAL_SCALE * system.potential(xs)
        return axes.plot_line_graph(
            x_values=xs,
            y_values=values,
            z_values=np.zeros_like(xs),
            line_color=GREEN,
            add_vertex_dots=False,
            stroke_width=5,
        )
