from __future__ import annotations

import sys
import tkinter as tk
import math
from pathlib import Path
from tkinter import colorchooser, filedialog, messagebox, ttk

if __package__ is None or __package__ == "":
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from labplot_studio.exporters import build_svg, export_normalized_csv, export_plot_image
from labplot_studio.identify import find_measured_peaks, match_reference_peaks, rank_candidate_phases
from labplot_studio.models import MeasuredSeries, ReferencePhase
from labplot_studio.parsers import parse_measured_file, parse_reference_file
from labplot_studio.xrd import normalize_measured, normalize_reference_phase, orientation_matches


COLORS = ["#d14a28", "#2374ab", "#2f8f5b", "#8c3f97", "#c08a1a", "#216869", "#c43b65", "#4b6cb7"]
MARKERS = ["circle", "triangle_down", "diamond", "triangle_up", "square", "cross"]

TEXT = {
    "ja": {
        "title": "LabPlot Studio - XRD手動同定",
        "app": "LabPlot Studio",
        "module": "XRD手動同定",
        "language": "言語",
        "load_measured": "測定データを開く",
        "clear_measured": "測定をクリア",
        "library": "参照ライブラリ",
        "choose_library": "参照フォルダを選択",
        "add_selected": "選択した参照を追加",
        "load_ref_files": "参照ファイルを直接追加",
        "active_refs": "使用中の参照",
        "remove_ref": "選択参照を外す",
        "ref_display_name": "参照表示名",
        "ref_color": "参照色",
        "ref_marker": "記号",
        "choose_color": "色を選ぶ",
        "apply_ref_style": "参照名/記号を反映",
        "plot": "XRDプロット",
        "x_min": "2theta min",
        "x_max": "2theta max",
        "offset": "縦オフセット",
        "tolerance": "同定許容差 / deg",
        "min_peak": "測定ピーク閾値",
        "min_ref": "参照強度閾値",
        "orientation": "配向フィルタ",
        "redraw": "再描画",
        "identify": "同定候補を更新",
        "export_svg": "SVG出力",
        "export_image": "PNG/JPEG出力",
        "export_csv": "CSV出力",
        "matches": "同定候補",
        "ready": "測定データと参照ピークを読み込んでください。",
        "empty_plot": "測定XRDデータを読み込んでください",
        "loaded_measured": "測定データを読み込みました",
        "loaded_refs": "参照相を追加しました",
        "library_loaded": "参照ライブラリを読み込みました",
        "no_measured": "先に測定データを読み込んでください。",
        "no_refs": "先に参照データを追加してください。",
        "no_library_selection": "参照ライブラリからファイルを選んでください。",
        "exported_svg": "SVGを書き出しました",
        "exported_image": "画像を書き出しました",
        "exported_csv": "CSVを書き出しました",
    },
    "en": {
        "title": "LabPlot Studio - XRD Manual ID",
        "app": "LabPlot Studio",
        "module": "XRD manual identification",
        "language": "Language",
        "load_measured": "Load measured data",
        "clear_measured": "Clear measured",
        "library": "Reference library",
        "choose_library": "Choose reference folder",
        "add_selected": "Add selected references",
        "load_ref_files": "Add reference files",
        "active_refs": "Active references",
        "remove_ref": "Remove selected reference",
        "ref_display_name": "Reference label",
        "ref_color": "Reference color",
        "ref_marker": "Marker",
        "choose_color": "Choose color",
        "apply_ref_style": "Apply ref style",
        "plot": "XRD plot",
        "x_min": "2theta min",
        "x_max": "2theta max",
        "offset": "Stack offset",
        "tolerance": "Tolerance / deg",
        "min_peak": "Measured peak threshold",
        "min_ref": "Reference intensity threshold",
        "orientation": "Orientation filter",
        "redraw": "Redraw",
        "identify": "Update candidates",
        "export_svg": "Export SVG",
        "export_image": "Export PNG/JPEG",
        "export_csv": "Export CSV",
        "matches": "Candidates",
        "ready": "Load measured XRD data and reference peaks.",
        "empty_plot": "Load measured XRD data to begin",
        "loaded_measured": "Loaded measured data",
        "loaded_refs": "Added reference phases",
        "library_loaded": "Loaded reference library",
        "no_measured": "Load measured data first.",
        "no_refs": "Add references first.",
        "no_library_selection": "Select files from the reference library.",
        "exported_svg": "Exported SVG",
        "exported_image": "Exported image",
        "exported_csv": "Exported CSV",
    },
}


TEXT = {
    "ja": {
        "title": "LabPlot Studio - XRD手動同定",
        "app": "LabPlot Studio",
        "module": "XRD手動同定",
        "language": "言語",
        "load_measured": "測定データを開く",
        "clear_measured": "測定をクリア",
        "library": "参照ライブラリ",
        "choose_library": "参照フォルダを選択",
        "add_selected": "選択した参照を追加",
        "load_ref_files": "参照ファイルを直接追加",
        "active_refs": "使用中の参照",
        "remove_ref": "選択参照を外す",
        "ref_display_name": "参照表示名",
        "ref_color": "参照色",
        "ref_marker": "記号",
        "choose_color": "色を選ぶ",
        "apply_ref_style": "参照名/記号を反映",
        "plot": "XRDプロット",
        "x_min": "2θ min",
        "x_max": "2θ max",
        "offset": "縦オフセット",
        "tolerance": "同定許容差 / deg",
        "min_peak": "測定ピーク閾値",
        "min_ref": "参照強度閾値",
        "orientation": "配向フィルタ",
        "redraw": "再描画",
        "identify": "同定候補を更新",
        "export_svg": "SVG出力",
        "export_image": "PNG/JPEG出力",
        "export_csv": "CSV出力",
        "matches": "ピーク対応",
        "phase_candidates": "候補相ランキング",
        "hide_peak": "選択ピークを隠す",
        "show_all_peaks": "選択参照のピークを全表示",
        "ready": "測定データと参照ピークを読み込んでください。",
        "empty_plot": "測定XRDデータを読み込んでください",
        "loaded_measured": "測定データを読み込みました",
        "loaded_refs": "参照相を追加しました",
        "library_loaded": "参照ライブラリを読み込みました",
        "no_measured": "先に測定データを読み込んでください。",
        "no_refs": "先に参照データを追加してください。",
        "no_library_selection": "参照ライブラリからファイルを選んでください。",
        "exported_svg": "SVGを書き出しました",
        "exported_image": "画像を書き出しました",
        "exported_csv": "CSVを書き出しました",
    },
    "en": {
        "title": "LabPlot Studio - XRD Manual ID",
        "app": "LabPlot Studio",
        "module": "XRD manual identification",
        "language": "Language",
        "load_measured": "Load measured data",
        "clear_measured": "Clear measured",
        "library": "Reference library",
        "choose_library": "Choose reference folder",
        "add_selected": "Add selected references",
        "load_ref_files": "Add reference files",
        "active_refs": "Active references",
        "remove_ref": "Remove selected reference",
        "ref_display_name": "Reference label",
        "ref_color": "Reference color",
        "ref_marker": "Marker",
        "choose_color": "Choose color",
        "apply_ref_style": "Apply ref style",
        "plot": "XRD plot",
        "x_min": "2θ min",
        "x_max": "2θ max",
        "offset": "Stack offset",
        "tolerance": "Tolerance / deg",
        "min_peak": "Measured peak threshold",
        "min_ref": "Reference intensity threshold",
        "orientation": "Orientation filter",
        "redraw": "Redraw",
        "identify": "Update candidates",
        "export_svg": "Export SVG",
        "export_image": "Export PNG/JPEG",
        "export_csv": "Export CSV",
        "matches": "Peak matches",
        "phase_candidates": "Phase candidates",
        "hide_peak": "Hide selected peak",
        "show_all_peaks": "Show all selected-ref peaks",
        "ready": "Load measured XRD data and reference peaks.",
        "empty_plot": "Load measured XRD data to begin",
        "loaded_measured": "Loaded measured data",
        "loaded_refs": "Added reference phases",
        "library_loaded": "Loaded reference library",
        "no_measured": "Load measured data first.",
        "no_refs": "Add references first.",
        "no_library_selection": "Select files from the reference library.",
        "exported_svg": "Exported SVG",
        "exported_image": "Exported image",
        "exported_csv": "Exported CSV",
    },
}


class LabPlotStudio(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.language = tk.StringVar(value="ja")
        self.measured: list[MeasuredSeries] = []
        self.references: list[ReferencePhase] = []
        self.library_files: list[Path] = []

        self.x_min = tk.DoubleVar(value=20.0)
        self.x_max = tk.DoubleVar(value=70.0)
        self.offset = tk.DoubleVar(value=125.0)
        self.tolerance = tk.DoubleVar(value=0.20)
        self.min_peak = tk.DoubleVar(value=8.0)
        self.min_ref = tk.DoubleVar(value=0.0)
        self.orientation = tk.StringVar(value="all")
        self.status = tk.StringVar(value=self.t("ready"))
        self.ref_display_name = tk.StringVar(value="")
        self.ref_color = tk.StringVar(value=COLORS[0])
        self.ref_marker = tk.StringVar(value=MARKERS[0])

        self.geometry("1320x820")
        self.minsize(1080, 700)
        self._build_ui()
        self._draw()

    def t(self, key: str) -> str:
        return TEXT[self.language.get()][key]

    def _build_ui(self) -> None:
        self.title(self.t("title"))
        for child in self.winfo_children():
            child.destroy()

        root = ttk.Frame(self, padding=10)
        root.pack(fill=tk.BOTH, expand=True)

        controls = ttk.Frame(root, width=390)
        controls.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        controls.pack_propagate(False)

        plot_area = ttk.Frame(root)
        plot_area.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self._build_controls(controls)
        self._build_plot_area(plot_area)

    def _build_controls(self, parent: ttk.Frame) -> None:
        ttk.Label(parent, text=self.t("app"), font=("Segoe UI", 16, "bold")).pack(anchor="w")
        ttk.Label(parent, text=self.t("module"), foreground="#555").pack(anchor="w", pady=(0, 8))

        language_row = ttk.Frame(parent)
        language_row.pack(fill=tk.X, pady=(0, 8))
        ttk.Label(language_row, text=self.t("language")).pack(side=tk.LEFT)
        lang = ttk.Combobox(language_row, textvariable=self.language, values=["ja", "en"], state="readonly", width=8)
        lang.pack(side=tk.RIGHT)
        lang.bind("<<ComboboxSelected>>", self._change_language)

        ttk.Button(parent, text=self.t("load_measured"), command=self.load_measured).pack(fill=tk.X, pady=2)
        ttk.Button(parent, text=self.t("clear_measured"), command=self.clear_measured).pack(fill=tk.X, pady=(2, 8))

        self._number_field(parent, self.t("x_min"), self.x_min)
        self._number_field(parent, self.t("x_max"), self.x_max)
        self._number_field(parent, self.t("offset"), self.offset)

        row = ttk.Frame(parent)
        row.pack(fill=tk.X, pady=(8, 2))
        ttk.Label(row, text=self.t("orientation")).pack(side=tk.LEFT)
        orientation = ttk.Combobox(
            row,
            textvariable=self.orientation,
            values=["all", "h00", "0k0", "00l", "hk0", "h0l", "0kl"],
            state="readonly",
            width=10,
        )
        orientation.pack(side=tk.RIGHT)
        orientation.bind("<<ComboboxSelected>>", lambda _event: self._refresh_all())

        self._number_field(parent, self.t("tolerance"), self.tolerance)
        self._number_field(parent, self.t("min_peak"), self.min_peak)
        self._number_field(parent, self.t("min_ref"), self.min_ref)

        ttk.Separator(parent).pack(fill=tk.X, pady=10)
        ttk.Label(parent, text=self.t("library"), font=("Segoe UI", 10, "bold")).pack(anchor="w")
        ttk.Button(parent, text=self.t("choose_library"), command=self.choose_library).pack(fill=tk.X, pady=2)
        self.library_list = tk.Listbox(parent, height=7, selectmode=tk.EXTENDED, exportselection=False)
        self.library_list.pack(fill=tk.X, pady=3)
        ttk.Button(parent, text=self.t("add_selected"), command=self.add_selected_library_refs).pack(fill=tk.X, pady=2)
        ttk.Button(parent, text=self.t("load_ref_files"), command=self.load_references).pack(fill=tk.X, pady=(2, 8))

        ttk.Label(parent, text=self.t("active_refs"), font=("Segoe UI", 10, "bold")).pack(anchor="w")
        self.reference_list = tk.Listbox(parent, height=5, exportselection=False)
        self.reference_list.pack(fill=tk.X, pady=3)
        self.reference_list.bind("<<ListboxSelect>>", self._load_selected_reference_style)
        self._text_field(parent, self.t("ref_display_name"), self.ref_display_name)
        self._text_field(parent, self.t("ref_color"), self.ref_color)
        marker_row = ttk.Frame(parent)
        marker_row.pack(fill=tk.X, pady=2)
        ttk.Label(marker_row, text=self.t("ref_marker")).pack(side=tk.LEFT)
        marker_box = ttk.Combobox(marker_row, textvariable=self.ref_marker, values=MARKERS, state="readonly", width=16)
        marker_box.pack(side=tk.RIGHT)
        color_buttons = ttk.Frame(parent)
        color_buttons.pack(fill=tk.X, pady=2)
        ttk.Button(color_buttons, text=self.t("choose_color"), command=self.choose_reference_color).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 3))
        ttk.Button(color_buttons, text=self.t("apply_ref_style"), command=self.apply_reference_style).pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(3, 0))
        ttk.Button(parent, text=self.t("remove_ref"), command=self.remove_selected_reference).pack(fill=tk.X, pady=(2, 8))

        buttons = ttk.Frame(parent)
        buttons.pack(fill=tk.X)
        ttk.Button(buttons, text=self.t("redraw"), command=self._refresh_all).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 3))
        ttk.Button(buttons, text=self.t("identify"), command=self.update_matches).pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(3, 0))
        peak_buttons = ttk.Frame(parent)
        peak_buttons.pack(fill=tk.X, pady=(8, 0))
        ttk.Button(peak_buttons, text=self.t("hide_peak"), command=self.hide_selected_peak).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 3))
        ttk.Button(peak_buttons, text=self.t("show_all_peaks"), command=self.show_all_selected_reference_peaks).pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(3, 0))
        ttk.Button(parent, text=self.t("export_svg"), command=self.export_svg).pack(fill=tk.X, pady=(8, 2))
        ttk.Button(parent, text=self.t("export_image"), command=self.export_image).pack(fill=tk.X, pady=2)
        ttk.Button(parent, text=self.t("export_csv"), command=self.export_csv).pack(fill=tk.X, pady=2)

        ttk.Label(parent, textvariable=self.status, wraplength=365, foreground="#555").pack(anchor="w", pady=(8, 0))

        self._refresh_library_list()
        self._refresh_reference_list()

    def _build_plot_area(self, parent: ttk.Frame) -> None:
        ttk.Label(parent, text=self.t("plot"), font=("Segoe UI", 12, "bold")).pack(anchor="w")
        self.canvas = tk.Canvas(parent, bg="white", highlightthickness=1, highlightbackground="#bdbdbd")
        self.canvas.pack(fill=tk.BOTH, expand=True, pady=(6, 8))
        self.canvas.bind("<Configure>", lambda _event: self._draw())

        ttk.Label(parent, text=self.t("phase_candidates"), font=("Segoe UI", 10, "bold")).pack(anchor="w")
        candidate_columns = ("score", "phase", "main", "matched")
        self.candidate_table = ttk.Treeview(parent, columns=candidate_columns, show="headings", height=5)
        candidate_headings = {
            "score": "score",
            "phase": "phase",
            "main": "main peak",
            "matched": "matched",
        }
        candidate_widths = {"score": 70, "phase": 240, "main": 90, "matched": 90}
        for column in candidate_columns:
            self.candidate_table.heading(column, text=candidate_headings[column])
            self.candidate_table.column(column, width=candidate_widths[column], anchor=tk.W)
        self.candidate_table.pack(fill=tk.X, pady=(0, 8))

        ttk.Label(parent, text=self.t("matches"), font=("Segoe UI", 10, "bold")).pack(anchor="w")
        columns = ("meas", "phase", "ref", "delta", "hkl")
        self.match_table = ttk.Treeview(parent, columns=columns, show="headings", height=8)
        headings = {
            "meas": "2θ obs",
            "phase": "phase",
            "ref": "2θ ref",
            "delta": "delta",
            "hkl": "hkl",
        }
        widths = {"meas": 95, "phase": 240, "ref": 95, "delta": 80, "hkl": 60}
        for column in columns:
            self.match_table.heading(column, text=headings[column])
            self.match_table.column(column, width=widths[column], anchor=tk.W)
        self.match_table.pack(fill=tk.X)

    def _number_field(self, parent: ttk.Frame, label: str, var: tk.DoubleVar) -> None:
        row = ttk.Frame(parent)
        row.pack(fill=tk.X, pady=2)
        ttk.Label(row, text=label).pack(side=tk.LEFT)
        entry = ttk.Entry(row, textvariable=var, width=12)
        entry.pack(side=tk.RIGHT)
        entry.bind("<Return>", lambda _event: self._refresh_all())
        entry.bind("<FocusOut>", lambda _event: self._refresh_all())

    def _text_field(self, parent: ttk.Frame, label: str, var: tk.StringVar) -> None:
        row = ttk.Frame(parent)
        row.pack(fill=tk.X, pady=2)
        ttk.Label(row, text=label).pack(side=tk.LEFT)
        entry = ttk.Entry(row, textvariable=var, width=20)
        entry.pack(side=tk.RIGHT)

    def _change_language(self, _event: object | None = None) -> None:
        self.status.set(self.t("ready"))
        self._build_ui()
        self._refresh_all()

    def load_measured(self) -> None:
        paths = filedialog.askopenfilenames(
            title=self.t("load_measured"),
            filetypes=[("Measurement files", "*.xy *.txt *.csv *.dat"), ("All files", "*.*")],
        )
        if not paths:
            return
        loaded = []
        try:
            for path in paths:
                loaded.append(parse_measured_file(path))
        except Exception as exc:
            messagebox.showerror("Load error", str(exc))
            return
        self.measured.extend(loaded)
        self.status.set(f"{self.t('loaded_measured')}: {len(loaded)}")
        self._refresh_all()

    def clear_measured(self) -> None:
        self.measured.clear()
        self.status.set(self.t("ready"))
        self._refresh_all()

    def choose_library(self) -> None:
        directory = filedialog.askdirectory(title=self.t("choose_library"))
        if not directory:
            return
        root = Path(directory)
        self.library_files = sorted(
            [path for path in root.rglob("*") if path.suffix.lower() in {".txt", ".csv", ".dat"}],
            key=lambda path: path.name.lower(),
        )
        self.status.set(f"{self.t('library_loaded')}: {len(self.library_files)}")
        self._refresh_library_list()

    def add_selected_library_refs(self) -> None:
        indexes = list(self.library_list.curselection())
        if not indexes:
            messagebox.showinfo(self.t("library"), self.t("no_library_selection"))
            return
        paths = [self.library_files[index] for index in indexes]
        self._add_reference_paths(paths)

    def load_references(self) -> None:
        paths = filedialog.askopenfilenames(
            title=self.t("load_ref_files"),
            filetypes=[("Reference files", "*.txt *.csv *.dat"), ("All files", "*.*")],
        )
        if paths:
            self._add_reference_paths([Path(path) for path in paths])

    def _add_reference_paths(self, paths: list[Path]) -> None:
        loaded = []
        try:
            for path in paths:
                color = COLORS[(len(self.references) + len(loaded)) % len(COLORS)]
                marker = MARKERS[(len(self.references) + len(loaded)) % len(MARKERS)]
                phase = normalize_reference_phase(parse_reference_file(path, color=color))
                phase.marker = marker
                phase.display_name = self._suggest_reference_label(phase.name)
                loaded.append(phase)
        except Exception as exc:
            messagebox.showerror("Load error", str(exc))
            return
        self.references.extend(loaded)
        self.status.set(f"{self.t('loaded_refs')}: {len(loaded)}")
        self._refresh_all()

    def _suggest_reference_label(self, name: str) -> str:
        lower = name.lower()
        if "m-type" in lower or "bafe12o19" in lower:
            return "M-type"
        if "z-type" in lower:
            return "Z-type"
        if "y-type" in lower:
            return "Y-type"
        if "spinel" in lower or "fe2o4" in lower:
            return "spinel"
        return name

    def _selected_reference_index(self) -> int | None:
        selection = self.reference_list.curselection()
        if not selection:
            return None
        return int(selection[0])

    def _load_selected_reference_style(self, _event: object | None = None) -> None:
        index = self._selected_reference_index()
        if index is None:
            return
        phase = self.references[index]
        self.ref_display_name.set(phase.label)
        self.ref_color.set(phase.color)
        self.ref_marker.set(phase.marker)

    def choose_reference_color(self) -> None:
        chosen = colorchooser.askcolor(color=self.ref_color.get(), title=self.t("choose_color"))
        if chosen and chosen[1]:
            self.ref_color.set(chosen[1])

    def apply_reference_style(self) -> None:
        index = self._selected_reference_index()
        if index is None:
            return
        phase = self.references[index]
        phase.display_name = self.ref_display_name.get().strip()
        phase.color = self.ref_color.get().strip() or phase.color
        phase.marker = self.ref_marker.get() or phase.marker
        self._refresh_all()

    def remove_selected_reference(self) -> None:
        indexes = sorted(self.reference_list.curselection(), reverse=True)
        for index in indexes:
            del self.references[index]
        self._refresh_all()

    def export_svg(self) -> None:
        if not self.measured:
            messagebox.showinfo(self.t("export_svg"), self.t("no_measured"))
            return
        path = filedialog.asksaveasfilename(
            title=self.t("export_svg"),
            defaultextension=".svg",
            filetypes=[("SVG files", "*.svg")],
        )
        if not path:
            return
        x_min, x_max, offset = self._plot_settings()
        phases = self._filtered_references()
        for series in self.measured:
            normalize_measured(series, x_min, x_max)
        svg = build_svg(self.measured, phases, x_min, x_max, offset, 1200, 900)
        Path(path).write_text(svg, encoding="utf-8")
        self.status.set(f"{self.t('exported_svg')}: {Path(path).name}")

    def export_image(self) -> None:
        if not self.measured:
            messagebox.showinfo(self.t("export_image"), self.t("no_measured"))
            return
        path = filedialog.asksaveasfilename(
            title=self.t("export_image"),
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg *.jpeg")],
        )
        if not path:
            return
        x_min, x_max, offset = self._plot_settings()
        phases = self._filtered_references()
        for series in self.measured:
            normalize_measured(series, x_min, x_max)
        export_plot_image(path, self.measured, phases, x_min, x_max, offset)
        self.status.set(f"{self.t('exported_image')}: {Path(path).name}")

    def export_csv(self) -> None:
        if not self.measured:
            messagebox.showinfo(self.t("export_csv"), self.t("no_measured"))
            return
        path = filedialog.asksaveasfilename(
            title=self.t("export_csv"),
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
        )
        if not path:
            return
        x_min, x_max, _offset = self._plot_settings()
        for series in self.measured:
            normalize_measured(series, x_min, x_max)
        export_normalized_csv(path, self.measured)
        self.status.set(f"{self.t('exported_csv')}: {Path(path).name}")

    def update_matches(self) -> None:
        self.match_table.delete(*self.match_table.get_children())
        if not self.measured:
            return
        x_min, x_max, _offset = self._plot_settings()
        phases = self._filtered_references()
        peaks = find_measured_peaks(self.measured[0], x_min, x_max, self.min_peak.get())
        matches = match_reference_peaks(peaks, phases, self.tolerance.get(), self.min_ref.get())
        self._update_phase_candidates(peaks, phases)
        for match in matches[:300]:
            self.match_table.insert(
                "",
                tk.END,
                values=(
                    f"{match.measured_two_theta:.3f}",
                    match.phase_name,
                    f"{match.reference_two_theta:.3f}",
                    f"{match.delta:+.3f}",
                    match.hkl,
                ),
            )
        self.status.set(f"{self.t('matches')}: {len(matches)}")

    def _update_phase_candidates(self, measured_peaks: list[tuple[float, float]], phases: list[ReferencePhase]) -> None:
        if not hasattr(self, "candidate_table"):
            return
        self.candidate_table.delete(*self.candidate_table.get_children())
        candidates = rank_candidate_phases(measured_peaks, phases, self.tolerance.get(), max(self.min_ref.get(), 8.0))
        for candidate in candidates[:50]:
            main = f"{candidate.main_peak_two_theta:.3f}"
            if not candidate.main_peak_found:
                main += " missing"
            self.candidate_table.insert(
                "",
                tk.END,
                values=(
                    f"{candidate.score:.1f}",
                    candidate.phase_name,
                    main,
                    f"{candidate.matched_peak_count}/{candidate.expected_peak_count}",
                ),
            )

    def hide_selected_peak(self) -> None:
        if not hasattr(self, "match_table"):
            return
        selection = self.match_table.selection()
        if not selection:
            return
        values = self.match_table.item(selection[0], "values")
        if len(values) < 5:
            return
        phase_label = str(values[1])
        try:
            ref_two_theta = float(values[2])
        except ValueError:
            return
        hkl = str(values[4])
        for phase in self.references:
            if phase.label != phase_label:
                continue
            for peak in phase.peaks:
                if abs(peak.two_theta - ref_two_theta) < 0.0005 and peak.hkl_label == hkl:
                    phase.hidden_peak_keys.add(phase.peak_key(peak))
                    self._refresh_all()
                    return

    def show_all_selected_reference_peaks(self) -> None:
        index = self._selected_reference_index()
        if index is None:
            return
        self.references[index].hidden_peak_keys.clear()
        self._refresh_all()

    def _refresh_all(self) -> None:
        self._refresh_reference_list()
        self._draw()
        if hasattr(self, "match_table"):
            self.update_matches()

    def _refresh_library_list(self) -> None:
        if not hasattr(self, "library_list"):
            return
        self.library_list.delete(0, tk.END)
        for path in self.library_files:
            self.library_list.insert(tk.END, path.name)

    def _refresh_reference_list(self) -> None:
        if not hasattr(self, "reference_list"):
            return
        self.reference_list.delete(0, tk.END)
        for phase in self.references:
            self.reference_list.insert(tk.END, f"{phase.label}  [{phase.name}]")

    def _plot_settings(self) -> tuple[float, float, float]:
        x_min = float(self.x_min.get())
        x_max = float(self.x_max.get())
        if x_max <= x_min:
            x_max = x_min + 1.0
        return x_min, x_max, float(self.offset.get())

    def _filtered_references(self) -> list[ReferencePhase]:
        mode = self.orientation.get()
        filtered: list[ReferencePhase] = []
        for phase in self.references:
            peaks = [
                peak for peak in phase.visible_peaks()
                if orientation_matches(peak, mode) and peak.intensity >= self.min_ref.get()
            ]
            filtered.append(
                ReferencePhase(
                    path=phase.path,
                    name=phase.name,
                    peaks=peaks,
                    color=phase.color,
                    display_name=phase.display_name,
                    marker=phase.marker,
                    hidden_peak_keys=set(phase.hidden_peak_keys),
                )
            )
        return filtered

    def _draw(self) -> None:
        if not hasattr(self, "canvas"):
            return
        canvas = self.canvas
        canvas.delete("all")
        width = max(canvas.winfo_width(), 720)
        height = max(canvas.winfo_height(), 520)
        left, right, top, bottom = 82, 28, 76, 76
        plot_w = width - left - right
        plot_h = height - top - bottom
        x_min, x_max, offset = self._plot_settings()
        y_min = -12.0
        y_max = max(112 + offset * max(len(self.measured) - 1, 0), 120)
        font = ("Times New Roman", 15)
        axis_font = ("Times New Roman", 18)
        small = ("Times New Roman", 10)

        def sx(x: float) -> float:
            return left + (x - x_min) / (x_max - x_min) * plot_w

        def sy(y: float) -> float:
            return top + plot_h - (y - y_min) / (y_max - y_min) * plot_h

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
            if best_index is None or best_delta is None or best_delta > max(self.tolerance.get(), 0.12):
                return None
            return series.normalized_y[best_index]

        canvas.create_rectangle(0, 0, width, height, fill="white", outline="")
        canvas.create_rectangle(left, top, left + plot_w, top + plot_h, outline="#111", width=1.4)
        canvas.create_text(width / 2, height - 30, text="2θ (deg.)   Cu-Kα", font=axis_font)
        canvas.create_text(24, top + plot_h / 2, text="Intensity (arb. units)", angle=90, font=font)

        self._draw_reference_legend(canvas, left + 28, 28)

        for x in self._major_ticks(x_min, x_max):
            px = sx(x)
            canvas.create_line(px, top + plot_h, px, top + plot_h - 16, fill="#111", width=1.2)
            canvas.create_line(px, top, px, top + 16, fill="#111", width=1.2)
            canvas.create_text(px, top + plot_h + 28, text=f"{x:g}", font=axis_font)

        if not self.measured:
            canvas.create_text(width / 2, height / 2, text=self.t("empty_plot"), fill="#777", font=("Segoe UI", 14))
            return

        for index, series in enumerate(self.measured):
            normalize_measured(series, x_min, x_max)
            base = offset * index
            points = []
            for x, y in zip(series.x, series.normalized_y):
                if x_min <= x <= x_max:
                    points.extend([sx(x), sy(y + base)])
            if len(points) >= 4:
                canvas.create_line(*points, fill="#111", width=1.15)
            canvas.create_text(left + plot_w - 8, sy(base + 94), text=series.name, anchor="e", fill="#222", font=("Times New Roman", 10))

        for phase_index, phase in enumerate(self._filtered_references()):
            for series_index, series in enumerate(self.measured):
                base = self.offset.get() * series_index
                for peak in phase.peaks:
                    if not (x_min <= peak.two_theta <= x_max):
                        continue
                    y_value = nearest_y(series, peak.two_theta)
                    if y_value is None:
                        continue
                    px = sx(peak.two_theta) + (phase_index % 3 - 1) * 4
                    py = sy(y_value + base) - 12 - 3 * (phase_index // 3)
                    self._draw_marker(canvas, px, py, phase.marker, phase.color, 8)

        marker_y = top + plot_h + 26
        for phase_index, phase in enumerate(self._filtered_references()):
            y0 = marker_y + phase_index * 14
            canvas.create_text(left, y0, text=phase.label, anchor="w", fill=phase.color, font=("Times New Roman", 8))
            for peak in phase.peaks:
                if x_min <= peak.two_theta <= x_max:
                    px = sx(peak.two_theta)
                    marker_h = 3 + 8 * peak.intensity / 100.0
                    canvas.create_line(px, y0, px, y0 - marker_h, fill=phase.color, width=1.4)

    def _draw_reference_legend(self, canvas: tk.Canvas, x: float, y: float) -> None:
        if not self.references:
            return
        col_width = 190
        row_height = 28
        for index, phase in enumerate(self.references[:8]):
            col = index % 4
            row = index // 4
            px = x + col * col_width
            py = y + row * row_height
            self._draw_marker(canvas, px, py, phase.marker, phase.color, 10)
            canvas.create_text(px + 24, py, text=phase.label, anchor="w", fill="#111", font=("Times New Roman", 16))

    def _major_ticks(self, x_min: float, x_max: float) -> list[float]:
        start = math.ceil(x_min / 10.0) * 10
        ticks = []
        value = start
        while value <= x_max + 1e-9:
            ticks.append(float(value))
            value += 10
        return ticks or [x_min, x_max]

    def _draw_marker(self, canvas: tk.Canvas, x: float, y: float, marker: str, color: str, size: int) -> None:
        if marker == "triangle_down":
            points = [x, y + size, x - size, y - size, x + size, y - size]
            canvas.create_polygon(points, fill=color, outline=color)
        elif marker == "triangle_up":
            points = [x, y - size, x - size, y + size, x + size, y + size]
            canvas.create_polygon(points, fill=color, outline=color)
        elif marker == "diamond":
            points = [x, y - size, x - size, y, x, y + size, x + size, y]
            canvas.create_polygon(points, fill=color, outline=color)
        elif marker == "square":
            canvas.create_rectangle(x - size, y - size, x + size, y + size, fill=color, outline=color)
        elif marker == "cross":
            canvas.create_line(x - size, y - size, x + size, y + size, fill=color, width=2)
            canvas.create_line(x - size, y + size, x + size, y - size, fill=color, width=2)
        else:
            canvas.create_oval(x - size, y - size, x + size, y + size, fill=color, outline=color)


def main() -> None:
    app = LabPlotStudio()
    app.mainloop()


if __name__ == "__main__":
    main()
