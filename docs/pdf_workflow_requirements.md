# PDF Workflow Requirements

These notes summarize the laboratory workflows extracted from the supplied PDFs on 2026-07-08.

Some Japanese text in the XRD PDF is embedded with fonts that do not extract cleanly, and the lattice-constant PDF appears to be image-based. The requirements below use the readable menu names, numerical settings, formulas, and the clearly extractable VSM procedure.

## XRD graph workflow

Source: `XRD_instruction.pdf`

The app should automate the Igor-style graph preparation steps:

- import Bruker-style `.xy` measured XRD data
- import reference peak tables exported from PDF/JCPDS/JADE-like sources
- support reference columns containing `2theta`, `d`, intensity, and `h k l`
- normalize measured intensity by:
  - subtracting the minimum intensity
  - dividing by `(max - min)`
  - multiplying by 100
- use publication-like plot defaults:
  - figure size equivalent to 12 cm x 9 cm
  - Times New Roman-style export typography where possible
  - y-axis label: `Intensity (arb. units)`
  - x-axis label: `2theta`
  - mirrored axes
  - inside ticks
- support stacked traces with a default y offset near 125
- support reference peak display as sticks/markers
- support reference hkl annotations and legends
- support graph reuse/templates so another sample can be plotted with the same formatting

## XRD identification workflow

Source: `XRD_instruction.pdf`

The app should eventually automate:

- selecting unknown peaks from measured XRD
- comparing unknown peak positions with reference peaks
- deleting or hiding irrelevant candidate reference peaks
- placing reference sticks in a chosen 2theta range, such as 10 to 70 degrees
- adding annotations/legends for candidate phases
- avoiding hkl label overlap
- exporting the final graph for reports, Word, and PowerPoint

## Lattice constant workflow

Sources: `XRD_instruction.pdf`, `格子定数の求め方.pdf`

The readable formula in the XRD instruction indicates a correction/fit workflow using:

```text
z = A x + B y + C
```

with terms based on:

```text
sin(theta)
(h^2 + h k + k^2) * lambda^2 / (6 sin(theta) cos^2(theta))
l^2 * lambda^2 / (8 sin(theta) cos^2(theta))
```

The app should therefore provide a lattice-constant module that can:

- take selected measured peak positions
- attach h, k, l indices
- convert 2theta to theta in radians
- compute correction terms
- fit coefficients by least squares
- estimate lattice constants `a` and `c`
- export a table containing peak position, hkl, calculated terms, fit result, and residual

The `格子定数の求め方.pdf` file needs visual/OCR review because plain text extraction returned blank pages.

## VSM workflow

Source: `VSM.pdf`

The VSM module should automate the Igor procedure:

- load delimited text VSM data
- support files where:
  - column labels are around line 41
  - data starts around line 42
  - the first column is date/time
  - the second column is magnetic field
  - the third column is magnetization
  - the fourth column is angle
- skip non-analysis columns such as date/time and fixed angle
- name imported waves/series using sample metadata:
  - `H_***`
  - `M_***`
  - sample id, composition, firing temperature, milling condition
- convert magnetization to mass-normalized units:
  - `M = M / sample_mass`
  - unit: `emu/g`
- convert magnetic field:
  - `H = H / 1000`
  - unit: `kOe`
- generate an M-H plot:
  - y-axis: `Magnetization (emu/g)`
  - x-axis: `Magnetic field (kOe)`
  - default axis range example: y = -70 to +70 emu/g, x = -15 to +15 kOe
  - figure size equivalent to 12 cm x 9 cm
  - Times New Roman-style typography
  - mirrored axes
  - inside ticks
  - zero lines on both axes
- add annotations for composition, sample number, heat treatment, and milling condition
- reuse the same graph template for later samples by replacing the sample identifier

## Product implication

The app should become an Igor-like laboratory plotting and analysis suite:

- XRD manual identification module first
- automatic XRD identification module after manual workflows are stable
- lattice constant module
- VSM module
- later MT/SQUID modules
- shared figure styling presets
- reusable graph templates
- project/session save files

## Current build target

The immediate target is manual XRD identification:

- measured `.xy` files are loaded as black measured traces
- reference `.txt` files are kept in a library folder and added when needed
- selected references are shown as colored stick rows
- selected references can be shown as colored symbols over measured peaks
- reference labels, colors, and marker symbols can be edited by the user
- multiple references are distinguished by color and phase name
- candidate matches are calculated from measured peak positions and reference peaks within a tolerance
- later automatic identification should build on the same reference library and matching logic
