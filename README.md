# LabPlot Studio Desktop

LabPlot Studio is a local desktop analysis app starter for laboratory measurement data.

The first implemented workflow is manual XRD identification:

- load measured `.xy`, `.txt`, `.csv`, `.dat` files
- load reference peak files such as `d 2theta I fix h k l` or `2theta I h k l`
- scan a folder of many reference files and add selected phases to the plot
- edit reference display names, colors, and marker symbols
- normalize measured data by subtracting the minimum and scaling the maximum to 100
- normalize each reference phase to max intensity 100
- stack multiple measured traces
- show multiple reference phases
- filter reference peaks by orientation: all, h00, 0k0, 00l, hk0, h0l, 0kl
- display manual identification candidates by comparing measured peak positions with selected references
- rank candidate phases by matched reference peaks, with main-peak absence strongly penalized
- overlay colored phase markers on measured peaks in a publication-style view
- hide individual reference peaks that should not be shown for a selected graph
- compare several identified measured patterns as vertically stacked traces while preserving phase colors
- hide y-axis numeric labels because the plotted intensity is normalized
- use inward ticks at 10-degree x-axis intervals
- lift the normalized baseline slightly above the lower frame
- switch UI language between Japanese and English
- export the current plot as SVG
- export the current plot as PNG or JPEG
- export normalized measured data as CSV

Additional analysis cores are included for the next development step:

- VSM text parsing, mass normalization, kOe conversion, and basic hysteresis estimates
- hexagonal lattice-constant fitting from indexed XRD peaks

The long-term goal is an Igor-like local desktop suite for XRD, VSM, MT, SQUID, and related measurement workflows.

## Run

Use Python 3.10 or newer.

```powershell
python -m labplot_studio
```

When running from this folder without installation:

```powershell
python src\labplot_studio\main.py
```

On this PC, double-click:

```text
run_labplot_studio.bat
```

See `HOW_TO_RUN_JA.md` for Japanese startup notes.

## Current recommended workflow

1. Start `run_labplot_studio.bat`.
2. Keep language as `ja` or switch to `en`.
3. Load a measured XRD file, for example `sample_data/sample_measurement.xy`.
4. Choose a reference library folder, or directly add reference files.
5. Add phases to the active reference list.
6. Select an active reference and edit its display name, color, and marker.
7. Adjust x range, tolerance, measured peak threshold, and reference intensity threshold.
8. Use the phase ranking table, peak match table, and overlaid phase markers as manual identification aids.
9. Hide individual reference peaks when a reference peak is not visible in the measured pattern.
10. Export SVG for reports, Word, or PowerPoint, or export PNG/JPEG for image use.

## Development order

1. Manual XRD identification
2. Automatic XRD identification with peak search and phase scoring
3. MH graph creation for VSM data
4. MT/SQUID graph creation
5. Lattice constant calculation

## Build direction

This starter uses only the Python standard library for the UI so it can run on many offline Windows laptops. For a polished production app, the recommended next step is:

1. keep the parser and analysis code in pure Python modules
2. move the UI to PySide6 or Qt
3. package with PyInstaller into a single Windows app folder or single executable
4. add module tabs for XRD, VSM, MT, SQUID, and reporting

## Suggested production stack

- Python core: parsing, normalization, peak search, fitting, exports
- PySide6/Qt UI: desktop application shell
- NumPy/SciPy: numerical processing and fitting
- Matplotlib or pyqtgraph: plotting
- PyInstaller: distribution to lab PCs

## Supplied workflow references

The supplied PDFs are summarized in:

```text
docs/pdf_workflow_requirements.md
```
