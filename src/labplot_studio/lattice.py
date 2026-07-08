from __future__ import annotations

import math
from dataclasses import dataclass


CU_K_ALPHA_ANGSTROM = 1.5406


@dataclass
class IndexedPeak:
    two_theta: float
    h: int
    k: int
    l: int


@dataclass
class LatticeFitResult:
    a: float
    c: float
    intercept: float
    coefficients: tuple[float, float, float]


def fit_hexagonal_lattice(
    peaks: list[IndexedPeak],
    wavelength: float = CU_K_ALPHA_ANGSTROM,
) -> LatticeFitResult:
    """Fit hexagonal lattice constants using the Igor-style correction terms.

    This follows the structure visible in the supplied XRD instruction:

    z = A x + B y + C

    where z is sin(theta), and x/y contain hkl and correction terms.
    """
    if len(peaks) < 3:
        raise ValueError("At least three indexed peaks are required")

    rows: list[tuple[float, float, float]] = []
    targets: list[float] = []
    for peak in peaks:
        theta = math.radians(peak.two_theta / 2.0)
        sin_t = math.sin(theta)
        cos_t = math.cos(theta)
        if sin_t == 0 or cos_t == 0:
            continue
        x_term = (peak.h * peak.h + peak.h * peak.k + peak.k * peak.k) * wavelength * wavelength / (
            6.0 * sin_t * cos_t * cos_t
        )
        y_term = peak.l * peak.l * wavelength * wavelength / (8.0 * sin_t * cos_t * cos_t)
        rows.append((x_term, y_term, 1.0))
        targets.append(sin_t)

    if len(rows) < 3:
        raise ValueError("At least three valid peaks are required")

    a_coef, c_coef, intercept = _least_squares_3(rows, targets)
    if a_coef <= 0 or c_coef <= 0:
        raise ValueError("Fit did not produce positive lattice coefficients")
    return LatticeFitResult(
        a=math.sqrt(1.0 / a_coef),
        c=math.sqrt(1.0 / c_coef),
        intercept=intercept,
        coefficients=(a_coef, c_coef, intercept),
    )


def _least_squares_3(rows: list[tuple[float, float, float]], targets: list[float]) -> tuple[float, float, float]:
    ata = [[0.0, 0.0, 0.0] for _ in range(3)]
    atb = [0.0, 0.0, 0.0]
    for row, target in zip(rows, targets):
        for i in range(3):
            atb[i] += row[i] * target
            for j in range(3):
                ata[i][j] += row[i] * row[j]
    return _solve_3x3(ata, atb)


def _solve_3x3(matrix: list[list[float]], vector: list[float]) -> tuple[float, float, float]:
    a = [row[:] + [value] for row, value in zip(matrix, vector)]
    for col in range(3):
        pivot = max(range(col, 3), key=lambda row: abs(a[row][col]))
        if abs(a[pivot][col]) < 1e-12:
            raise ValueError("Singular fit matrix")
        a[col], a[pivot] = a[pivot], a[col]
        scale = a[col][col]
        for j in range(col, 4):
            a[col][j] /= scale
        for row in range(3):
            if row == col:
                continue
            factor = a[row][col]
            for j in range(col, 4):
                a[row][j] -= factor * a[col][j]
    return a[0][3], a[1][3], a[2][3]

