from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class MeasuredSeries:
    path: Path
    name: str
    x: list[float]
    y: list[float]
    normalized_y: list[float] = field(default_factory=list)


@dataclass
class ReferencePeak:
    two_theta: float
    intensity: float
    h: int | None = None
    k: int | None = None
    l: int | None = None
    d_spacing: float | None = None

    @property
    def hkl_label(self) -> str:
        if self.h is None or self.k is None or self.l is None:
            return ""
        return f"{self.h}{self.k}{self.l}"


@dataclass
class ReferencePhase:
    path: Path
    name: str
    peaks: list[ReferencePeak]
    color: str = "#d14a28"
    display_name: str = ""
    marker: str = "circle"
    hidden_peak_keys: set[str] = field(default_factory=set)

    @property
    def label(self) -> str:
        return self.display_name or self.name

    def peak_key(self, peak: ReferencePeak) -> str:
        return f"{peak.two_theta:.4f}|{peak.hkl_label}"

    def visible_peaks(self) -> list[ReferencePeak]:
        return [peak for peak in self.peaks if self.peak_key(peak) not in self.hidden_peak_keys]
