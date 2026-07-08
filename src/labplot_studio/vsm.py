from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .parsers import _split_numeric_line


@dataclass
class VsmSeries:
    path: Path
    name: str
    field_koe: list[float]
    magnetization_emu_g: list[float]
    mass_g: float


def parse_vsm_file(
    path: str | Path,
    sample_name: str | None = None,
    mass_g: float = 1.0,
    first_data_line: int = 42,
    field_column: int = 2,
    magnetization_column: int = 3,
) -> VsmSeries:
    """Parse the common VSM text layout described in the lab PDF.

    Line numbers and columns are 1-based to match the laboratory instruction.
    """
    file_path = Path(path)
    if mass_g <= 0:
        raise ValueError("mass_g must be positive")

    field_koe: list[float] = []
    magnetization_emu_g: list[float] = []

    lines = file_path.read_text(encoding="utf-8", errors="ignore").splitlines()
    for line in lines[first_data_line - 1:]:
        values = _split_numeric_line(line)
        if len(values) < max(field_column, magnetization_column):
            continue
        field_oe = values[field_column - 1]
        magnetization_emu = values[magnetization_column - 1]
        field_koe.append(field_oe / 1000.0)
        magnetization_emu_g.append(magnetization_emu / mass_g)

    if not field_koe:
        raise ValueError(f"No VSM data points were found in {file_path.name}")

    return VsmSeries(
        path=file_path,
        name=sample_name or file_path.stem,
        field_koe=field_koe,
        magnetization_emu_g=magnetization_emu_g,
        mass_g=mass_g,
    )


def estimate_hysteresis(series: VsmSeries) -> dict[str, float]:
    max_m = max(series.magnetization_emu_g)
    min_m = min(series.magnetization_emu_g)
    remanence = _interpolate_at_x(series.field_koe, series.magnetization_emu_g, 0.0)
    coercivity = _interpolate_zero_crossing(series.field_koe, series.magnetization_emu_g)
    return {
        "m_max_emu_g": max_m,
        "m_min_emu_g": min_m,
        "m_remanence_emu_g": remanence,
        "h_coercivity_koe": coercivity,
    }


def _interpolate_at_x(xs: list[float], ys: list[float], target_x: float) -> float:
    for x0, x1, y0, y1 in zip(xs, xs[1:], ys, ys[1:]):
        if (x0 <= target_x <= x1) or (x1 <= target_x <= x0):
            if x1 == x0:
                return y0
            ratio = (target_x - x0) / (x1 - x0)
            return y0 + ratio * (y1 - y0)
    return ys[min(range(len(xs)), key=lambda i: abs(xs[i] - target_x))]


def _interpolate_zero_crossing(xs: list[float], ys: list[float]) -> float:
    candidates: list[float] = []
    for x0, x1, y0, y1 in zip(xs, xs[1:], ys, ys[1:]):
        if y0 == 0:
            candidates.append(x0)
        elif (y0 < 0 < y1) or (y1 < 0 < y0):
            ratio = -y0 / (y1 - y0)
            candidates.append(x0 + ratio * (x1 - x0))
    if not candidates:
        return 0.0
    return min(candidates, key=abs)

