# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repository is

Coursework for **Foundations of Data Engineering and Analytics** (University of Innsbruck,
Dept. of Computer Science; Gassler & Zangerle, WS 2026). It is **not** a software product — it is
a semester-long collection of Jupyter-notebook solutions to exercise sheets plus a final group
project. The repo is new and currently holds only course material (`guidelines.pdf`, `01/sheet01.pdf`).

Expected layout as the semester progresses: one directory per sheet (`01/`, `02/`, …), each
containing that sheet's PDF, the solution notebook(s), and exported `.pdf`/`.html` renderings.
There are nine exercise sheets (10 pts each) and a group project (30 pts) — 120 pts total.

## Tooling (required by Sheet 1, Exercise 1)

- **Reproducible environments are graded.** The solution must run after a fresh clone/download into
  a clean environment. Use a proper dependency manager — **uv**, conda, or pipenv — and commit the
  lockfile/manifest so the environment is reconstructable. Prefer `uv` for new work.
- **Jupyter notebooks** are the deliverable format for exercises.
- Core data libraries: **pandas** or **polars** for wrangling; **Plotly/Dash**, Perspective, or Bokeh
  for interactive visualization.
- Optional quality tooling the course recommends and welcomes: **nbval** (notebook validation /
  execute-and-check), **nbQA** (run formatters, type checks, static analysis on notebooks).

### Common commands (uv-based; adjust if the active sheet uses conda/pipenv)

```bash
uv sync                      # reconstruct the environment from the lockfile
uv run jupyter lab           # launch Jupyter
uv run jupyter nbconvert --to html <notebook>.ipynb   # export deliverable
uv run jupyter nbconvert --to pdf  <notebook>.ipynb
uv run pytest --nbval <notebook>.ipynb                # validate a notebook end-to-end
uv run nbqa black . && uv run nbqa ruff .             # format / lint notebooks
```

Reproducibility check before submitting: run the notebook top-to-bottom in a fresh kernel
("Restart & Run All") and confirm every cell executes without manual intervention.

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
