"""Visual objects — Manim-объекты для отображения физических сущностей."""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
from manim import *

if TYPE_CHECKING:
    from core.state_evolution import FreeParticleEvolution, ScatteringEvolution
    from core.quantum_system import PotentialBarrier, PotentialStep


class ProbabilityDensity1D(VGroup):
    """Визуализация |ψ(x,t)|² на одних осях."""

    def __init__(
        self,
        axes: Axes,
        evolution: FreeParticleEvolution,
        color: str = BLUE,
        stroke_width: float = 4.0,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.axes = axes
        self.evolution = evolution
        self.color = color
        self.stroke_width = stroke_width
        x_min, x_max = axes.x_range[:2]
        self._x_vals = np.linspace(x_min, x_max, 1000)
        self.graph: ParametricFunction = self._build_graph(0.0)
        self.add(self.graph)

    def _build_graph(self, t: float) -> ParametricFunction:
        psi = self.evolution.psi(self._x_vals, t)
        density = np.abs(psi) ** 2
        graph = self.axes.plot(
            lambda xi: float(np.interp(xi, self._x_vals, density)),
            color=self.color,
            use_smoothing=False,
        )
        graph.set_stroke(width=self.stroke_width)
        return graph

    def update_t(self, t: float) -> None:
        self.graph.become(self._build_graph(t))


class WaveFunction3D(VGroup):
    """3D-визуализация x, Re(psi), Im(psi) для стационарного рассеяния."""

    def __init__(
        self,
        axes: ThreeDAxes,
        evolution: ScatteringEvolution,
        x_range: tuple[float, float] = (-5.0, 5.0),
        samples: int = 300,
        color: str = RED,
        stroke_width: float = 4.0,
        add_vertex_dots: bool = False,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.axes = axes
        self.evolution = evolution
        self.x_range = x_range
        self.samples = samples
        self.color = color
        self.stroke_width = stroke_width
        self.add_vertex_dots = add_vertex_dots
        self._x_vals = np.linspace(x_range[0], x_range[1], samples)
        self.graph = self._build_graph(0.0)
        self.add(self.graph)

    def _build_graph(self, t: float):
        psi = self.evolution.psi(self._x_vals, t)
        return self.axes.plot_line_graph(
            x_values=self._x_vals,
            y_values=np.real(psi),
            z_values=np.imag(psi),
            line_color=self.color,
            add_vertex_dots=self.add_vertex_dots,
            stroke_width=self.stroke_width,
        )

    def update_t(self, t: float) -> None:
        self.graph.become(self._build_graph(t))


class PotentialCurve3D(VGroup):
    """Потенциал как линия в плоскости z=0."""

    def __init__(
        self,
        axes: ThreeDAxes,
        system: PotentialStep | PotentialBarrier,
        x_range: tuple[float, float] = (-5.0, 5.0),
        samples: int = 300,
        color: str = GREEN,
        stroke_width: float = 6.0,
        scale_factor: float = 1.0,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.axes = axes
        self.system = system
        self.x_range = x_range
        self.samples = samples
        self.color = color
        self.stroke_width = stroke_width
        self.scale_factor = scale_factor
        self._x_vals = np.linspace(x_range[0], x_range[1], samples)
        self.graph = self._build_graph()
        self.add(self.graph)

    def _build_graph(self):
        potential = self.system.potential(self._x_vals) * self.scale_factor
        return self.axes.plot_line_graph(
            x_values=self._x_vals,
            y_values=potential,
            z_values=np.zeros_like(self._x_vals),
            line_color=self.color,
            add_vertex_dots=False,
            stroke_width=self.stroke_width,
        )