# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repository is

Coursework for **Foundations of Data Engineering and Analytics** (University of Innsbruck,
Dept. of Computer Science; Gassler & Zangerle, WS 2026). It is **not** a software product — it is
a semester-long collection of Jupyter-notebook solutions to exercise sheets plus a final group
project. There are nine exercise sheets (10 pts each) and a group project (30 pts) — 120 pts total.

## Layout and conventions (established by Sheet 1 — follow them for later sheets)

One directory per sheet (`01/`, `02/`, …), one uv environment at the repo root shared by all sheets:

- `NN/sheetNN.pdf` — the **assignment** (Angabe) from the course. Not a solution export —
  never overwrite it (a naive `nbconvert --to pdf NN/sheetNN.ipynb` would do exactly that).
- `NN/sheetNN.ipynb` — the solution; `NN/sheetNN.html` — its export, committed alongside.
- `NN/data/` — datasets are **committed locally** so the notebook runs offline and reproducibly.
  Notebooks load them via paths relative to the notebook's own directory (`data/...`), so they
  must be executed with the sheet directory as CWD (Jupyter and nbconvert both do this).
- `README.md` (German) holds the setup instructions, version table, project tree and the
  per-sheet submission checklist. Update its tree and version table when adding a sheet or a dependency.

Notebook conventions:

- **Prose and code comments are in German**; keep that consistent within and across notebooks.
- Each notebook is structured by the sheet's exercises (`## Exercise N – … [P]`, `### a) …`) and
  answers the reflection/explanation questions in markdown, not just with code.
- Plotly is the visualization library. Set `pio.renderers.default = "notebook"` so plotly.js is
  embedded and the exported HTML stays interactive offline. For interactivity use Plotly's own
  controls (`updatemenus`, `rangeslider`) rather than `ipywidgets` — widgets need a live kernel and
  are dead in the submitted HTML.
- Inspect raw data files before parsing (separator, encoding, BOM, date formats, trailing spaces in
  headers) and document the findings in a comment. Sheet 1's CSV is UTF-8 **with BOM** → `utf-8-sig`;
  guessing `cp1252` silently produced mojibake.

## Tooling (required by Sheet 1, Exercise 1)

- **Reproducible environments are graded.** The solution must run after a fresh clone/download into
  a clean environment. Use a proper dependency manager — **uv**, conda, or pipenv — and commit the
  lockfile/manifest so the environment is reconstructable. Prefer `uv` for new work.
- **Jupyter notebooks** are the deliverable format for exercises.
- Core data libraries: **pandas** or **polars** for wrangling; **Plotly/Dash**, Perspective, or Bokeh
  for interactive visualization.
- Optional quality tooling the course recommends and welcomes: **nbval** (notebook validation /
  execute-and-check), **nbQA** (run formatters, type checks, static analysis on notebooks).

### Common commands

The project uses **uv** (Python pinned to 3.13 via `.python-version`; deps in `pyproject.toml`,
exact versions in `uv.lock`). Add packages with `uv add <pkg>` so both files stay in sync.

```bash
uv sync                                    # reconstruct the environment from uv.lock
uv run jupyter lab                         # launch Jupyter

# Headless "Restart & Run All": execute in place, then export the stored outputs to HTML
uv run jupyter nbconvert --to notebook --execute --inplace NN/sheetNN.ipynb
uv run jupyter nbconvert --to html NN/sheetNN.ipynb
```

- `nbconvert --to html` without `--execute` only renders the outputs **already saved** in the
  `.ipynb` — execute first, or the HTML can be stale.
- Prefer HTML as the export: it keeps Plotly charts interactive. PDF export needs pandoc (not
  installed; MiKTeX/xelatex is) and renders Plotly figures poorly. If ever needed, write it to a
  different name (`--output sheetNN_solution`) so the assignment PDF is not overwritten.
- nbval / nbQA / ruff / black are recommended by the course but **not yet dependencies**. Add them
  as dev deps before use: `uv add --dev pytest nbval nbqa ruff black`, then
  `uv run pytest --nbval-lax NN/sheetNN.ipynb` (plain `--nbval` also compares outputs, which fails
  on Plotly's embedded HTML) and `uv run nbqa ruff NN/`.

### Environment gotchas (Windows)

- If `uv run jupyter …` fails with *"uv trampoline failed to canonicalize script path"*, the
  repo folder was renamed or moved after `.venv` was created — its `.exe` launchers hard-code the
  old absolute path. Delete `.venv` and run `uv sync`. `uv run python -m nbconvert …` works meanwhile.
- The console encoding is cp1252: when printing notebook JSON or German data from a script, use
  `python -X utf8` (or `PYTHONIOENCODING=utf-8`), otherwise umlauts/BOM raise `UnicodeEncodeError`.

## Submission rules (these shape how work must be delivered)

- **Deadline:** every **Tuesday 23:59** via **OLAT** (the day before the Wednesday tutorial). Also
  tick the solved-exercise checkboxes in OLAT — the submitted file alone is not enough.
- **Deliverables per exercise:** the `.ipynb` **and** an exported `.pdf` or `.html` of the notebook.
- **Teams** (max 3 people): add a `team.txt` listing all members. Every member must submit
  individually in OLAT and tick their own checkboxes.
- A positive grade also requires presenting successfully ≥2× in the tutorial and ≤2 absences —
  so solutions must be ones Luca can explain and defend live.

## AI policy — read before generating solution content

AI tools are explicitly **allowed** for this course (ideation, programming, data analysis, literature
search, editing, etc.), **but the student remains fully responsible and must understand everything
submitted.** If selected to present, they must explain and justify the solution and answer questions;
failure to demonstrate understanding voids the presentation and can cost exercise points.

Practical implication for how to help here: **favor clarity and learning over cleverness.** Prefer
straightforward, well-commented, idiomatic solutions that Luca can read, follow, and defend. Explain
the reasoning and the choices (why this library, why this approach), not just the code. Avoid opaque
one-liners or advanced tricks that would be hard to explain in a live tutorial.
