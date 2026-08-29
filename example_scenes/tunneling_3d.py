"""MVP-сцены для туннелирования и рассеяния на ступеньке/барьере."""

from __future__ import annotations

from manim import *

from animation.semantic import EvolveState
from core.quantum_state import PlaneWaveState
from core.quantum_system import PotentialBarrier, PotentialStep
from core.state_evolution import ScatteringEvolution
from visual.objects import PotentialCurve3D, WaveFunction3D


class BaseScatteringScene(ThreeDScene):
    scene_title = "Scattering MVP"
    x_range = (-5.0, 5.0)
    y_range = (-2.5, 3.5)
    z_range = (-2.5, 2.5)
    samples = 320
    evolution_time = 8.0

    def build_system(self):
        raise NotImplementedError

    def build_state(self):
        raise NotImplementedError

    def create_axes(self) -> ThreeDAxes:
        axes = ThreeDAxes(
            x_range=[self.x_range[0], self.x_range[1], 1],
            y_range=[self.y_range[0], self.y_range[1], 1],
            z_range=[self.z_range[0], self.z_range[1], 1],
            axis_config={"include_numbers": True, "font_size": 24},
        )
        return axes

    def create_labels(self):
        x_label = Text("x", font_size=28)
        re_label = Text("Re(psi)", font_size=28)
        im_label = Text("Im(psi)", font_size=28)
        return x_label, re_label, im_label

    def build_summary(self, evolution: ScatteringEvolution) -> VGroup:
        relation = "E > U0" if evolution.energy > self.system.U0 else "E < U0"
        lines = VGroup(
            Text(self.scene_title, font_size=34),
            Text(f"{relation}; E={evolution.energy:.2f}; U0={self.system.U0:.2f}", font_size=24),
            Text(
                f"|R|^2={evolution.reflection_probability:.3f}; |T|^2={evolution.transmission_probability:.3f}",
                font_size=24,
            ),
        ).arrange(DOWN, aligned_edge=LEFT)
        lines.to_corner(UL)
        return lines

    def construct(self):
        self.system = self.build_system()
        state = self.build_state()
        evolution = ScatteringEvolution(state, self.system)

        axes = self.create_axes()
        x_label, re_label, im_label = self.create_labels()
        x_label.next_to(axes.x_axis.get_end(), RIGHT)
        re_label.next_to(axes.y_axis.get_end(), UP)
        im_label.next_to(axes.z_axis.get_end(), UP)

        summary = self.build_summary(evolution)
        wave = WaveFunction3D(
            axes=axes,
            evolution=evolution,
            x_range=self.x_range,
            samples=self.samples,
            color=RED,
            stroke_width=5.0,
        )
        potential = PotentialCurve3D(
            axes=axes,
            system=self.system,
            x_range=self.x_range,
            samples=self.samples,
            scale_factor=1.0,
            color=GREEN,
            stroke_width=6.0,
        )

        self.set_camera_orientation(phi=0 * DEGREES, theta=-90 * DEGREES)
        self.play(FadeIn(summary), Create(axes), FadeIn(x_label), FadeIn(re_label), FadeIn(im_label), run_time=1.5)
        self.play(FadeIn(potential), FadeIn(wave), run_time=1.0)

        evolve = EvolveState(wave, evolution=evolution, t_range=(0.0, self.evolution_time), rate_func=linear)
        self.play(evolve, run_time=4.0)
        self.move_camera(phi=72 * DEGREES, theta=-120 * DEGREES, run_time=3.0)
        self.play(evolve, run_time=4.0)
        self.wait(0.5)


class BarrierBelowU0(BaseScatteringScene):
    scene_title = "Barrier tunneling: E < U0"

    def build_system(self):
        return PotentialBarrier(U0=3.0, a=2.0, x0=0.0, mass=1.0)

    def build_state(self):
        return PlaneWaveState(k=2.0, mass=1.0)


class BarrierAboveU0(BaseScatteringScene):
    scene_title = "Barrier scattering: E > U0"

    def build_system(self):
        return PotentialBarrier(U0=2.0, a=2.0, x0=0.0, mass=1.0)

    def build_state(self):
        return PlaneWaveState(k=3.0, mass=1.0)


class StepBelowU0(BaseScatteringScene):
    scene_title = "Step tunneling tail: E < U0"

    def build_system(self):
        return PotentialStep(U0=3.0, x0=0.0, mass=1.0)

    def build_state(self):
        return PlaneWaveState(k=2.0, mass=1.0)


class StepAboveU0(BaseScatteringScene):
    scene_title = "Step scattering: E > U0"

    def build_system(self):
        return PotentialStep(U0=2.0, x0=0.0, mass=1.0)

    def build_state(self):
        return PlaneWaveState(k=3.0, mass=1.0)