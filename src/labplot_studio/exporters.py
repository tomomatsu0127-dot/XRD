from __future__ import annotations

import csv
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from .models import MeasuredSeries, ReferencePhase


def export_normalized_csv(path: str | Path, series_list: list[MeasuredSeries]) -> None:
    out_path = Path(path)
    with out_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["dataset", "two_theta", "intensity_normalized"])
        for series in series_list:
            y_values = series.normalized_y or series.y
            for x, y in zip(series.x, y_values):
                writer.writerow([series.name, x, y])


def build_svg(
    series_list: list[MeasuredSeries],
    phases: list[ReferencePhase],
    x_min: float,
    x_max: float,
    offset: float,
    width: int,
    height: int,
) -> str:
    margin_left = 88
    margin_right = 34
    margin_top = 92
    margin_bottom = 86
    plot_w = width - margin_left - margin_right
    plot_h = height - margin_top - margin_bottom

    y_min = -12.0
    y_max = max(112 + offset * max(len(series_list) - 1, 0), 120)

    def sx(x: float) -> float:
        return margin_left + (x - x_min) / (x_max - x_min) * plot_w

    def sy(y: float) -> float:
        return margin_top + plot_h - (y - y_min) / (y_max - y_min) * plot_h

    def nearest_y(series: MeasuredSeries, target_x: float) -> float | None:
        best_index = None
        best_delta = None
        for i, x in enumerate(series.x):
            if x < x_min or x > x_max:
                continue
            delta = abs(x - target_x)
            if best_delta is None or delta < best_delta:
                best_delta = delta
                best_index = i
        if best_index is None or best_delta is None or best_delta > 0.25:
            return None
        values = series.normalized_y or series.y
        return values[best_index]

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        f'<rect x="{margin_left}" y="{margin_top}" width="{plot_w}" height="{plot_h}" fill="none" stroke="#111" stroke-width="1.2"/>',
        f'<text x="{width / 2}" y="{height - 30}" font-family="Times New Roman, serif" font-size="30" text-anchor="middle">2θ (deg.)   Cu-Kα</text>',
        f'<text x="34" y="{margin_top + plot_h / 2}" font-family="Times New Roman, serif" font-size="24" text-anchor="middle" transform="rotate(-90 34 {margin_top + plot_h / 2})">Intensity (arb. units)</text>',
    ]

    for index, phase in enumerate(phases[:8]):
        col = index % 4
        row = index // 4
        lx = margin_left + 35 + col * 210
        ly = 35 + row * 28
        parts.append(_svg_marker(lx, ly, phase.marker, phase.color, 10))
        parts.append(f'<text x="{lx + 24}" y="{ly + 7}" font-family="Times New Roman, serif" font-size="22">{_escape(phase.label)}</text>')

    for x in _major_ticks(x_min, x_max):
        px = sx(x)
        parts.append(f'<line x1="{px:.2f}" y1="{margin_top + plot_h}" x2="{px:.2f}" y2="{margin_top + plot_h - 18}" stroke="#111" stroke-width="1.2"/>')
        parts.append(f'<line x1="{px:.2f}" y1="{margin_top}" x2="{px:.2f}" y2="{margin_top + 18}" stroke="#111" stroke-width="1.2"/>')
        parts.append(f'<text x="{px:.2f}" y="{margin_top + plot_h + 42}" font-family="Times New Roman, serif" font-size="30" text-anchor="middle">{x:g}</text>')

    for index, series in enumerate(series_list):
        base = offset * index
        y_values = series.normalized_y or series.y
        points = []
        for x, y in zip(series.x, y_values):
            if x_min <= x <= x_max:
                points.append(f"{sx(x):.2f},{sy(y + base):.2f}")
        if points:
            parts.append(f'<polyline fill="none" stroke="#111" stroke-width="1.2" points="{" ".join(points)}"/>')
            parts.append(f'<text x="{margin_left + plot_w - 6}" y="{sy(base + 94):.2f}" font-family="Times New Roman, serif" font-size="12" text-anchor="end">{_escape(series.name)}</text>')

    for phase_index, phase in enumerate(phases):
        for series_index, series in enumerate(series_list):
            base = offset * series_index
            for peak in phase.peaks:
                if x_min <= peak.two_theta <= x_max:
                    y_value = nearest_y(series, peak.two_theta)
                    if y_value is None:
                        continue
                    px = sx(peak.two_theta) + (phase_index % 3 - 1) * 4
                    py = sy(y_value + base) - 12 - 3 * (phase_index // 3)
                    parts.append(_svg_marker(px, py, phase.marker, phase.color, 8))

    marker_bottom = margin_top + plot_h + 34
    for phase_index, phase in enumerate(phases):
        y0 = marker_bottom + phase_index * 14
        parts.append(f'<text x="{margin_left}" y="{y0 + 4}" font-family="Times New Roman, serif" font-size="9" fill="{phase.color}">{_escape(phase.label)}</text>')
        for peak in phase.peaks:
            if x_min <= peak.two_theta <= x_max:
                px = sx(peak.two_theta)
                marker_h = 3 + 8 * peak.intensity / 100.0
                parts.append(f'<line x1="{px:.2f}" y1="{y0:.2f}" x2="{px:.2f}" y2="{y0 - marker_h:.2f}" stroke="{phase.color}" stroke-width="1.3"/>')

    parts.append("</svg>")
    return "\n".join(parts)


def export_plot_image(
    path: str | Path,
    series_list: list[MeasuredSeries],
    phases: list[ReferencePhase],
    x_min: float,
    x_max: float,
    offset: float,
    width: int = 1800,
    height: int = 1350,
) -> None:
    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)
    fonts = _load_fonts()
    margin_left = 150
    margin_right = 70
    margin_top = 155
    margin_bottom = 150
    plot_w = width - margin_left - margin_right
    plot_h = height - margin_top - margin_bottom
    y_min = -12.0
    y_max = max(112 + offset * max(len(series_list) - 1, 0), 120)

    def sx(x: float) -> float:
        return margin_left + (x - x_min) / (x_max - x_min) * plot_w

    def sy(y: float) -> float:
        return margin_top + plot_h - (y - y_min) / (y_max - y_min) * plot_h

    draw.rectangle((margin_left, margin_top, margin_left + plot_w, margin_top + plot_h), outline="black", width=3)
    _draw_centered_text(draw, (width / 2, height - 58), "2θ (deg.)   Cu-Kα", fonts["axis"])
    _draw_rotated_text(image, (48, margin_top + plot_h / 2), "Intensity (arb. units)", fonts["label"])

    for index, phase in enumerate(phases[:8]):
        col = index % 4
        row = index // 4
        lx = margin_left + 60 + col * 300
        ly = 62 + row * 42
        _pil_marker(draw, lx, ly, phase.marker, phase.color, 17)
        draw.text((lx + 38, ly - 18), phase.label, fill="black", font=fonts["legend"])

    for x in _major_ticks(x_min, x_max):
        px = sx(x)
        draw.line((px, margin_top + plot_h, px, margin_top + plot_h - 28), fill="black", width=2)
        draw.line((px, margin_top, px, margin_top + 28), fill="black", width=2)
        _draw_centered_text(draw, (px, margin_top + plot_h + 54), f"{x:g}", fonts["axis"])

    def nearest_y(series: MeasuredSeries, target_x: float) -> float | None:
        best_index = None
        best_delta = None
        for i, x in enumerate(series.x):
            if x < x_min or x > x_max:
                continue
            delta = abs(x - target_x)
            if best_delta is None or delta < best_delta:
                best_delta = delta
                best_index = i
        if best_index is None or best_delta is None or best_delta > 0.25:
            return None
        values = series.normalized_y or series.y
        return values[best_index]

    for index, series in enumerate(series_list):
        base = offset * index
        values = series.normalized_y or series.y
        points = [(sx(x), sy(y + base)) for x, y in zip(series.x, values) if x_min <= x <= x_max]
        if len(points) >= 2:
            draw.line(points, fill="black", width=2)
        draw.text((margin_left + plot_w - 260, sy(base + 94) - 15), series.name, fill="black", font=fonts["small"])

    for phase_index, phase in enumerate(phases):
        for series_index, series in enumerate(series_list):
            base = offset * series_index
            for peak in phase.peaks:
                if not (x_min <= peak.two_theta <= x_max):
                    continue
                y_value = nearest_y(series, peak.two_theta)
                if y_value is None:
                    continue
                px = sx(peak.two_theta) + (phase_index % 3 - 1) * 7
                py = sy(y_value + base) - 24 - 5 * (phase_index // 3)
                _pil_marker(draw, px, py, phase.marker, phase.color, 14)

    suffix = Path(path).suffix.lower()
    image.save(path, quality=95 if suffix in {".jpg", ".jpeg"} else None)


def _svg_marker(x: float, y: float, marker: str, color: str, size: int) -> str:
    if marker == "triangle_down":
        points = f"{x:.2f},{y + size:.2f} {x - size:.2f},{y - size:.2f} {x + size:.2f},{y - size:.2f}"
        return f'<polygon points="{points}" fill="{color}" stroke="{color}"/>'
    if marker == "triangle_up":
        points = f"{x:.2f},{y - size:.2f} {x - size:.2f},{y + size:.2f} {x + size:.2f},{y + size:.2f}"
        return f'<polygon points="{points}" fill="{color}" stroke="{color}"/>'
    if marker == "diamond":
        points = f"{x:.2f},{y - size:.2f} {x - size:.2f},{y:.2f} {x:.2f},{y + size:.2f} {x + size:.2f},{y:.2f}"
        return f'<polygon points="{points}" fill="{color}" stroke="{color}"/>'
    if marker == "square":
        return f'<rect x="{x - size:.2f}" y="{y - size:.2f}" width="{2 * size}" height="{2 * size}" fill="{color}" stroke="{color}"/>'
    if marker == "cross":
        return (
            f'<line x1="{x - size:.2f}" y1="{y - size:.2f}" x2="{x + size:.2f}" y2="{y + size:.2f}" stroke="{color}" stroke-width="2"/>'
            f'<line x1="{x - size:.2f}" y1="{y + size:.2f}" x2="{x + size:.2f}" y2="{y - size:.2f}" stroke="{color}" stroke-width="2"/>'
        )
    return f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{size}" fill="{color}" stroke="{color}"/>'


def _major_ticks(x_min: float, x_max: float) -> list[float]:
    start = math.ceil(x_min / 10.0) * 10
    ticks = []
    value = start
    while value <= x_max + 1e-9:
        ticks.append(float(value))
        value += 10
    if not ticks:
        ticks = [x_min, x_max]
    return ticks


def _load_fonts() -> dict[str, ImageFont.FreeTypeFont | ImageFont.ImageFont]:
    candidates = [
        Path(r"C:\Windows\Fonts\times.ttf"),
        Path(r"C:\Windows\Fonts\timesbd.ttf"),
    ]
    regular = candidates[0] if candidates[0].exists() else None
    return {
        "axis": ImageFont.truetype(str(regular), 46) if regular else ImageFont.load_default(),
        "label": ImageFont.truetype(str(regular), 40) if regular else ImageFont.load_default(),
        "legend": ImageFont.truetype(str(regular), 38) if regular else ImageFont.load_default(),
        "small": ImageFont.truetype(str(regular), 24) if regular else ImageFont.load_default(),
    }


def _draw_centered_text(draw: ImageDraw.ImageDraw, center: tuple[float, float], text: str, font: ImageFont.ImageFont) -> None:
    box = draw.textbbox((0, 0), text, font=font)
    x = center[0] - (box[2] - box[0]) / 2
    y = center[1] - (box[3] - box[1]) / 2
    draw.text((x, y), text, fill="black", font=font)


def _draw_rotated_text(image: Image.Image, center: tuple[float, float], text: str, font: ImageFont.ImageFont) -> None:
    temp = Image.new("RGBA", (600, 80), (255, 255, 255, 0))
    draw = ImageDraw.Draw(temp)
    box = draw.textbbox((0, 0), text, font=font)
    draw.text(((600 - (box[2] - box[0])) / 2, (80 - (box[3] - box[1])) / 2), text, fill="black", font=font)
    rotated = temp.rotate(90, expand=True)
    image.paste(rotated, (int(center[0] - rotated.width / 2), int(center[1] - rotated.height / 2)), rotated)


def _pil_marker(draw: ImageDraw.ImageDraw, x: float, y: float, marker: str, color: str, size: int) -> None:
    if marker == "triangle_down":
        draw.polygon([(x, y + size), (x - size, y - size), (x + size, y - size)], fill=color)
    elif marker == "triangle_up":
        draw.polygon([(x, y - size), (x - size, y + size), (x + size, y + size)], fill=color)
    elif marker == "diamond":
        draw.polygon([(x, y - size), (x - size, y), (x, y + size), (x + size, y)], fill=color)
    elif marker == "square":
        draw.rectangle((x - size, y - size, x + size, y + size), fill=color)
    elif marker == "cross":
        draw.line((x - size, y - size, x + size, y + size), fill=color, width=4)
        draw.line((x - size, y + size, x + size, y - size), fill=color, width=4)
    else:
        draw.ellipse((x - size, y - size, x + size, y + size), fill=color)


def _escape(value: str) -> str:
    return (
        value.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )
