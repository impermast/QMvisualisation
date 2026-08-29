"""QuantumState — начальные состояния ψ(x, t=0), независимо от Manim."""

from __future__ import annotations

from typing import Any, Dict

import numpy as np


class GaussianState:
    """Гауссовский волновой пакет в момент t=0."""

    def __init__(self, x0: float = 0.0, p0: float = 0.0, sigma: float = 1.0):
        self.name = "Gaussian wave packet"
        self.description = (
            "Minimum-uncertainty state with given mean position, momentum, and width."
        )
        self.x0 = x0
        self.p0 = p0
        self.sigma = sigma
        self.parameters: Dict[str, Any] = {"x0": x0, "p0": p0, "sigma": sigma}
        self.latex: Dict[str, str] = {
            "wavefunction": (
                r"\psi(x,0) = \frac{1}{(2\pi\sigma^2)^{1/4}} "
                r"\exp\!\left[-\frac{(x-x_0)^2}{4\sigma^2} + \frac{i}{\hbar}p_0 x\right]"
            )
        }

    def psi(self, x: np.ndarray) -> np.ndarray:
        norm = (2 * np.pi * self.sigma**2) ** (-0.25)
        envelope = np.exp(-((x - self.x0) ** 2) / (4 * self.sigma**2))
        phase = np.exp(1j * self.p0 * x)
        return norm * envelope * phase


class PlaneWaveState:
    """Падающая слева плоская волна единичной амплитуды."""

    def __init__(self, k: float, mass: float = 1.0):
        if k <= 0:
            raise ValueError("k must be positive for left-to-right scattering.")

        self.name = "Plane wave"
        self.description = "Stationary plane wave incident from the left."
        self.k = float(k)
        self.mass = float(mass)
        self.energy = self.k**2 / (2 * self.mass)
        self.parameters: Dict[str, Any] = {
            "k": self.k,
            "mass": self.mass,
            "energy": self.energy,
        }
        self.latex: Dict[str, str] = {
            "wavefunction": r"\psi_{in}(x,t)=e^{i(kx-Et)}",
            "energy": r"E=\frac{\hbar^2 k^2}{2m}",
        }

    def psi(self, x: np.ndarray) -> np.ndarray:
        return np.exp(1j * self.k * x)