"""Пример: свободный гауссовский волновой пакет.

Демонстрирует вертикальный срез нового ядра:
    GaussianState + FreeParticleSystem
    → FreeParticleEvolution
    → ProbabilityDensity1D
    → EvolveState
"""

from manim import *

from core.quantum_state import GaussianState
from core.quantum_system import FreeParticleSystem
from core.state_evolution import FreeParticleEvolution
from visual.objects import ProbabilityDensity1D
from animation.semantic import EvolveState


class FreeGaussianPacket(Scene):
    def construct(self):
        # 1. Физика
        state = GaussianState(x0=-2.0, p0=0.8, sigma=0.4)
        system = FreeParticleSystem(mass=1.0)
        evolution = FreeParticleEvolution(state, system)

        # 2. Оси
        ax = Axes(
            x_range=[-8, 8, 2],
            y_range=[0, 0.8, 0.2],
            x_length=10,
            y_length=5,
            tips=False,
            axis_config={"include_numbers": True},
        )
        x_label = MathTex("x").next_to(ax.x_axis, RIGHT, buff=0.2)
        y_label = MathTex(r"|\psi|^2").next_to(ax.y_axis, UP, buff=0.2)

        # 3. Визуальный объект
        prob_density = ProbabilityDensity1D(ax, evolution, color=BLUE)

        # 4. Семантическая анимация
        evolve_anim = EvolveState(
            mobject=prob_density,
            evolution=evolution,
            t_range=(0.0, 4.0),
            rate_func=linear,
        )

        # 5. Сцена
        self.play(
            Create(ax),
            FadeIn(x_label),
            FadeIn(y_label),
            FadeIn(prob_density),
            run_time=1,
        )
        self.play(evolve_anim, run_time=4)
        self.wait(1)