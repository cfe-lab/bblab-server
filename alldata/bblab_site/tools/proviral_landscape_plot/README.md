Proviral Landscape Plot
=======================

What this tool does
-------------------
This module (`proviral_landscape_plot.py`) reads a CSV produced by the proviral pipeline and produces an SVG visualization that shows, per-sample, the genomic regions that are intact or affected by different defect types. It groups entries by defect category, sorts samples within each category by gap structure, draws primers and gene segments as horizontal tracks, and renders a legend and a sidebar with defect percentages.

Quick run
---------
From the command line:

python proviral_landscape_plot.py <proviral_landscape_csv> <output_svg>

Example:

python proviral_landscape_plot.py input.csv output.svg

Required CSV columns
------------------------------------------
- `samp_name` : sample identifier
- `ref_start` : integer, start coordinate in reference
- `ref_end`   : integer, end coordinate in reference
- `defect`    : defect key (mapped via `DEFECT_TYPE`)
- `is_defective` : flag (string) used to detect defect-region highlighting
- `is_inverted`  : flag (string) used to detect inversion highlighting
