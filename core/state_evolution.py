"""StateEvolution — аналитическая эволюция и стационарное рассеяние."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np

from .quantum_state import GaussianState, PlaneWaveState
from .quantum_system import FreeParticleSystem, PotentialBarrier, PotentialStep


class FreeParticleEvolution:
    """Аналитическая временная эволюция GaussianState в FreeParticleSystem."""

    def __init__(self, state: GaussianState, system: FreeParticleSystem):
        self.state = state
        self.system = system

    def psi(self, x: np.ndarray, t: float) -> np.ndarray:
        m = self.system.mass
        x0 = self.state.x0
        p0 = self.state.p0
        sigma = self.state.sigma
        s = sigma**2 + 1j * t / m
        norm = (2 * np.pi * s) ** (-0.25)
        xc = x0 + p0 * t / m
        envelope = np.exp(-((x - xc) ** 2) / (4 * s))
        phase = np.exp(1j * (p0 * x - 0.5 * p0**2 * t / m))
        return norm * envelope * phase


@dataclass(frozen=True)
class RegionSolution:
    left: float | None
    right: float | None
    potential: float
    k: complex
    c_plus: complex
    c_minus: complex


class ScatteringEvolution:
    """Стационарное рассеяние плоской волны на кусочно-постоянном потенциале."""

    def __init__(self, state: PlaneWaveState, system: PotentialStep | PotentialBarrier):
        self.state = state
        self.system = system
        self.mass = getattr(system, "mass", state.mass)
        self.energy = state.energy
        self._regions = self._build_region_solutions()
        self.reflection_amplitude = self._regions[0].c_minus
        self.transmission_amplitude = self._regions[-1].c_plus
        self.reflection_probability = abs(self.reflection_amplitude) ** 2
        transmitted_k = self._regions[-1].k
        if abs(transmitted_k.real) > 1e-10:
            self.transmission_probability = (
                transmitted_k.real / self._regions[0].k.real
            ) * abs(self.transmission_amplitude) ** 2
        else:
            self.transmission_probability = 0.0

    def _wave_number(self, potential: float) -> complex:
        return np.sqrt(2 * self.mass * (self.energy - potential) + 0j)

    def _build_linear_system(self) -> tuple[np.ndarray, np.ndarray, list[tuple[float | None, float | None, float]]]:
        regions = self.system.regions()
        n = len(regions)
        matrix = np.zeros((2 * n, 2 * n), dtype=complex)
        vector = np.zeros(2 * n, dtype=complex)
        ks = [self._wave_number(region[2]) for region in regions]

        matrix[0, 0] = 1.0
        vector[0] = 1.0
        matrix[1, 2 * (n - 1) + 1] = 1.0
        vector[1] = 0.0

        row = 2
        for boundary_index in range(n - 1):
            boundary = regions[boundary_index][1]
            left_k = ks[boundary_index]
            right_k = ks[boundary_index + 1]
            left_plus = 2 * boundary_index
            left_minus = left_plus + 1
            right_plus = left_plus + 2
            right_minus = left_plus + 3

            left_phase_plus = np.exp(1j * left_k * boundary)
            left_phase_minus = np.exp(-1j * left_k * boundary)
            right_phase_plus = np.exp(1j * right_k * boundary)
            right_phase_minus = np.exp(-1j * right_k * boundary)

            matrix[row, left_plus] = left_phase_plus
            matrix[row, left_minus] = left_phase_minus
            matrix[row, right_plus] = -right_phase_plus
            matrix[row, right_minus] = -right_phase_minus
            row += 1

            matrix[row, left_plus] = 1j * left_k * left_phase_plus
            matrix[row, left_minus] = -1j * left_k * left_phase_minus
            matrix[row, right_plus] = -1j * right_k * right_phase_plus
            matrix[row, right_minus] = 1j * right_k * right_phase_minus
            row += 1

        return matrix, vector, regions

    def _build_region_solutions(self) -> list[RegionSolution]:
        matrix, vector, regions = self._build_linear_system()
        coeffs = np.linalg.solve(matrix, vector)
        solutions: list[RegionSolution] = []
        for index, (left, right, potential) in enumerate(regions):
            solutions.append(
                RegionSolution(
                    left=left,
                    right=right,
                    potential=potential,
                    k=self._wave_number(potential),
                    c_plus=coeffs[2 * index],
                    c_minus=coeffs[2 * index + 1],
                )
            )
        return solutions

    @property
    def regions(self) -> list[RegionSolution]:
        return self._regions

    def psi_stationary(self, x: np.ndarray) -> np.ndarray:
        x_arr = np.asarray(x, dtype=float)
        psi = np.zeros_like(x_arr, dtype=complex)
        for region in self._regions:
            left_ok = np.ones_like(x_arr, dtype=bool) if region.left is None else x_arr >= region.left
            right_ok = np.ones_like(x_arr, dtype=bool) if region.right is None else x_arr <= region.right
            mask = left_ok & right_ok
            if not np.any(mask):
                continue
            x_region = x_arr[mask]
            psi[mask] = (
                region.c_plus * np.exp(1j * region.k * x_region)
                + region.c_minus * np.exp(-1j * region.k * x_region)
            )
        return psi

    def psi(self, x: np.ndarray, t: float) -> np.ndarray:
        return self.psi_stationary(x) * np.exp(-1j * self.energy * t)

    def probability_current_coefficients(self) -> dict[str, Any]:
        return {
            "R": self.reflection_probability,
            "T": self.transmission_probability,
            "R_amp": self.reflection_amplitude,
            "T_amp": self.transmission_amplitude,
            "energy": self.energy,
        }