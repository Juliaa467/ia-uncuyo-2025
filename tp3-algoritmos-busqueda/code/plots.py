import os, csv, math
import matplotlib.pyplot as plt

CSV_PATH = os.path.join(os.path.dirname(__file__), "..", "results.csv")
IMG_DIR  = os.path.join(os.path.dirname(__file__), "..", "images")
os.makedirs(IMG_DIR, exist_ok=True)

ALGO_ORDER = ["random", "bfs", "dfs", "dls50", "dls75", "dls100", "ucs", "astar"]

data = {a: {"states_n": [], "actions_count": [], "actions_cost": [], "time": []} for a in ALGO_ORDER}

with open(CSV_PATH, newline="") as f:
    r = csv.DictReader(f)
    for row in r:
        algo = row["algorithm_name"]
        if algo not in data:
            continue
        def to_num(x):
            if x is None or x == "" or x.lower() == "none":
                return None
            try:
                return float(x)
            except:
                return None

        sn  = to_num(row["states_n"])
        tm  = to_num(row["time"])
        ac1 = to_num(row["actions_count"])
        ac2 = to_num(row["actions_cost"])

        if sn is not None:  data[algo]["states_n"].append(sn)
        if tm is not None:  data[algo]["time"].append(tm)
        if ac1 is not None: data[algo]["actions_count"].append(ac1)
        if ac2 is not None: data[algo]["actions_cost"].append(ac2)

def boxplot_metric(metric, ylabel, filename):
    vals = [data[a][metric] for a in ALGO_ORDER]
    labels = ALGO_ORDER
    filtered = [(lab, v) for lab, v in zip(labels, vals) if len(v) > 0]
    if not filtered:
        print(f"Keine Daten für {metric}")
        return
    labels, vals = zip(*filtered)

    plt.figure()
    plt.boxplot(vals, showmeans=True)
    plt.xticks(range(1, len(labels)+1), labels, rotation=20)
    plt.ylabel(ylabel)
    plt.title(f"Boxplot {metric}")
    out = os.path.join(IMG_DIR, filename)
    plt.tight_layout()
    plt.savefig(out, dpi=160)
    plt.close()
    print(f"Gespeichert: {out}")

def mean_std(xs):
    if not xs: return (math.nan, math.nan)
    m = sum(xs)/len(xs)
    v = sum((x-m)**2 for x in xs)/(len(xs)-1) if len(xs) > 1 else 0.0
    return (m, math.sqrt(v))

boxplot_metric("states_n",     "Explorierte Zustände (S1)", "box_states_n.png")
boxplot_metric("actions_count","Anzahl Aktionen (S1)",      "box_actions_count.png")
boxplot_metric("actions_cost", "Aktionskosten (S2)",        "box_actions_cost.png")
boxplot_metric("time",         "Zeit [s] (S1)",             "box_time.png")

stats_path = os.path.join(IMG_DIR, "summary_stats.txt")
with open(stats_path, "w") as f:
    for a in ALGO_ORDER:
        s = data[a]["states_n"];  m_s, sd_s = mean_std(s)
        ac = data[a]["actions_count"]; m_ac, sd_ac = mean_std(ac)
        c2 = data[a]["actions_cost"];  m_c2, sd_c2 = mean_std(c2)
        t  = data[a]["time"];          m_t, sd_t  = mean_std(t)
        f.write(
            f"{a}\n"
            f"- states_n (S1): mean={m_s:.2f}, std={sd_s:.2f}, n={len(s)}\n"
            f"- actions_count (S1): mean={m_ac:.2f}, std={sd_ac:.2f}, n={len(ac)}\n"
            f"- actions_cost (S2): mean={m_c2:.2f}, std={sd_c2:.2f}, n={len(c2)}\n"
            f"- time [s] (S1): mean={m_t:.4f}, std={sd_t:.4f}, n={len(t)}\n\n"
        )
print(f"Statistik gespeichert: {stats_path}")
