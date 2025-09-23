# Uso con Makefile:
#   make exp   → corre todos los experimentos
#   make hc    → Hill Climbing
#   make sa    → Simulated Annealing
#   make ga    → Algoritmo Genético
#   make rand  → Búsqueda Aleatoria
# Resultados en carpeta tp4-busquedas-locales

import argparse, time, random, math, csv, statistics
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

def project_root():
    return Path(__file__).resolve().parent.parent

def random_board(n, rng):
    return [rng.randrange(n) for _ in range(n)]

def H(board):
    n = len(board)
    h = 0
    for c1 in range(n):
        r1 = board[c1]
        for c2 in range(c1 + 1, n):
            r2 = board[c2]
            if r1 == r2 or abs(r1 - r2) == abs(c1 - c2):
                h += 1
    return h

def best_neighbor(board, rng):
    n = len(board)
    current_h = H(board)
    best_h = current_h
    bests = []
    for c in range(n):
        r_orig = board[c]
        for r in range(n):
            if r == r_orig:
                continue
            board[c] = r
            val = H(board)
            if val < best_h:
                best_h = val
                bests = [(c, r)]
            elif val == best_h:
                bests.append((c, r))
        board[c] = r_orig
    if not bests:
        return board[:], current_h, False
    c, r = rng.choice(bests)
    nb = board[:]
    nb[c] = r
    return nb, best_h, True

def hill_climbing(n, max_states, seed, return_history=False):
    rng = random.Random(seed)
    board = random_board(n, rng)
    states = 1
    start = time.time()
    history = [H(board)] if return_history else None
    while states < max_states:
        if H(board) == 0:
            break
        nb, nb_h, improved = best_neighbor(board, rng)
        if not improved:
            break
        board = nb
        states += 1
        if return_history:
            history.append(nb_h)
    elapsed = time.time() - start
    return board, H(board), states, elapsed, (history if return_history else None)

def random_search(n, max_states, seed, return_history=False):
    rng = random.Random(seed)
    best = None
    best_h = math.inf
    states = 0
    start = time.time()
    history = []
    while states < max_states:
        b = random_board(n, rng)
        val = H(b)
        states += 1
        if return_history:
            history.append(val if best is None else min(best_h, val))
        if val < best_h:
            best = b
            best_h = val
        if best_h == 0:
            break
    elapsed = time.time() - start
    return best, best_h, states, elapsed, (history if return_history else None)

def neighbors_for_sa(board, rng):
    n = len(board)
    c = rng.randrange(n)
    r = rng.randrange(n)
    nb = board[:]
    nb[c] = r
    return nb

def simulated_annealing(n, max_states, seed, T0=1.0, alpha=0.995, Tmin=1e-4, return_history=False):
    rng = random.Random(seed)
    current = random_board(n, rng)
    current_h = H(current)
    best = current[:]
    best_h = current_h
    states = 1
    start = time.time()
    T = T0
    history = [current_h] if return_history else None
    while states < max_states and T > Tmin and best_h > 0:
        candidate = neighbors_for_sa(current, rng)
        cand_h = H(candidate)
        delta = cand_h - current_h
        if delta <= 0 or rng.random() < math.exp(-delta / T):
            current, current_h = candidate, cand_h
            if current_h < best_h:
                best, best_h = current[:], current_h
        T *= alpha
        states += 1
        if return_history:
            history.append(current_h)
    elapsed = time.time() - start
    return best, best_h, states, elapsed, (history if return_history else None)

def fitness(board):
    return -H(board)

def tournament_select(pop, k, rng):
    sel = rng.sample(pop, k)
    sel.sort(key=lambda ind: ind[1], reverse=True)
    return sel[0][0][:]

def crossover(p1, p2, rng, pc=0.9):
    if rng.random() > pc:
        return p1[:], p2[:]
    n = len(p1)
    c1, c2 = p1[:], p2[:]
    for i in range(n):
        if rng.random() < 0.5:
            c1[i], c2[i] = c2[i], c1[i]
    return c1, c2

def mutate(ind, rng, pm=0.1):
    n = len(ind)
    for i in range(n):
        if rng.random() < pm:
            ind[i] = rng.randrange(n)

def genetic_algorithm(n, max_states, seed, pop_size=100, k_tourn=3, pc=0.9, pm=0.1, elitism=2, return_history=False):
    rng = random.Random(seed)
    pop = []
    evals = 0
    for _ in range(pop_size):
        b = random_board(n, rng)
        f = fitness(b)
        pop.append((b, f))
        evals += 1
    best_ind = max(pop, key=lambda x: x[1])[0][:]
    best_h = H(best_ind)
    start = time.time()
    history = [best_h] if return_history else None
    while evals < max_states and best_h > 0:
        pop.sort(key=lambda x: x[1], reverse=True)
        new_pop = pop[:elitism]
        while len(new_pop) < pop_size:
            p1 = tournament_select(pop, k_tourn, rng)
            p2 = tournament_select(pop, k_tourn, rng)
            c1, c2 = crossover(p1, p2, rng, pc)
            mutate(c1, rng, pm)
            mutate(c2, rng, pm)
            f1 = fitness(c1)
            f2 = fitness(c2)
            new_pop.append((c1, f1))
            if len(new_pop) < pop_size:
                new_pop.append((c2, f2))
            evals += 2
            if evals >= max_states:
                break
        pop = new_pop
        cur_best = max(pop, key=lambda x: x[1])[0][:]
        cur_h = H(cur_best)
        if cur_h < best_h:
            best_ind, best_h = cur_best[:], cur_h
        if return_history:
            history.append(best_h)
        if best_h == 0:
            break
    elapsed = time.time() - start
    return best_ind, best_h, evals, elapsed, (history if return_history else None)

def write_csv(rows, csv_path):
    header = ["algorithm_name","env_n","size","best_solution","H","states","time"]
    with open(csv_path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        for r in rows:
            w.writerow(r)

def stats_summary(values):
    if not values:
        return 0.0, 0.0
    if len(values) == 1:
        return float(values[0]), 0.0
    return float(statistics.mean(values)), float(statistics.pstdev(values))

def plot_history(hist, title, out_path):
    plt.figure()
    plt.plot(range(1, len(hist)+1), hist)
    plt.xlabel("Iteración")
    plt.ylabel("H(e)")
    plt.title(title)
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()

def boxplot_metric(data_by_algo, ylabel, title, out_path):
    labels = sorted(data_by_algo.keys())
    data = [data_by_algo[k] for k in labels]
    plt.figure()
    plt.boxplot(data, labels=labels)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()

def run_single(alg, n, max_states, seed, sa_T0, sa_alpha, sa_Tmin, ga_pop, ga_k, ga_pc, ga_pm, ga_elitism, history_flag):
    if alg == "HC":
        return hill_climbing(n, max_states, seed, return_history=history_flag)
    if alg == "SA":
        return simulated_annealing(n, max_states, seed, T0=sa_T0, alpha=sa_alpha, Tmin=sa_Tmin, return_history=history_flag)
    if alg == "GA":
        return genetic_algorithm(n, max_states, seed, pop_size=ga_pop, k_tourn=ga_k, pc=ga_pc, pm=ga_pm, elitism=ga_elitism, return_history=history_flag)
    if alg == "random":
        return random_search(n, max_states, seed, return_history=history_flag)
    raise ValueError("unknown algorithm")

def experiments(seeds, sizes, max_states, sa_T0, sa_alpha, sa_Tmin, ga_pop, ga_k, ga_pc, ga_pm, ga_elitism):
    base = project_root()
    images_dir = base / "images"
    images_dir.mkdir(parents=True, exist_ok=True)
    csv_path = base / "tp4-Nreinas.csv"
    rows = []
    algos = ["random","HC","SA","GA"]
    for n in sizes:
        for env_n, seed in enumerate(seeds, start=1):
            for alg in algos:
                b, hval, states, t, _ = run_single(alg, n, max_states, seed, sa_T0, sa_alpha, sa_Tmin, ga_pop, ga_k, ga_pc, ga_pm, ga_elitism, history_flag=False)
                rows.append([alg, env_n, n, b, hval, states, f"{t:.6f}"])
    write_csv(rows, csv_path)
    agg = {}
    for alg in algos:
        agg[alg] = {}
        for n in sizes:
            subset = [r for r in rows if r[0]==alg and r[2]==n]
            hs = [int(r[4]) for r in subset]
            ts = [float(r[6]) for r in subset]
            sts = [int(r[5]) for r in subset]
            succ = sum(1 for v in hs if v==0)
            rate = 100.0*succ/len(hs) if hs else 0.0
            agg[alg][n] = {"success_rate":rate,"H_mean":stats_summary(hs)[0],"H_std":stats_summary(hs)[1],"time_mean":stats_summary(ts)[0],"time_std":stats_summary(ts)[1],"states_mean":stats_summary(sts)[0],"states_std":stats_summary(sts)[1]}
    for n in sizes:
        data_h = {alg:[int(r[4]) for r in rows if r[0]==alg and r[2]==n] for alg in algos}
        data_t = {alg:[float(r[6]) for r in rows if r[0]==alg and r[2]==n] for alg in algos}
        data_s = {alg:[int(r[5]) for r in rows if r[0]==alg and r[2]==n] for alg in algos}
        boxplot_metric(data_h, "H(e)", f"H por algoritmo (N={n})", images_dir / f"boxplot_H_N{n}.png")
        boxplot_metric(data_t, "Tiempo [s]", f"Tiempo por algoritmo (N={n})", images_dir / f"boxplot_time_N{n}.png")
        boxplot_metric(data_s, "Estados", f"Estados por algoritmo (N={n})", images_dir / f"boxplot_states_N{n}.png")
    for alg in ["random","HC","SA","GA"]:
        seed = seeds[0]
        n = sizes[0]
        b, hval, states, t, hist = run_single(alg, n, max_states, seed, sa_T0, sa_alpha, sa_Tmin, ga_pop, ga_k, ga_pc, ga_pm, ga_elitism, history_flag=True)
        if hist and len(hist)>1:
            plot_history(hist, f"Evolución H(e) {alg} (N={n}, seed={seed})", images_dir / f"history_{alg}_N{n}_seed{seed}.png")
    reporte_md = base / "tp4-reporte.md"
    with open(reporte_md, "w") as f:
        f.write("tp4-reporte\n\n")
        f.write("Resumen de métricas por algoritmo y tamaño:\n\n")
        for alg in algos:
            f.write(f"{alg}:\n")
            for n in sizes:
                m = agg[alg][n]
                f.write(f"N={n}: success={m['success_rate']:.1f}%, H_mean={m['H_mean']:.3f}±{m['H_std']:.3f}, time={m['time_mean']:.4f}±{m['time_std']:.4f}s, states={m['states_mean']:.1f}±{m['states_std']:.1f}\n")
            f.write("\n")
        f.write("Ver gráficos en carpeta images.\n")
    return str(csv_path), str(reporte_md), str(images_dir)

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--mode", choices=["single","exp"], default="single")
    p.add_argument("--alg", choices=["random","HC","SA","GA"], default="HC")
    p.add_argument("--n", type=int, default=8)
    p.add_argument("--max_states", type=int, default=10000)
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--sa_T0", type=float, default=1.0)
    p.add_argument("--sa_alpha", type=float, default=0.995)
    p.add_argument("--sa_Tmin", type=float, default=1e-4)
    p.add_argument("--ga_pop", type=int, default=100)
    p.add_argument("--ga_k", type=int, default=3)
    p.add_argument("--ga_pc", type=float, default=0.9)
    p.add_argument("--ga_pm", type=float, default=0.1)
    p.add_argument("--ga_elitism", type=int, default=2)
    p.add_argument("--history", action="store_true")
    args = p.parse_args()

    if args.mode == "single":
        b, hval, states, t, hist = run_single(args.alg, args.n, args.max_states, args.seed, args.sa_T0, args.sa_alpha, args.sa_Tmin, args.ga_pop, args.ga_k, args.ga_pc, args.ga_pm, args.ga_elitism, args.history)
        print("algorithm_name:", args.alg)
        print("solution:", b)
        print("H:", hval)
        print("states:", states)
        print("time_sec:", f"{t:.6f}")
        if args.history and hist:
            base = project_root()
            img = base / "images"
            img.mkdir(parents=True, exist_ok=True)
            outp = img / f"history_{args.alg}_N{args.n}_seed{args.seed}.png"
            plot_history(hist, f"Evolución H(e) {args.alg} (N={args.n}, seed={args.seed})", outp)
            print("history_plot:", str(outp))
    else:
        seeds = list(range(1, 30 + 1))
        sizes = [4, 8, 10]
        csv_path, reporte_md, images_dir = experiments(seeds, sizes, args.max_states, args.sa_T0, args.sa_alpha, args.sa_Tmin, args.ga_pop, args.ga_k, args.ga_pc, args.ga_pm, args.ga_elitism)
        print("csv:", csv_path)
        print("reporte_md:", reporte_md)
        print("images_dir:", images_dir)

if __name__ == "__main__":
    main()
