from __future__ import annotations

import csv
import re
from pathlib import Path

from .models import MeasuredSeries, ReferencePeak, ReferencePhase


NUMBER_RE = re.compile(r"[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?")


def _split_numeric_line(line: str) -> list[float]:
    if "," in line:
        row = next(csv.reader([line]))
        values: list[float] = []
        for cell in row:
            try:
                values.append(float(cell.strip()))
            except ValueError:
                pass
        return values
    return [float(match.group(0)) for match in NUMBER_RE.finditer(line)]


def parse_measured_file(path: str | Path) -> MeasuredSeries:
    file_path = Path(path)
    x: list[float] = []
    y: list[float] = []
    for raw_line in file_path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw_line.strip()
        if not line or line.startswith(("#", "//", ";")):
            continue
        values = _split_numeric_line(line)
        if len(values) < 2:
            continue
        x.append(values[0])
        y.append(values[1])
    if not x:
        raise ValueError(f"No measured data points were found in {file_path.name}")
    return MeasuredSeries(path=file_path, name=file_path.stem, x=x, y=y)


def parse_reference_file(path: str | Path, color: str = "#d14a28") -> ReferencePhase:
    file_path = Path(path)
    peaks: list[ReferencePeak] = []
    header: list[str] | None = None
    for raw_line in file_path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw_line.strip()
        if not line or line.startswith(("#", "//", ";")):
            continue
        if any(ch.isalpha() for ch in line) and not NUMBER_RE.match(line):
            header = _normalize_header(line)
            continue
        values = _split_numeric_line(line)
        if len(values) < 2:
            continue

        peak = _parse_reference_values(values, header)
        if peak is not None:
            peaks.append(peak)

    if not peaks:
        raise ValueError(f"No reference peaks were found in {file_path.name}")
    return ReferencePhase(path=file_path, name=file_path.stem, peaks=peaks, color=color)


def _normalize_header(line: str) -> list[str]:
    normalized = (
        line.lower()
        .replace("2ﾎｸ", "2theta")
        .replace("2θ", "2theta")
        .replace("theta", "theta")
    )
    return re.split(r"[\s,]+", normalized.strip())


def _parse_reference_values(values: list[float], header: list[str] | None = None) -> ReferencePeak | None:
    if header:
        peak = _parse_reference_with_header(values, header)
        if peak is not None:
            return peak

    # Supported common forms:
    # d 2theta I fix h k l
    # d 2theta I h k l
    # 2theta I h k l
    if len(values) >= 7:
        return ReferencePeak(
            d_spacing=values[0],
            two_theta=values[1],
            intensity=values[2],
            h=int(values[-3]),
            k=int(values[-2]),
            l=int(values[-1]),
        )
    if len(values) >= 6:
        return ReferencePeak(
            d_spacing=values[0],
            two_theta=values[1],
            intensity=values[2],
            h=int(values[-3]),
            k=int(values[-2]),
            l=int(values[-1]),
        )
    if len(values) >= 5:
        return ReferencePeak(
            two_theta=values[0],
            intensity=values[1],
            h=int(values[-3]),
            k=int(values[-2]),
            l=int(values[-1]),
        )
    if len(values) >= 2:
        return ReferencePeak(two_theta=values[0], intensity=values[1])
    return None


def _parse_reference_with_header(values: list[float], header: list[str]) -> ReferencePeak | None:
    if len(values) < len(header):
        return None

    index = {name: pos for pos, name in enumerate(header)}
    two_theta_index = _first_existing(index, ["2theta", "2th", "twotheta"])
    intensity_index = _first_existing(index, ["i", "intensity"])
    d_index = _first_existing(index, ["d", "dspacing", "d_spacing"])
    h_index = index.get("h")
    k_index = index.get("k")
    l_index = index.get("l")

    if two_theta_index is None or intensity_index is None:
        return None

    return ReferencePeak(
        two_theta=values[two_theta_index],
        intensity=values[intensity_index],
        d_spacing=values[d_index] if d_index is not None else None,
        h=int(values[h_index]) if h_index is not None else None,
        k=int(values[k_index]) if k_index is not None else None,
        l=int(values[l_index]) if l_index is not None else None,
    )


def _first_existing(index: dict[str, int], names: list[str]) -> int | None:
    for name in names:
        if name in index:
            return index[name]
    return None
