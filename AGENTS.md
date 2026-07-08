# LabPlot Studio Project Instructions

## Goal

Build a local, offline-capable desktop application for laboratory measurement analysis.

The first module is XRD. Future modules should support VSM, MT, SQUID, and related measurement formats.

## Product direction

- Treat this as a standalone desktop app, not a web-only HTML app.
- The app should be usable on lab laptops without a server.
- Prefer a modular architecture inspired by Igor-style workflows:
  - import raw measurement files
  - clean and normalize data
  - compare multiple datasets
  - annotate and identify peaks or characteristic values
  - export publication-ready figures and tables

## Current module: XRD

Preserve support for:

- Bruker-style `.xy` files
- generic two-column measured data: `2theta intensity`
- reference peak files with columns such as:
  - `d 2theta I fix h k l`
  - `2theta I h k l`
- measured data normalization by subtracting min and scaling max to 100
- reference phase normalization to max intensity 100
- multiple measured datasets
- multiple reference phases
- orientation filters: all, h00, 0k0, 00l, hk0, h0l, 0kl
- SVG export for Word and PowerPoint
- CSV export for processed data

## Future modules

- XRD phase identification and unknown peak detection
- lattice parameter calculation
- VSM hysteresis loop processing
- MT / SQUID temperature-dependent magnetization processing
- report and figure template export

## Reference workflows

Use `docs/pdf_workflow_requirements.md` as the project-level summary of the supplied laboratory PDF instructions. The app should preserve the Igor-like workflow while removing repetitive manual steps.

## Development rules

- Keep parsing and analysis logic independent from the UI.
- Add tests for parsers and numerical logic before changing behavior.
- Do not require internet access at runtime.
- Avoid putting lab-specific sample data into source code.
- Keep a path toward single-machine Windows distribution.
