# student_agents/graficos.py
# -*- coding: utf-8 -*-
"""
Genera gráficos comparativos (Random vs. Reflex) a partir de results_*.csv.
Usa exactamente estos nombres de columnas en la CSV:
agent, agent_class, size_x, size_y, grid_cells, dirt_rate, seed,
cells_cleaned, actions, execution_time, success, error

Guarda PNGs y un CSV resumen en ../batch_results/.
Uso:
    python student_agents/graficos.py
    python student_agents/graficos.py --csv results_1756153529.csv
"""

from pathlib import Path
import argparse

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# Nombres de columnas EXACTOS
COL = {
    "AGENT": "agent",
    "AGENT_CLASS": "agent_class",
    "SX": "size_x",
    "SY": "size_y",
    "GRID": "grid_cells",
    "DIRT": "dirt_rate",
    "SEED": "seed",
    "CLEAN": "cells_cleaned",
    "ACT": "actions",
    "TIME": "execution_time",
    "SUCCESS": "success",
    "ERROR": "error",
}

def archivo_mas_reciente(dir_datos: Path) -> Path:
    archivos = list(dir_datos.glob("results_*.csv"))
    if not archivos:
        raise FileNotFoundError(f"No se encontró ningún results_*.csv en {dir_datos}")
    return max(archivos, key=lambda p: p.stat().st_mtime)

def cargar_y_preparar(csv_path: Path) -> pd.DataFrame:
    df = pd.read_csv(csv_path)

    # Validación mínima: columnas requeridas
    requeridas = [COL["AGENT"], COL["SX"], COL["SY"], COL["CLEAN"], COL["ACT"]]
    faltan = [c for c in requeridas if c not in df.columns]
    if faltan:
        raise ValueError(f"Faltan columnas en {csv_path.name}: {faltan}")

    # grid_cells si no está
    if COL["GRID"] not in df.columns:
        df[COL["GRID"]] = df[COL["SX"]] * df[COL["SY"]]

    # success/error a booleano si llegan como texto
    for c in (COL["SUCCESS"], COL["ERROR"]):
        if c in df.columns and df[c].dtype == object:
            df[c] = df[c].astype(str).str.lower().map({"true": True, "false": False})

    # Limpieza básica de strings
    df[COL["AGENT"]] = df[COL["AGENT"]].astype(str).str.strip()

    # Métricas derivadas (nombres internos, no escriben la CSV)
    df["coverage"] = df[COL["CLEAN"]] / df[COL["GRID"]]
    df["efficiency"] = df[COL["CLEAN"]] / df[COL["ACT"]].replace({0: np.nan})
    df["cost_per_cell"] = df[COL["ACT"]] / df[COL["CLEAN"]].replace({0: np.nan})
    return df

def resumir(df: pd.DataFrame) -> pd.DataFrame:
    agg = (df.groupby([COL["AGENT"], COL["GRID"]])
             .agg(
                 corridas=(COL["AGENT"], "count"),
                 cobertura_prom=("coverage", "mean"),
                 cobertura_std=("coverage", "std"),
                 acciones_prom=(COL["ACT"], "mean"),
                 acciones_std=(COL["ACT"], "std"),
                 celdas_prom=(COL["CLEAN"], "mean"),
                 tasa_exito=(COL["SUCCESS"], "mean") if COL["SUCCESS"] in df.columns else (COL["AGENT"], "count"),
                 tiempo_prom=(COL["TIME"], "mean") if COL["TIME"] in df.columns else (COL["AGENT"], "count"),
             )
             .reset_index()
             .sort_values([COL["GRID"], COL["AGENT"]]))
    if COL["SUCCESS"] not in df.columns:
        agg["tasa_exito"] = np.nan
    if COL["TIME"] not in df.columns:
        agg["tiempo_prom"] = np.nan
    return agg

def _finalizar(ax, titulo, xlabel, ylabel, leyenda=True):
    ax.set_title(titulo)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.grid(True, alpha=0.3)
    if leyenda:
        ax.legend(frameon=False)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)

def linea_metric(agg_df, metric, ylabel, titulo, archivo_salida):
    fig, ax = plt.subplots(figsize=(7.5, 4.5))
    for agente, sub in agg_df.groupby(COL["AGENT"]):
        sub = sub.sort_values(COL["GRID"])
        ax.plot(sub[COL["GRID"]], sub[metric], marker="o", label=agente)
    _finalizar(ax, titulo, "Tamaño de grilla (celdas)", ylabel)
    fig.tight_layout()
    fig.savefig(archivo_salida, dpi=150)
    plt.close(fig)

def dispersion_tradeoff(df_in, archivo_salida):
    fig, ax = plt.subplots(figsize=(7, 5.5))
    for agente, sub in df_in.groupby(COL["AGENT"]):
        ax.scatter(sub[COL["ACT"]], sub[COL["CLEAN"]], alpha=0.5, label=agente)
    _finalizar(ax, "Trade-off: celdas limpiadas vs. acciones", "Acciones (pasos)", "Celdas limpiadas")
    fig.tight_layout()
    fig.savefig(archivo_salida, dpi=150)
    plt.close(fig)

def box_tiempo(df_in, archivo_salida):
    if COL["TIME"] not in df_in.columns or df_in[COL["TIME"]].isna().all():
        return False
    orden = df_in[COL["AGENT"]].value_counts().index.tolist()
    datos = [df_in[df_in[COL["AGENT"]]==a][COL["TIME"]] for a in orden]
    fig, ax = plt.subplots(figsize=(6.5, 4.2))
    ax.boxplot(datos, labels=orden, showfliers=False)
    _finalizar(ax, "Tiempo de ejecución por agente", "", "Tiempo [s]", leyenda=False)
    fig.tight_layout()
    fig.savefig(archivo_salida, dpi=150)
    plt.close(fig)
    return True

def plots_por_dirt(df_in, prefijo_salida):
    if COL["DIRT"] not in df_in.columns:
        return []
    archivos = []
    por_dirt = (df_in.groupby([COL["AGENT"], COL["GRID"], COL["DIRT"]])
                  .agg(cobertura_prom=("coverage","mean"),
                       acciones_prom=(COL["ACT"],"mean"))
                  .reset_index())
    # Cobertura
    fig, ax = plt.subplots(figsize=(8, 4.8))
    for (agente, dr), sub in por_dirt.groupby([COL["AGENT"], COL["DIRT"]]):
        sub = sub.sort_values(COL["GRID"])
        ax.plot(sub[COL["GRID"]], 100*sub["cobertura_prom"], marker="o", alpha=0.9, label=f"{agente} – dirt={dr}")
    _finalizar(ax, "Cobertura por tasa de suciedad", "Tamaño de grilla (celdas)", "Cobertura [%]")
    f_cov = f"{prefijo_salida}_cobertura_por_dirt.png"
    fig.tight_layout(); fig.savefig(f_cov, dpi=150); plt.close(fig)
    archivos.append(f_cov)
    # Acciones
    fig, ax = plt.subplots(figsize=(8, 4.8))
    for (agente, dr), sub in por_dirt.groupby([COL["AGENT"], COL["DIRT"]]):
        sub = sub.sort_values(COL["GRID"])
        ax.plot(sub[COL["GRID"]], sub["acciones_prom"], marker="s", alpha=0.9, label=f"{agente} – dirt={dr}")
    _finalizar(ax, "Acciones por tasa de suciedad", "Tamaño de grilla (celdas)", "Acciones [promedio]")
    f_act = f"{prefijo_salida}_acciones_por_dirt.png"
    fig.tight_layout(); fig.savefig(f_act, dpi=150); plt.close(fig)
    archivos.append(f_act)
    return archivos

def main():
    parser = argparse.ArgumentParser(description="Gráficos comparativos desde results_*.csv")
    parser.add_argument("--csv", type=str, default=None, help="Nombre del results_*.csv en batch_results/")
    parser.add_argument("--agents", type=str, default="Random,Reflex",
                        help="Agentes a incluir (coinciden con la columna 'agent'), separados por coma")
    args = parser.parse_args()

    aqui = Path(__file__).resolve()
    dir_datos = aqui.parents[1] / "batch_results"
    dir_salida = dir_datos
    dir_salida.mkdir(parents=True, exist_ok=True)

    csv_path = dir_datos / args.csv if args.csv else archivo_mas_reciente(dir_datos)
    df = cargar_y_preparar(csv_path)

    # Filtrar agentes (tal como aparecen en la CSV)
    agentes = [a.strip() for a in args.agents.split(",") if a.strip()]
    foco = df[df[COL["AGENT"]].isin(agentes)].copy()
    if foco.empty:
        raise ValueError(f"No hay filas para agentes {agentes}. Disponibles: {sorted(df[COL['AGENT']].unique())}")

    agg = resumir(foco)
    stem = csv_path.stem
    prefijo = dir_salida / stem

    # 1) Rendimiento (cobertura)
    cov_agg = agg.assign(cobertura_pct=lambda x: 100 * x["cobertura_prom"])
    linea_metric(cov_agg, "cobertura_pct", "Cobertura [%]",
                 "Rendimiento: porcentaje de celdas limpiadas",
                 prefijo.with_name(f"{stem}_cobertura_vs_grilla.png"))

    # 2) Costo (acciones)
    linea_metric(agg, "acciones_prom", "Acciones [promedio por corrida]",
                 "Costo: acciones promedio vs. tamaño de grilla",
                 prefijo.with_name(f"{stem}_acciones_vs_grilla.png"))

    # 3) Trade-off (dispersión)
    dispersion_tradeoff(foco, prefijo.with_name(f"{stem}_tradeoff_acciones_vs_celdas.png"))

    # 4) Éxito (si existe)
    if COL["SUCCESS"] in foco.columns and not foco[COL["SUCCESS"]].isna().all():
        sr = (foco.groupby([COL["AGENT"], COL["GRID"]])[COL["SUCCESS"]]
                    .mean().reset_index(name="tasa_exito"))
        sr["tasa_exito"] = 100 * sr["tasa_exito"]
        linea_metric(sr, "tasa_exito", "Tasa de éxito [%]",
                     "Tasa de éxito por tamaño de grilla",
                     prefijo.with_name(f"{stem}_exito_vs_grilla.png"))

    # 5) Boxplot de tiempos (si existe)
    box_tiempo(foco, prefijo.with_name(f"{stem}_tiempo_ejecucion_box.png"))

    # 6) Cortes por tasa de suciedad (si existe)
    plots_por_dirt(foco, prefijo.with_name(f"{stem}").as_posix())

    # 7) CSV de “ganadores” por grilla
    costo = (foco.groupby([COL["AGENT"], COL["GRID"]])
                  .apply(lambda x: (x[COL["ACT"]] / x[COL["CLEAN"]].replace({0: np.nan})).mean())
                  .reset_index(name="acciones_por_celda_prom"))
    ganadores = []
    g_cov = (agg.sort_values([COL["GRID"], "cobertura_prom"], ascending=[True, False])
                .groupby(COL["GRID"]).head(1)
                .loc[:, [COL["GRID"], COL["AGENT"], "cobertura_prom"]]
                .rename(columns={"cobertura_prom": "valor"}))
    g_cov["metrica"] = "mejor_cobertura"; ganadores.append(g_cov)

    g_act = (agg.sort_values([COL["GRID"], "acciones_prom"], ascending=[True, True])
                .groupby(COL["GRID"]).head(1)
                .loc[:, [COL["GRID"], COL["AGENT"], "acciones_prom"]]
                .rename(columns={"acciones_prom": "valor"}))
    g_act["metrica"] = "menos_acciones"; ganadores.append(g_act)

    g_cost = (costo.sort_values([COL["GRID"], "acciones_por_celda_prom"], ascending=[True, True])
                .groupby(COL["GRID"]).head(1)
                .loc[:, [COL["GRID"], COL["AGENT"], "acciones_por_celda_prom"]]
                .rename(columns={"acciones_por_celda_prom": "valor"}))
    g_cost["metrica"] = "menor_acciones_por_celda"; ganadores.append(g_cost)

    ganadores_df = pd.concat(ganadores, ignore_index=True)
    ganadores_df.to_csv(prefijo.with_name(f"{stem}_ganadores_por_grilla.csv"), index=False)

    print("Listo. Archivos guardados en:", dir_salida)
    for f in dir_salida.glob(f"{stem}_*.png"):
        print(" -", f.name)
    print(" -", f"{stem}_ganadores_por_grilla.csv")

if __name__ == "__main__":
    main()
