# i)   Aleatorio
# ii)  BFS
# iii) DFS
# iv)  DLS (Limits 50/75/100)
# v)   Uniform Cost Search (Dijkstra)
# vi)  A*

import time, random, heapq
from collections import deque
import gymnasium as gym
from gymnasium import wrappers
import csv, os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))          # …/tp3-algoritmos-busqueda/code
OUT_CSV  = os.path.abspath(os.path.join(BASE_DIR, "..", "results.csv"))

#0=izquierda, 1=abajo, 2=derecha, 3=arriba
MOVES = {0:(0,-1), 1:(1,0), 2:(0,1), 3:(-1,0)}

def generate_random_map_custom(size=100, p_frozen=0.92, seed=42):
    rng = random.Random(seed)
    grid = []
    for _ in range(size):
        row = ['F' if rng.random() < p_frozen else 'H' for __ in range(size)]
        grid.append(row)
    def rand_free():
        while True:
            r, c = rng.randrange(size), rng.randrange(size)
            if grid[r][c] == 'F':
                return r, c
    sr, sc = rand_free()
    gr, gc = rand_free()
    while (gr, gc) == (sr, sc):
        gr, gc = rand_free()
    grid[sr][sc] = 'S'
    grid[gr][gc] = 'G'
    desc = [''.join(row) for row in grid]
    return desc, (sr, sc), (gr, gc)

def make_env(desc, max_steps=1000, is_slippery=False, render_mode=None):
    env = gym.make("FrozenLake-v1", desc=desc, is_slippery=is_slippery, render_mode=render_mode).env
    env = wrappers.TimeLimit(env, max_episode_steps=max_steps)
    return env

def in_bounds(r,c,h,w): return 0 <= r < h and 0 <= c < w
def passable(desc,r,c): return desc[r][c] != 'H'

def neighbors(desc, r, c):
    h, w = len(desc), len(desc[0])
    for a, (dr, dc) in MOVES.items():
        nr, nc = r+dr, c+dc
        if in_bounds(nr, nc, h, w) and passable(desc, nr, nc):
            yield nr, nc, a

def reconstruct(parent, start, goal):
    r, c = goal
    path = [(r, c)]
    while (r, c) != start:
        r, c = parent[(r, c)][0]
        path.append((r, c))
    path.reverse()
    actions = []
    for i in range(len(path)-1):
        r1, c1 = path[i]
        r2, c2 = path[i+1]
        dr, dc = r2-r1, c2-c1
        for a, (mdr, mdc) in MOVES.items():
            if (dr, dc) == (mdr, mdc):
                actions.append(a); break
    return path, actions

def step_cost(action, cost_mode):
    if cost_mode == 1:
        return 1
    return 1 if action in (0,2) else 10

# A* heuristica
def heuristic(pos, goal, cost_mode):
    (r, c), (gr, gc) = pos, goal
    dx, dy = abs(gc - c), abs(gr - r)
    if cost_mode == 1:
        return dx + dy
    return dx*1 + dy*10

def random_search(desc, start, goal, max_expansions=200000):
    frontier = [start]
    parent = {start: (None, None)}  # (prev, action)
    explored = 0
    rng = random.Random(0)
    while frontier and explored < max_expansions:
        i = rng.randrange(len(frontier))
        r, c = frontier.pop(i)
        explored += 1
        if (r, c) == goal:
            p = []
            cur = (r, c)
            while parent[cur][0] is not None:
                p.append(cur)
                cur = parent[cur][0]
            p.append(start); p.reverse()
            actions = []
            for j in range(len(p)-1):
                r1,c1 = p[j]; r2,c2 = p[j+1]
                dr,dc = r2-r1, c2-c1
                for a,(mdr,mdc) in MOVES.items():
                    if (dr,dc)==(mdr,mdc): actions.append(a); break
            return p, actions, explored
        for nr, nc, a in neighbors(desc, r, c):
            if (nr, nc) not in parent:
                parent[(nr, nc)] = ((r, c), a)
                frontier.append((nr, nc))
    return None, None, explored

def bfs(desc, start, goal):
    q = deque([start])
    parent = {start:(None, None)}
    explored = 0
    while q:
        r, c = q.popleft()
        explored += 1
        if (r, c) == goal:
            path, actions = reconstruct(parent, start, goal)
            return path, actions, explored
        for nr, nc, a in neighbors(desc, r, c):
            if (nr, nc) not in parent:
                parent[(nr, nc)] = ((r, c), a)
                q.append((nr, nc))
    return None, None, explored

def dfs(desc, start, goal, max_expansions=200000):
    stack = [start]
    parent = {start:(None, None)}
    explored = 0
    while stack and explored < max_expansions:
        r, c = stack.pop()
        explored += 1
        if (r, c) == goal:
            path, actions = reconstruct(parent, start, goal)
            return path, actions, explored
        for nr, nc, a in reversed(list(neighbors(desc, r, c))):
            if (nr, nc) not in parent:
                parent[(nr, nc)] = ((r, c), a)
                stack.append((nr, nc))
    return None, None, explored

def dls(desc, start, goal, limit):
    stack = [(start, 0)]
    parent = {start:(None, None)}
    best_depth = {start:0}
    explored = 0
    while stack:
        (r, c), d = stack.pop()
        explored += 1
        if (r, c) == goal:
            path, actions = reconstruct(parent, start, goal)
            return path, actions, explored
        if d < limit:
            for nr, nc, a in neighbors(desc, r, c):
                nd = d+1
                if (nr, nc) not in best_depth or nd < best_depth[(nr, nc)]:
                    best_depth[(nr, nc)] = nd
                    parent[(nr, nc)] = ((r, c), a)
                    stack.append(((nr, nc), nd))
    return None, None, explored

def ucs(desc, start, goal, cost_mode):
    pq = [(0, start)]
    parent = {start:(None, None)}
    g_cost = {start:0}
    explored = 0
    while pq:
        g, (r, c) = heapq.heappop(pq)
        explored += 1
        if (r, c) == goal:
            path, actions = reconstruct(parent, start, goal)
            return path, actions, explored, g
        for nr, nc, a in neighbors(desc, r, c):
            ng = g + step_cost(a, cost_mode)
            if (nr, nc) not in g_cost or ng < g_cost[(nr, nc)]:
                g_cost[(nr, nc)] = ng
                parent[(nr, nc)] = ((r, c), a)
                heapq.heappush(pq, (ng, (nr, nc)))
    return None, None, explored, None

def astar(desc, start, goal, cost_mode):
    h0 = heuristic(start, goal, cost_mode)
    pq = [(h0, 0, start)]
    parent = {start:(None, None)}
    g_cost = {start:0}
    explored = 0
    while pq:
        f, g, (r, c) = heapq.heappop(pq)
        explored += 1
        if (r, c) == goal:
            path, actions = reconstruct(parent, start, goal)
            return path, actions, explored, g
        for nr, nc, a in neighbors(desc, r, c):
            ng = g + step_cost(a, cost_mode)
            if (nr, nc) not in g_cost or ng < g_cost[(nr, nc)]:
                g_cost[(nr, nc)] = ng
                parent[(nr, nc)] = ((r, c), a)
                nf = ng + heuristic((nr, nc), goal, cost_mode)
                heapq.heappush(pq, (nf, ng, (nr, nc)))
    return None, None, explored, None

def cost_s1(actions):
    return len(actions) if actions is not None else None

def cost_s2(actions):
    if actions is None: return None
    total = 0
    for a in actions:
        total += 1 if a in (0,2) else 10
    return total

def print_env(desc):
    for row in desc:
        print(row)

ALGORITHMS = ["random", "bfs", "dfs", "dls50", "dls75", "dls100", "ucs", "astar"]

def run_algo(desc, S, G, name, cost_mode):
    if name == "random":
        path, actions, explored = random_search(desc, S, G)
        g_val = None
    elif name == "bfs":
        path, actions, explored = bfs(desc, S, G)
        g_val = None
    elif name == "dfs":
        path, actions, explored = dfs(desc, S, G)
        g_val = None
    elif name == "dls50":
        path, actions, explored = dls(desc, S, G, 50)
        g_val = None
    elif name == "dls75":
        path, actions, explored = dls(desc, S, G, 75)
        g_val = None
    elif name == "dls100":
        path, actions, explored = dls(desc, S, G, 100)
        g_val = None
    elif name == "ucs":
        path, actions, explored, g_val = ucs(desc, S, G, cost_mode)
    elif name == "astar":
        path, actions, explored, g_val = astar(desc, S, G, cost_mode)
    else:
        raise ValueError(name)
    return path, actions, explored, g_val

def eval_one_environment(env_seed):
    desc, S, G = generate_random_map_custom(size=100, p_frozen=0.92, seed=env_seed)
    _ = make_env(desc, max_steps=1000, is_slippery=False, render_mode=None)

    rows = []
    for algo in ALGORITHMS:
        # 1)
        t0 = time.perf_counter()
        path1, actions1, explored1, g1 = run_algo(desc, S, G, algo, cost_mode=1)
        t1 = time.perf_counter() - t0

        # 2)
        path2, actions2, explored2, g2 = run_algo(desc, S, G, algo, cost_mode=2)
        actions_cost2 = cost_s2(actions2) if actions2 is not None else None
        row = {
            "algorithm_name": algo,
            "env_n": env_seed,
            "states_n": explored1,
            "actions_count": len(actions1) if actions1 is not None else None,
            "actions_cost": actions_cost2,
            "time": t1,
            "solution_found": (path1 is not None and path2 is not None)
        }
        rows.append(row)
    return rows

def run_30_and_write_csv(out_path="../results.csv", n_envs=30, start_seed=0):
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["algorithm_name","env_n","states_n","actions_count","actions_cost","time","solution_found"]
        )
        writer.writeheader()
        for env_seed in range(start_seed, start_seed + n_envs):
            for row in eval_one_environment(env_seed):
                writer.writerow(row)
    print(f"Ergebnisse gespeichert in {out_path}")

if __name__ == "__main__":
    run_30_and_write_csv(out_path=OUT_CSV, n_envs=30, start_seed=0)


