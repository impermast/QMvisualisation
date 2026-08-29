"""Semantic animations — Manim-анимации с физическим смыслом."""

from __future__ import annotations
from typing import Callable, Protocol, TYPE_CHECKING

from manim import *

if TYPE_CHECKING:
    from core.state_evolution import FreeParticleEvolution, ScatteringEvolution


class TimeUpdatable(Protocol):
    def update_t(self, t: float) -> None: ...


class EvolveState(Animation):
    """Анимирует временную эволюцию объекта с методом update_t.

    На каждом кадре вызывает evolution.psi(x, t) и обновляет
    отображение плотности вероятности.
    """

    def __init__(
        self,
        mobject: TimeUpdatable,
        evolution: FreeParticleEvolution | ScatteringEvolution,
        t_range: tuple[float, float] = (0.0, 5.0),
        rate_func: Callable[[float], float] = linear,
        **kwargs,
    ):
        super().__init__(mobject, **kwargs)
        self._evolution = evolution
        self._t_min, self._t_max = t_range
        self._rate_func = rate_func

    def interpolate(self, alpha: float) -> None:
        t = interpolate(self._t_min, self._t_max, self._rate_func(alpha))
        self.mobject.update_t(t)