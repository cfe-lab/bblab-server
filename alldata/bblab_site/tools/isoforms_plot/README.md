# isoforms_plot

Generate an SVG "isoforms / splicing map" from a structured CSV input.

This repo contains two closely related pieces:

1. **`isoforms_plot/` (library + CLI)** - parses a CSV that describes splice sites and transcript fragments, compiles it into a plot-ready representation, and renders an SVG.
2. **Django integration (web UI)** - a thin wrapper that lets users upload a CSV in a browser and view/download the resulting SVG.

The tool is designed to make isoform diagrams **consistent and comparable** by requiring transcript fragment boundaries to line up with a declared set of donor/acceptor splice sites (rather than allowing arbitrary coordinates per transcript).

---

## Quick start (CLI)

The package provides a module entrypoint:

```bash
python -m isoforms_plot INPUT.csv OUTPUT.svg
````

Under the hood this runs:

* `parser.parse()` -> validate and parse CSV into an AST
* `compiler.compile()` -> enforce semantic constraints and compute plot-ready structures
* `plotter.plot()` -> render the SVG (via `drawsvg` + `genetracks`)

---

## What the input represents (conceptual)

The CSV describes three kinds of things:

* **Splice sites**: donors and acceptors, each with a name and a position (and optional colour).
* **Transcripts**: each transcript is a list of **fragments** (exon-like blocks) expressed as `start-end` ranges.
* **Grouping / labels / comments**: optional metadata to make the figure easier to read.

A key design choice: transcript fragments are treated as **paths between declared splice sites**. That makes the plot more reliable (fewer silent typos), and makes multiple transcripts visually align on the same landmarks.

---

## Repository layout

### Core library + CLI

* `isoforms_plot/__main__.py`

  * CLI entrypoint: takes `input_csv` and `output_svg`.
* `isoforms_plot/parser.py`

  * Parses the multi-section CSV into an `AST` (`title`, `transcripts`, `donors`, `acceptors`).
  * Performs syntax/shape checks (e.g., fragment strings, missing fields, allowed colours).
* `isoforms_plot/compiler.py`

  * Converts parsed objects into plotter-friendly dataclasses (`Compiled*`).
  * Enforces semantic constraints (e.g., valid fragment boundaries, non-overlap, unique splice site names).
  * Computes group sizes and deduplicates consecutive labels for cleaner figures.
* `isoforms_plot/plotter.py`

  * Renders the final SVG drawing.
  * Contains layout logic, "genome overview" landmarks, splice site ticks/labels, group rendering, etc.
* `isoforms_plot/exceptions.py`

  * Error types intended to produce actionable feedback for users (and for the web UI).

### Django web integration

* `run_isoforms.py`

  * Web-oriented runner:

    * Accepts file-like CSV data
    * Returns a `{success, svg_path, error_message, error_details}` dict
    * Writes the SVG to a configured output path (currently hard-coded)
* `views.py`

  * Endpoints:

    * upload -> run -> show SVG or show error
    * "use example" and "download example CSV"
* `urls.py`

  * URL routes for the above
* `models.py`

  * Placeholder (no models currently)

---

## Developer usage

### As a library

Typical flow:

```python
from isoforms_plot import parser, compiler, plotter

ast = parser.parse(path_or_filelike)
compiled = compiler.compile(ast)
drawing = plotter.plot(
    compiled.transcripts,
    compiled.groups,
    compiled.splicing_sites,
    compiled.title,
)
drawing.save_svg("out.svg")
```

### Web app flow

The Django side uses `run_isoforms.run(csv_data)` where `csv_data` is a file-like object.
It renders `isoforms_plot/index.html` with either:

* `svg_path` on success, or
* `error_message` and optionally `error_details` on failure.

> Note: `run_isoforms.py` currently hard-codes an output SVG filesystem path; if you deploy this outside the original environment, you'll want to make that configurable.

---

## Dependencies

At minimum, the plotter relies on:

* `drawsvg`
* `genetracks`
* `multicsv`

The web UI additionally needs:

* `django`

The code uses modern typing features (notably `|` unions), so **Python 3.10+** is recommended.

---

## Design notes (why it's structured this way)

* **Parser vs compiler split**:

  * The parser focuses on "is this CSV well-formed?"
  * The compiler focuses on "does this describe a coherent splicing model?"
  * This keeps error reporting clearer and keeps the plotter simpler.
* **Strict boundaries**:

  * For comparability, fragments are forced to start/end on a shared set of splice sites.
  * This avoids a class of mistakes where slightly different coordinates accidentally create misleading diagrams.
* **Plotter assumptions**:

  * The plotter expects already-validated, coherent data and focuses on layout and readability.
