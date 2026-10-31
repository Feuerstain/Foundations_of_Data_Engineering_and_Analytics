"""Crawler für DevHire Europe (Sheet 3, Exercise 1b).

Ablauf:
1. Listenseite /jobs?page=N mit einem Headless-Browser laden (die Seite wird per JavaScript
   gerendert, ein einfacher HTTP-Request liefert nur eine leere Hülle).
2. Auf jede der 24 Anzeigen klicken, die Felder über ihre data-field-Attribute auslesen und
   zurück zur Liste gehen. Diese Klicks passieren innerhalb der App und schicken keine
   Requests an den Server.
3. Jede Anzeige sofort als eine Zeile an eine JSONL-Datei anhängen. Bei einem Neustart werden
   bereits gespeicherte job_ids übersprungen (Wiederaufnahme nach Abbruch).

Starten (im Ordner 03/):  uv run python crawler.py
"""

import json
import time
from datetime import datetime
from pathlib import Path

from playwright.sync_api import TimeoutError, sync_playwright

BASE_URL = "https://devhire-europe.pages.dev"
# Ehrlicher User-Agent: zeigt dem Betreiber, wer crawlt und wozu
USER_AGENT = "FDEA-student-crawler/1.0 (Uni Innsbruck, course Data Engineering and Analytics)"
LAST_PAGE = 50          # 1.200 Anzeigen / 24 pro Seite
WAIT_AFTER_LOAD_S = 1.5  # robots.txt verlangt Crawl-delay: 1 -> wir warten etwas länger
WAIT_AFTER_CLICK_S = 0.3  # In-App-Klick ohne Server-Request: kurze Pause zum Rendern
MAX_TRIES = 3

# Einfache Felder, die auf der Detailseite als data-field="..." markiert sind
FIELDS = [
    "job_id", "survey_year", "title", "role_family", "seniority",
    "company_name", "company_size", "industry", "country", "city", "work_mode",
    "required_experience_years", "salary_min_eur", "salary_max_eur", "salary_disclosed",
    "posted_at",
]


def load_done_ids(out_file):
    """job_ids, die schon in der Ausgabedatei stehen (für die Wiederaufnahme)."""
    done = set()
    if Path(out_file).exists():
        with open(out_file, encoding="utf-8") as f:
            for line in f:
                done.add(json.loads(line)["job_id"])
    return done


def log_failure(fail_file, page_no, job_id, reason):
    with open(fail_file, "a", encoding="utf-8") as f:
        f.write(f"{datetime.now().isoformat(timespec='seconds')};{page_no};{job_id};{reason}\n")


def open_listing(page, page_no, fail_file):
    """Listenseite laden. Bei 429/5xx warten und erneut versuchen, bei 403 abbrechen."""
    for attempt in range(1, MAX_TRIES + 1):
        try:
            response = page.goto(f"{BASE_URL}/jobs?page={page_no}", wait_until="networkidle")
        except TimeoutError:
            log_failure(fail_file, page_no, "", f"timeout (Versuch {attempt})")
            time.sleep(10 * attempt)
            continue

        if response.status == 200:
            page.wait_for_selector("a.job-title-link")
            time.sleep(WAIT_AFTER_LOAD_S)
            return True
        if response.status == 403:
            # data-use: bei verweigertem Zugriff aufhören und die Kursleitung kontaktieren
            raise SystemExit("403 Forbidden - Crawl gestoppt, nicht umgehen!")

        # 429 Too Many Requests oder Serverfehler: Retry-After respektieren
        wait = int(response.headers.get("retry-after", 30 * attempt))
        log_failure(fail_file, page_no, "", f"HTTP {response.status}, warte {wait} s")
        time.sleep(wait)
    return False


def read_job(page, job_id):
    """Auf eine Anzeige klicken, alle Felder auslesen und zurück zur Liste gehen."""
    page.click(f'a[href="/jobs/{job_id}"]')
    page.wait_for_selector(f'[data-field="job_id"]:text-is("{job_id}")')

    job = {}
    for field in FIELDS:
        element = page.query_selector(f'[data-field="{field}"]')
        job[field] = element.inner_text().strip() if element else None
    # Technologien sind mehrere <li> -> als Liste speichern
    tags = page.query_selector_all('[data-field="technologies"] li')
    job["technologies"] = [tag.inner_text().strip() for tag in tags]

    page.go_back()
    page.wait_for_selector("a.job-title-link")
    time.sleep(WAIT_AFTER_CLICK_S)
    return job


def crawl(pages, out_file, fail_file):
    """Crawlt die angegebenen Listenseiten. Gibt die Zahl der Server-Requests zurück."""
    done = load_done_ids(out_file)
    requests_sent = []

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(user_agent=USER_AGENT)
        page.on("request", lambda request: requests_sent.append(request.url))

        for page_no in pages:
            if not open_listing(page, page_no, fail_file):
                log_failure(fail_file, page_no, "", "Listenseite nicht erreichbar")
                continue

            links = page.eval_on_selector_all(
                "a.job-title-link", "els => els.map(e => e.getAttribute('href'))")
            job_ids = [link.split("/")[-1] for link in links]
            print(f"Seite {page_no}: {len(job_ids)} Anzeigen, schon gespeichert: "
                  f"{sum(j in done for j in job_ids)}")

            for job_id in job_ids:
                if job_id in done:
                    continue
                try:
                    job = read_job(page, job_id)
                except TimeoutError:
                    log_failure(fail_file, page_no, job_id, "timeout auf Detailseite")
                    open_listing(page, page_no, fail_file)  # zurück auf einen sauberen Stand
                    continue

                job["listing_page"] = page_no
                job["crawled_at"] = datetime.now().isoformat(timespec="seconds")
                # sofort anhängen -> bei einem Abbruch geht nichts verloren
                with open(out_file, "a", encoding="utf-8") as f:
                    f.write(json.dumps(job, ensure_ascii=False) + "\n")
                done.add(job_id)

        browser.close()
    return len(requests_sent)


if __name__ == "__main__":
    start = time.time()
    n_requests = crawl(range(1, LAST_PAGE + 1), "data/jobs_raw.jsonl", "data/crawl_failures.log")
    print(f"Fertig in {time.time() - start:.0f} s, {n_requests} Requests an den Server")
