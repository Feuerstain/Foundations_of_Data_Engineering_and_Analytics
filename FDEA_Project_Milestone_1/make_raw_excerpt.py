"""Write the CT7 raw-data excerpt that 00_extraction.ipynb reads (provenance only).

Run once from the folder that contains this script, on the local copy of the CTM telemetry storage
(~/Data/CT7/app, which it only reads). Graders and team members do not need it: the excerpt it writes is part of
the project package. It applies the same file selection, 100 ms thinning and activity rule as
00_extraction.ipynb and keeps, per session, the original candump lines of

- every thinned, well-formed frame of the 10 wanted CAN messages inside an activity period, and
- the earliest thinned frame of these messages in the file (also outside activity periods), which fixes
  the session's time origin (t_s = 0).

From these lines 00_extraction.ipynb reproduces the extracted values exactly. Counts that need the whole
log file (all lines, malformed lines, frames with another length, thinned frames outside activity, clock
gaps) cannot be recomputed from the excerpt; they are written to ct7_scan_stats.csv as provenance.

Outputs in data/: raw/S###.log.xz, ct7_signals.dbc (the 10 message definitions taken from ctm.dbc with
cantools; IDs, bit layouts, scale, offset and unit unchanged), ct7_scan_stats.csv, ct7_archive_summary.csv.
"""
import csv
import lzma
import logging
from bisect import bisect_right
from pathlib import Path

import cantools

RAW = Path.home() / "Data" / "CT7" / "app"
LOGS = RAW / "logs"
FIRST_DAY = "2025-05-26"
ACTIVE_RPM = 100
PAD_S = 30
OUT = Path("data")

SIGNALS = [  # identical to 00_extraction.ipynb
    ("can-inv", "amk_fl_actual_values_1", {"actual_velocity": "rpm_fl"}),
    ("can-inv", "amk_fr_actual_values_1", {"actual_velocity": "rpm_fr"}),
    ("can-inv", "amk_rl_actual_values_1", {"actual_velocity": "rpm_rl"}),
    ("can-inv", "amk_rr_actual_values_1", {"actual_velocity": "rpm_rr"}),
    ("can-main", "pedals", {"accel": "accel_pct", "brake": "brake_pct", "regen": "regen_pct"}),
    ("can-main", "vcu_front_status", {"steering_angle": "steer_deg"}),
    ("can-main", "isa_current", {"value": "isa_current_a"}),
    ("can-main", "isa_ubat", {"value": "isa_voltage_v"}),
    ("can-main", "isa_power", {"value": "isa_power_w"}),
    ("can-main", "ams_ts_on_state", {"max_temp": "cell_temp_max_c"}),
]


def active_periods(times):
    periods = []
    for t in times:
        if periods and t - PAD_S <= periods[-1][1]:
            periods[-1][1] = t + PAD_S
        else:
            periods.append([t - PAD_S, t + PAD_S])
    return periods


def inside(t, periods, starts):
    i = bisect_right(starts, t) - 1
    return i >= 0 and t <= periods[i][1]


def scan(path, wanted):
    """The read_session logic of 00_extraction.ipynb, keeping the original line of every thinned frame."""
    frames, seen = [], set()
    stats = dict(lines=0, malformed_lines=0, dlc_mismatch=0, forward_gaps_over_60s=0, backward_steps_over_1s=0)
    prev = None
    with open(path, errors="replace") as f:
        for line in f:
            stats["lines"] += 1
            parts = line.split()
            if len(parts) != 3 or parts[2].count("#") != 1 or len(parts[0]) != 19:
                stats["malformed_lines"] += 1
                continue
            t = float(parts[0][1:-1])
            can_id, payload = parts[2].split("#")
            if prev is not None and t - prev > 60:
                stats["forward_gaps_over_60s"] += 1
            if prev is not None and t - prev < -1:
                stats["backward_steps_over_1s"] += 1
            prev = t
            key = (parts[1], can_id)
            if key not in wanted or (key, int(t * 10)) in seen:
                continue
            if len(payload) != 2 * wanted[key][0].length:  # counted only while the 100 ms slot has no valid frame
                stats["dlc_mismatch"] += 1
                continue
            seen.add((key, int(t * 10)))
            frames.append((t, key, payload, line))
    stats["frames_kept"] = len(frames)
    if not frames:
        return [], stats
    active = []
    for t, key, payload, _ in frames:
        msg, columns = wanted[key]
        values = msg.decode(bytes.fromhex(payload), decode_choices=False)
        active += [t for sig, col in columns.items() if col.startswith("rpm_") and abs(values[sig]) > ACTIVE_RPM]
    periods = active_periods(sorted(active))
    starts = [a for a, _ in periods]
    first = min(range(len(frames)), key=lambda i: frames[i][0])
    keep = [line for i, (t, _, _, line) in enumerate(frames) if i == first or inside(t, periods, starts)]
    return (keep if periods else []), stats


def main():
    logging.getLogger("cantools").setLevel(logging.ERROR)
    full = cantools.database.load_file(RAW / "ctm.dbc")
    messages = [full.get_message_by_name(name) for _, name, _ in SIGNALS]
    (OUT / "raw").mkdir(parents=True, exist_ok=True)
    cantools.database.dump_file(cantools.database.can.Database(messages=messages), OUT / "ct7_signals.dbc")
    wanted = {(bus, f"{m.frame_id:03X}"): (m, cols) for (bus, _, cols), m in zip(SIGNALS, messages)}

    all_files = sorted(LOGS.glob("candump-*.log"))
    files = [p for p in all_files if p.name[8:18] >= FIRST_DAY and p.stat().st_size > 0]
    with open(OUT / "ct7_archive_summary.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["item", "value"])
        w.writerows([["log files", len(all_files)],
                     ["empty files", sum(p.stat().st_size == 0 for p in all_files)],
                     ["files before " + FIRST_DAY, sum(p.name[8:18] < FIRST_DAY for p in all_files)],
                     ["files selected", len(files)],
                     ["bytes selected", sum(p.stat().st_size for p in files)]])

    rows = []
    for i, path in enumerate(files, 1):
        sid = f"S{i:03d}"
        lines, stats = scan(path, wanted)
        if lines:
            with lzma.open(OUT / "raw" / f"{sid}.log.xz", "wt", preset=9) as f:
                f.writelines(lines)
        rows.append({"session_id": sid, "file_date": path.name[8:18], "bytes": path.stat().st_size,
                     "excerpt_lines": len(lines), **stats})
        print(sid, path.name[8:18], stats["lines"], "lines,", len(lines), "in the excerpt", flush=True)
    with open(OUT / "ct7_scan_stats.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


if __name__ == "__main__":
    main()
