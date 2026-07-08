from __future__ import annotations

from dataclasses import dataclass

from .models import MeasuredSeries, ReferencePhase
from .xrd import normalize_measured


@dataclass
class PeakMatch:
    measured_two_theta: float
    measured_intensity: float
    phase_name: str
    reference_two_theta: float
    reference_intensity: float
    delta: float
    hkl: str
    color: str


@dataclass
class PhaseCandidate:
    phase_name: str
    score: float
    matched_peak_count: int
    expected_peak_count: int
    main_peak_found: bool
    main_peak_two_theta: float
    color: str


def find_measured_peaks(
    series: MeasuredSeries,
    x_min: float,
    x_max: float,
    min_intensity: float = 8.0,
    window: int = 4,
) -> list[tuple[float, float]]:
    normalize_measured(series, x_min, x_max)
    peaks: list[tuple[float, float]] = []
    xs = series.x
    ys = series.normalized_y
    for index in range(window, len(xs) - window):
        x = xs[index]
        y = ys[index]
        if x < x_min or x > x_max or y < min_intensity:
            continue
        left = ys[index - window:index]
        right = ys[index + 1:index + window + 1]
        if all(y >= value for value in left) and all(y > value for value in right):
            peaks.append((x, y))
    return _thin_close_peaks(peaks, min_separation=0.12)


def match_reference_peaks(
    measured_peaks: list[tuple[float, float]],
    phases: list[ReferencePhase],
    tolerance: float,
    min_reference_intensity: float = 0.0,
) -> list[PeakMatch]:
    matches: list[PeakMatch] = []
    for measured_x, measured_y in measured_peaks:
        for phase in phases:
            for peak in phase.peaks:
                if peak.intensity < min_reference_intensity:
                    continue
                delta = measured_x - peak.two_theta
                if abs(delta) <= tolerance:
                    matches.append(
                        PeakMatch(
                            measured_two_theta=measured_x,
                            measured_intensity=measured_y,
                            phase_name=phase.label,
                            reference_two_theta=peak.two_theta,
                            reference_intensity=peak.intensity,
                            delta=delta,
                            hkl=peak.hkl_label,
                            color=phase.color,
                        )
                    )
    matches.sort(key=lambda match: (match.measured_two_theta, abs(match.delta), -match.reference_intensity))
    return matches


def rank_candidate_phases(
    measured_peaks: list[tuple[float, float]],
    phases: list[ReferencePhase],
    tolerance: float,
    min_reference_intensity: float = 8.0,
) -> list[PhaseCandidate]:
    candidates: list[PhaseCandidate] = []
    for phase in phases:
        expected = [peak for peak in phase.peaks if peak.intensity >= min_reference_intensity]
        if not expected:
            continue
        main_peak = max(phase.peaks, key=lambda peak: peak.intensity)
        matched = []
        for peak in expected:
            best_delta = _nearest_peak_delta(measured_peaks, peak.two_theta)
            if best_delta is not None and abs(best_delta) <= tolerance:
                matched.append(peak)
        main_delta = _nearest_peak_delta(measured_peaks, main_peak.two_theta)
        main_found = main_delta is not None and abs(main_delta) <= tolerance
        matched_weight = sum(peak.intensity for peak in matched)
        expected_weight = sum(peak.intensity for peak in expected)
        score = 100.0 * matched_weight / expected_weight if expected_weight else 0.0
        if not main_found:
            score *= 0.25
        missing_strong = [peak for peak in expected if peak.intensity >= 50 and peak not in matched]
        score -= 8.0 * len(missing_strong)
        candidates.append(
            PhaseCandidate(
                phase_name=phase.label,
                score=max(score, 0.0),
                matched_peak_count=len(matched),
                expected_peak_count=len(expected),
                main_peak_found=main_found,
                main_peak_two_theta=main_peak.two_theta,
                color=phase.color,
            )
        )
    candidates.sort(key=lambda item: item.score, reverse=True)
    return candidates


def _thin_close_peaks(peaks: list[tuple[float, float]], min_separation: float) -> list[tuple[float, float]]:
    selected: list[tuple[float, float]] = []
    for x, y in sorted(peaks, key=lambda item: item[1], reverse=True):
        if all(abs(x - sx) >= min_separation for sx, _sy in selected):
            selected.append((x, y))
    return sorted(selected)


def _nearest_peak_delta(measured_peaks: list[tuple[float, float]], reference_two_theta: float) -> float | None:
    if not measured_peaks:
        return None
    nearest = min(measured_peaks, key=lambda item: abs(item[0] - reference_two_theta))
    return nearest[0] - reference_two_theta
