Proviral Landscape Plot
=======================

What this tool does
-------------------
This module (`proviral_landscape_plot.py`) reads a CSV produced by the proviral pipeline and produces an SVG visualization that shows, per-sample, the genomic regions that are intact or affected by different defect types. It groups entries by defect category, sorts samples within each category by gap structure, draws primers and gene segments as horizontal tracks, and renders a legend and a sidebar with defect percentages.

Quick run
---------
This directory is a standalone uv project, so the CLI needs nothing but `uv`:
no docker image, no bblab_site virtualenv. Run it from anywhere with:

    uv run --project <this directory> --frozen proviral_landscape_plot <csv> [<csv> ...] <output_svg>

`--project` points uv at this directory, so the first run creates `.venv` here
from the committed `uv.lock` and every later run reuses it. Drop `--frozen` if
you want uv to re-resolve the dependencies. If you prefer a one-liner in the
shell:

    uv tool install <this directory>   # then just: proviral_landscape_plot ...

To plot the example inputs from the sibling `other` checkout there are two
wrapper scripts on the PATH:

    ws-make-plot                          # plot the example inputs, print the svg path
    ws-make-plot-examples [output.svg]    # the same, with an explicit output path
    ws-make-plot a.csv b.csv out.svg      # plot whatever you pass instead

The output file always goes last, after the input csvs.

Give one csv per plot. With a single csv you get the classic single plot with
its own legend and a percentage sidebar. With several csvs all plots are drawn
on one page in a grid of 3 columns (however many rows that takes), sharing one
legend placed at the bottom center of the page. Every plot keeps its own
percentage sidebar.

Every plot on a page is given exactly the same height, so the proportions of the
defect categories can be compared directly between plots. A plot with many
samples gets thinner sample tracks than a plot with few. Each plot is titled
with its input file name, with its sample count printed underneath.

Example:

uv run --project . --frozen proviral_landscape_plot input.csv output.svg

uv run --project . --frozen proviral_landscape_plot participant_1.csv participant_2.csv participant_3.csv output.svg

uv run --project . --frozen proviral_landscape_plot -c 2 a.csv b.csv c.csv output.svg

Running `python proviral_landscape_plot.py ...` against a checkout still works
as long as `drawsvg` and `genetracks` are importable.

Paper size and raster output
----------------------------
A page of several plots is laid out for a sheet of A4 in landscape by default.
The drawing declares that physical size (`width="297mm" height="210mm"`), so it
prints at the right dimensions and rasterizes at whatever resolution is asked
for. The plots, the gaps between them and the text are all scaled onto the
paper together, which is why the fonts keep a readable size however many plots
share the page.

`--dpi 300` writes a raster image instead of an svg. The format comes from the
output file name: a `.tif`/`.tiff` output is a TIFF (LZW compressed, tagged
with the resolution), anything else is a PNG. This needs two extra packages,
which are in the `raster` extra:

    uv run --project . --frozen --extra raster proviral_landscape_plot \
        -c 4 --dpi 300 a.csv b.csv c.csv d.csv page.tiff

Without `--extra raster` an svg is written, which is the normal case.

Options:

- `-c`/`--columns` : number of plots per row (default 3)
- `--title-column COLUMN` : take each plot's title from that csv column
  instead of from the input file name. The title is the participant number
  that every sample name in the file starts with, so
  `0380X00415ANFL11M11-NFLHIVDNA_S158` is titled `0380`. Sample names that
  are not participant-numbered (a control, or a lab code such as
  `Y04589ASGA-...`) are ignored; if what is left is ambiguous, the input file
  name is used as before.
- `--titles KEY=TITLE[,KEY=TITLE...]` : set the titles explicitly. `KEY` is
  the input file stem, the participant number in the file name, or the
  participant number in the sample names. These win over `--title-column`,
  which is what you want when the titles are lab codes rather than
  participant numbers, e.g.
  `--titles 0913=BC023,0380=BC016,1094=BC024`
- `--legend-font-size PX` : font size of the shared legend (default 15). The
  legend grows to fit, so a bigger number is fine on a page of several plots.
- `--page-size NAME` : paper the page is laid out for, `a4-landscape` (the
  default), `a4-portrait`, or `fit` to let the page grow to fit its content
  with no fixed physical size.
- `--dpi DPI` : write a raster image (tiff for a `.tif`/`.tiff` output name,
  png otherwise) at this resolution instead of an svg. Needs the `raster`
  extra; see above.

Required CSV columns
------------------------------------------
- `samp_name` : sample identifier
- `ref_start` : integer, start coordinate in reference
- `ref_end`   : integer, end coordinate in reference
- `defect`    : defect key (mapped via `DEFECT_TYPE`)
- `is_defective` : flag (string) used to detect defect-region highlighting
  - Accepted TRUE values (case-insensitive): `1`, `true`, `t`, `yes`, `y`
  - Accepted FALSE values (case-insensitive): `0`, `false`, `f`, `no`, `n`, or empty string
- `is_inverted`  : flag (string) used to detect inversion highlighting
  - Accepted TRUE values (case-insensitive): `1`, `true`, `t`, `yes`, `y`
  - Accepted FALSE values (case-insensitive): `0`, `false`, `f`, `no`, `n`, or empty string

A csv that is missing any of these columns is rejected with an error naming the
missing ones, rather than producing an empty plot.

Reading is forgiving about the things spreadsheets add: a utf-8 byte order
mark, whitespace around the header names (` samp_name` is fine), short final
lines and blank trailing lines are all tolerated.
