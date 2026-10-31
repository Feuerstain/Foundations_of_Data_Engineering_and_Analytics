# Foundations of Data Engineering and Analytics

Kursarbeit (Übungsblätter + Gruppenprojekt) für die LV *Foundations of Data
Engineering and Analytics*, Universität Innsbruck, WS 2026.
Bearbeitung: **Luca Jenewein**.

## Projektstruktur

```text
Foundations_of_Data_Engineering_and_Analytics/
├── 01/                       # Sheet 1 – Datasets
│   ├── sheet01.ipynb         # Lösung (Ex 1–3)
│   ├── sheet01.html          # Export für OLAT (interaktive Plotly-Grafiken)
│   ├── sheet01.pdf           # Angabe
│   └── data/
│       └── radverkehrszaehlungen_wien.csv   # Datensatz (lokal, offline-reproduzierbar)
├── 02/                       # Sheet 2 – Data Preparation & Data Quality
│   ├── sheet02.ipynb         # Lösung
│   ├── sheet02.html          # Export für OLAT
│   ├── sheet02.pdf           # Angabe
│   └── data/spotify_modified.json   # Datensatz (aus OLAT)
├── 03/                       # Sheet 3 – Web Crawling & Univariate EDA
│   ├── sheet03.ipynb         # Übungsversion: Ex 2 mit Aufgabe/Tipp, Lösung auskommentiert
│   ├── sheet03_abgabe.ipynb  # fertige Lösung (Abgabe)
│   ├── sheet03_abgabe.html   # Export für OLAT
│   ├── sheet03.pdf           # Angabe
│   ├── crawler.py            # Playwright-Crawler für DevHire Europe
│   └── data/                 # Rohdaten (jobs_raw.jsonl) + bereinigt (jobs_2026.csv, job_technologies.csv)
├── VO-Folien/                # Vorlesungsfolien (DEA-NN-<Thema>.pdf)
├── pyproject.toml            # Abhängigkeiten
├── uv.lock                   # exakte, gepinnte Paketversionen
├── .python-version           # Python-Version des Projekts
└── guidelines.pdf            # Kurs-Organisation & Bewertung
```

## Umgebung einrichten & starten

Die Umgebung wird mit **[uv](https://docs.astral.sh/uv/)** verwaltet. `uv.lock`
fixiert die exakten Paketversionen, sodass jeder Klon dieselbe Umgebung erhält
(Reproduzierbarkeit – siehe Sheet 1, Exercise 1).

```bash
# 1. uv installieren (falls noch nicht vorhanden)
#    Windows (PowerShell):
#    irm https://astral.sh/uv/install.ps1 | iex
#    macOS/Linux:
#    curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Umgebung aus uv.lock reproduzieren
uv sync

# 3. JupyterLab starten
uv run jupyter lab
```

Danach `01/sheet01.ipynb` öffnen und **Kernel → Restart Kernel and Run All Cells**
ausführen. Läuft von oben nach unten ohne manuelle Eingriffe durch.

### Notebook exportieren (für die OLAT-Abgabe)

```bash
uv run jupyter nbconvert --to html 01/sheet01.ipynb   # interaktive Grafiken bleiben erhalten
uv run jupyter nbconvert --to pdf  01/sheet01.ipynb   # statische PDF-Variante
```

## Versionen

| Komponente | Version |
|------------|---------|
| Python     | 3.13.5  |
| uv         | 0.12.23 |
| pandas     | 3.0.6   |
| plotly     | 7.1.0   |
| jupyterlab | 4.6.4   |
| ipywidgets | 8.1.9   |
| scipy      | 1.18.1  |
| playwright | 1.64.1  |

Für den Crawler aus Sheet 3 braucht Playwright zusätzlich einen Browser:
`uv run playwright install chromium`. Das Notebook selbst läuft auch ohne,
weil die gecrawlten Daten in `03/data/` liegen.

(Verbindlich sind die in `uv.lock` gepinnten Versionen; `pyproject.toml` listet
die direkten Abhängigkeiten.)

## Neues Paket hinzufügen

```bash
uv add <paketname>     # installiert + aktualisiert pyproject.toml und uv.lock
```

## Abgabe-Checkliste (pro Sheet)

- [ ] Notebook läuft via *Restart & Run All* fehlerfrei durch
- [ ] `.ipynb` **und** `.html`/`.pdf` nach OLAT hochgeladen
- [ ] Gelöste Aufgaben in OLAT angehakt
- [ ] Deadline: Dienstag 23:59 (Tag vor dem Tutorium)
