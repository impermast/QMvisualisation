"""QuantumSystem — гамильтониан / потенциал, независимо от Manim."""

from __future__ import annotations
from typing import Dict, Any
import numpy as np


class FreeParticleSystem:
    """Свободная частица: V(x) = 0 всюду.

    Масса — явный атрибут (не приравнивается к 1).
    ħ = c = 1, но m задаётся пользователем.
    """

    def __init__(self, mass: float = 1.0):
        self.name = "Free particle"
        self.description = "A particle in zero external potential (V = 0)."
        # Физически значимый атрибут
        self.mass = mass
        # Метаданные
        self.parameters: Dict[str, Any] = {"mass": mass}
        self.latex: Dict[str, str] = {
            "potential": r"V(x) = 0",
            "hamiltonian": r"\hat H = \frac{\hat p^2}{2m}",
        }

    def potential(self, x: np.ndarray, t: float = 0.0) -> np.ndarray:
        """Потенциальная энергия V(x, t).

        Для свободной частицы V ≡ 0.
        """
        return np.zeros_like(x, dtype=float)


class PotentialStep:
    """Потенциальная ступенька: V=0 при x<x0 и V=U0 при x>=x0."""

    def __init__(self, U0: float, x0: float = 0.0, mass: float = 1.0):
        self.name = "Potential step"
        self.description = "A single discontinuity in the potential energy."
        self.U0 = float(U0)
        self.x0 = float(x0)
        self.mass = float(mass)
        self.parameters: Dict[str, Any] = {"U0": self.U0, "x0": self.x0, "mass": self.mass}
        self.latex: Dict[str, str] = {
            "potential": r"V(x)=\begin{cases}0,&x<x_0\\U_0,&x\ge x_0\end{cases}",
        }

    def potential(self, x: np.ndarray, t: float = 0.0) -> np.ndarray:
        x_arr = np.asarray(x, dtype=float)
        return np.where(x_arr < self.x0, 0.0, self.U0)

    def regions(self) -> list[tuple[float | None, float | None, float]]:
        return [(None, self.x0, 0.0), (self.x0, None, self.U0)]


class PotentialBarrier:
    """Прямоугольный барьер: V=U0 на участке [x0, x0+a]."""

    def __init__(self, U0: float, a: float, x0: float = 0.0, mass: float = 1.0):
        if a <= 0:
            raise ValueError("Barrier width a must be positive.")

        self.name = "Potential barrier"
        self.description = "A finite rectangular barrier."
        self.U0 = float(U0)
        self.a = float(a)
        self.x0 = float(x0)
        self.mass = float(mass)
        self.parameters: Dict[str, Any] = {
            "U0": self.U0,
            "a": self.a,
            "x0": self.x0,
            "mass": self.mass,
        }
        self.latex: Dict[str, str] = {
            "potential": (
                r"V(x)=\begin{cases}0,&x<x_0\\U_0,&x_0\le x\le x_0+a\\0,&x>x_0+a\end{cases}"
            ),
        }

    def potential(self, x: np.ndarray, t: float = 0.0) -> np.ndarray:
        x_arr = np.asarray(x, dtype=float)
        inside = (x_arr >= self.x0) & (x_arr <= self.x0 + self.a)
        return np.where(inside, self.U0, 0.0)

    def regions(self) -> list[tuple[float | None, float | None, float]]:
        return [(None, self.x0, 0.0), (self.x0, self.x0 + self.a, self.U0), (self.x0 + self.a, None, 0.0)]