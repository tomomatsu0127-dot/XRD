# Development Notes

## Why this is not just an HTML wrapper

The original HTML app is useful as a prototype, but the target product is a local desktop analysis suite. For long-term growth, the app should separate:

- data import
- analysis
- plotting
- project/session state
- export
- UI

This makes it possible to add VSM, MT, SQUID, and other measurement modules without rewriting the XRD code.

## Proposed architecture

```text
labplot_studio/
  main.py              desktop app entry point
  models.py            shared data classes
  parsers.py           text/csv measurement and reference parsing
  xrd.py               XRD-specific normalization and filters
  exporters.py         CSV/SVG/export helpers
```

## Milestones

1. Desktop MVP
   - XRD file load
   - stacked plot
   - reference markers
   - SVG/CSV export

2. XRD analysis
   - automatic peak detection
   - unknown peak list
   - hkl label collision avoidance
   - phase matching score

3. Lattice parameter tools
   - peak fitting
   - d-spacing calculation
   - lattice constant estimation
   - error table export

4. Magnetization modules
   - VSM M-H loop import
   - coercivity, remanence, saturation estimates
   - MT/SQUID M-T curve import
   - transition temperature and anomaly detection

5. Distribution
   - PySide6 UI
   - PyInstaller build
   - sample project format
   - user manual

