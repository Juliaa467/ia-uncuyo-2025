#!/usr/bin/env python3
import itertools
import csv
import time
from pathlib import Path
import importlib.util
from statistics import mean

# --- Pfade anpassen ---
SERVER_URL = "http://localhost:5000"

# Dein Reflex-Agent
REFLEX_AGENT_FILE = "student_agents/student_julia_kroepfl_agent.py"
# RandomAgent – Pfad ggf. anpassen (liegt z.B. in student_agents/random-agent.py)
RANDOM_AGENT_FILE = "student_agents/random-agent.py"

# --- run_agent.py-Hilfsfunktionen laden ---
RUNNER_PATH = Path("run_agent.py").resolve()
spec = importlib.util.spec_from_file_location("runner", str(RUNNER_PATH))
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)
load_agent_from_file = runner.load_agent_from_file
run_single_agent = runner.run_single_agent

# --- Testmatrix ---
SIZES = [(2, 2), (4, 4), (8, 8), (16, 16), (32, 32), (64, 64), (128, 128)]
DIRT_RATES = [0.1, 0.2, 0.4, 0.8]
SEEDS = list(range(1, 11))  # 10 Seeds: 1..10

ENABLE_UI = False
RECORD = False
VERBOSE = False

def run_suite(agent_file, agent_label, out_rows):
    agent_class = load_agent_from_file(agent_file)
    for (sx, sy), dirt, seed in itertools.product(SIZES, DIRT_RATES, SEEDS):
        res = run_single_agent(
            agent_class=agent_class,
            server_url=SERVER_URL,
            size_x=sx,
            size_y=sy,
            dirt_rate=dirt,
            verbose=VERBOSE,
            agent_id=0,
            enable_ui=ENABLE_UI,
            record_game=RECORD,
            replay_file=None,
            cell_size=60,
            fps=10,
            auto_exit_on_finish=True,
            live_stats=False,
            seed=seed
        )

        # Metriken extrahieren:
        cells_cleaned = res.get("performance")              # = gereinigte Zellen (Score)
        actions = res.get("total_actions")                  # = verbrauchte Aktionen
        out_rows.append({
            "agent": agent_label,
            "agent_class": res.get("agent_class"),
            "size_x": sx,
            "size_y": sy,
            "grid_cells": sx * sy,
            "dirt_rate": dirt,
            "seed": seed,
            "cells_cleaned": cells_cleaned,
            "actions": actions,
            "execution_time": res.get("execution_time"),
            "success": res.get("success"),
            "error": res.get("error"),
        })

        print(f"[{agent_label}] {sx}x{sy}  dirt={dirt}  seed={seed}  "
              f"ok={res.get('success')}  cleaned={cells_cleaned}  actions={actions}  "
              f"err={res.get('error')}")

def main():
    outdir = Path("batch_results")
    outdir.mkdir(exist_ok=True)
    outfile = outdir / f"results_{int(time.time())}.csv"

    rows = []
    # Reflex-Agent laufen lassen
    run_suite(REFLEX_AGENT_FILE, "Reflex", rows)
    # Random-Agent laufen lassen
    run_suite(RANDOM_AGENT_FILE, "Random", rows)

    # CSV speichern
    fieldnames = ["agent","agent_class","size_x","size_y","grid_cells",
                  "dirt_rate","seed","cells_cleaned","actions",
                  "execution_time","success","error"]
    with outfile.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)

    # Kleine Zusammenfassung (Durchschnitt über alle Läufe, nur erfolgreiche)
    for label in ["Reflex", "Random"]:
        sub = [r for r in rows if r["agent"] == label and r["success"]]
        if sub:
            avg_cleaned = mean(r["cells_cleaned"] for r in sub)
            avg_actions = mean(r["actions"] for r in sub)
            print(f"\nSummary [{label}]: "
                  f"avg cleaned = {avg_cleaned:.2f}, avg actions = {avg_actions:.2f} "
                  f"(n={len(sub)} successful runs)")
        else:
            print(f"\nSummary [{label}]: keine erfolgreichen Läufe gefunden.")

    print(f"\nFertig. Ergebnisse gespeichert in: {outfile}")

if __name__ == "__main__":
    main()
