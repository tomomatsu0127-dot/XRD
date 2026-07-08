from __future__ import annotations

from .models import MeasuredSeries, ReferencePeak, ReferencePhase


def normalize(values: list[float], subtract_min: bool = True) -> list[float]:
    if not values:
        return []
    min_value = min(values) if subtract_min else 0.0
    shifted = [value - min_value for value in values]
    max_value = max(shifted) if shifted else 0.0
    if max_value == 0:
        return [0.0 for _ in shifted]
    return [100.0 * value / max_value for value in shifted]


def normalize_measured(series: MeasuredSeries, x_min: float | None = None, x_max: float | None = None) -> MeasuredSeries:
    selected = [
        y for x, y in zip(series.x, series.y)
        if (x_min is None or x >= x_min) and (x_max is None or x <= x_max)
    ]
    if not selected:
        series.normalized_y = normalize(series.y)
        return series
    min_value = min(selected)
    max_value = max(value - min_value for value in selected)
    if max_value == 0:
        series.normalized_y = [0.0 for _ in series.y]
        return series
    series.normalized_y = [100.0 * (value - min_value) / max_value for value in series.y]
    return series


def normalize_reference_phase(phase: ReferencePhase) -> ReferencePhase:
    max_i = max((peak.intensity for peak in phase.peaks), default=0.0)
    if max_i <= 0:
        return phase
    for peak in phase.peaks:
        peak.intensity = 100.0 * peak.intensity / max_i
    return phase


def orientation_matches(peak: ReferencePeak, mode: str) -> bool:
    if mode == "all":
        return True
    if peak.h is None or peak.k is None or peak.l is None:
        return False
    h, k, l = peak.h, peak.k, peak.l
    if mode == "h00":
        return h != 0 and k == 0 and l == 0
    if mode == "0k0":
        return h == 0 and k != 0 and l == 0
    if mode == "00l":
        return h == 0 and k == 0 and l != 0
    if mode == "hk0":
        return h != 0 and k != 0 and l == 0
    if mode == "h0l":
        return h != 0 and k == 0 and l != 0
    if mode == "0kl":
        return h == 0 and k != 0 and l != 0
    return True

