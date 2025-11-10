# archivo: experimentos_n_reinas.py
import csv
import os
import statistics as stats

from n_reinas_csp import (
    resolver_n_reinas_backtracking,
    resolver_n_reinas_forward_checking,
)

# Directorio de este archivo: .../tp5-csp/code
DIR_CODE = os.path.dirname(os.path.abspath(__file__))

# Directorio tp5-csp (padre de code)
DIR_TP5 = os.path.dirname(DIR_CODE)

# Ruta al CSV en tp5-csp
CSV_PATH = os.path.join(DIR_TP5, "tp5-Nreinas.csv")

# Carpeta images dentro de tp5-csp
IMAGES_DIR = os.path.join(DIR_TP5, "images")


def correr_experimentos(Ns=(4, 8, 10), num_semillas=30, output_csv=CSV_PATH):
    resultados = []

    for N in Ns:
        for semilla in range(num_semillas):
            # Backtracking
            sol_bt, nodos_bt, tiempo_bt = resolver_n_reinas_backtracking(N, semilla=semilla)
            exito_bt = sol_bt is not None
            resultados.append(
                {
                    "algoritmo": "backtracking",
                    "N": N,
                    "semilla": semilla,
                    "exito": int(exito_bt),
                    "tiempo": tiempo_bt,
                    "nodos": nodos_bt,
                }
            )

            # Forward checking
            sol_fc, nodos_fc, tiempo_fc = resolver_n_reinas_forward_checking(N, semilla=semilla)
            exito_fc = sol_fc is not None
            resultados.append(
                {
                    "algoritmo": "forward_checking",
                    "N": N,
                    "semilla": semilla,
                    "exito": int(exito_fc),
                    "tiempo": tiempo_fc,
                    "nodos": nodos_fc,
                }
            )

    # Guardar CSV (punto 5a) en tp5-csp
    with open(output_csv, "w", newline="") as f:
        fieldnames = ["algoritmo", "N", "semilla", "exito", "tiempo", "nodos"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(resultados)

    return resultados


def calcular_estadisticas(resultados):
    """
    Punto 5b:
      - porcentaje de ejecuciones con solución válida
      - tiempo medio y desviación estándar
      - nodos medios y desviación estándar
    Solo se consideran las ejecuciones donde exito == 1.
    """
    print("Resumen estadístico por algoritmo y tamaño N\n")

    # clave: (algoritmo, N)
    grupos = {}
    for r in resultados:
        clave = (r["algoritmo"], r["N"])
        grupos.setdefault(clave, []).append(r)

    for (algoritmo, N), regs in sorted(grupos.items(), key=lambda x: (x[0][0], x[0][1])):
        total = len(regs)
        exitos = [r for r in regs if r["exito"] == 1]
        num_exitos = len(exitos)
        porcentaje_exito = 100.0 * num_exitos / total if total > 0 else 0.0

        if num_exitos > 0:
            tiempos = [r["tiempo"] for r in exitos]
            nodos = [r["nodos"] for r in exitos]

            tiempo_prom = stats.mean(tiempos)
            tiempo_std = stats.stdev(tiempos) if len(tiempos) > 1 else 0.0

            nodos_prom = stats.mean(nodos)
            nodos_std = stats.stdev(nodos) if len(nodos) > 1 else 0.0
        else:
            tiempo_prom = tiempo_std = nodos_prom = nodos_std = float("nan")

        print(f"Algoritmo: {algoritmo}, N = {N}")
        print(f"  Ejecuciones totales: {total}")
        print(f"  Ejecuciones con solución: {num_exitos} ({porcentaje_exito:.2f}%)")
        print(f"  Tiempo medio (s): {tiempo_prom:.6f}  |  Desv. std: {tiempo_std:.6f}")
        print(f"  Nodos medios: {nodos_prom:.2f}       |  Desv. std: {nodos_std:.2f}")
        print()


def generar_boxplots(resultados, carpeta_imagenes=IMAGES_DIR):
    """
    Punto 5c: genera boxplots de tiempos y nodos por algoritmo y N.
    Crea una imagen por N para tiempos y otra para nodos,
    dentro de tp5-csp/images.
    """
    import matplotlib.pyplot as plt

    os.makedirs(carpeta_imagenes, exist_ok=True)

    Ns = sorted(set(r["N"] for r in resultados))
    algoritmos = ["backtracking", "forward_checking"]

    for N in Ns:
        datos_N = [r for r in resultados if r["N"] == N and r["exito"] == 1]
        if not datos_N:
            continue

        tiempos_por_alg = []
        nodos_por_alg = []
        etiquetas = []

        for alg in algoritmos:
            datos_alg = [r for r in datos_N if r["algoritmo"] == alg]
            if not datos_alg:
                continue

            tiempos = [r["tiempo"] for r in datos_alg]
            nodos = [r["nodos"] for r in datos_alg]

            tiempos_por_alg.append(tiempos)
            nodos_por_alg.append(nodos)
            etiquetas.append(alg)

        if not etiquetas:
            continue

        # Boxplot tiempos
        plt.figure()
        plt.boxplot(tiempos_por_alg, labels=etiquetas)
        plt.xlabel("Algoritmo")
        plt.ylabel("Tiempo de ejecución (s)")
        plt.title(f"Distribución de tiempos para N = {N}")
        plt.tight_layout()
        ruta_tiempos = os.path.join(carpeta_imagenes, f"boxplot_tiempos_N{N}.png")
        plt.savefig(ruta_tiempos)
        plt.close()

        # Boxplot nodos
        plt.figure()
        plt.boxplot(nodos_por_alg, labels=etiquetas)
        plt.xlabel("Algoritmo")
        plt.ylabel("Nodos explorados")
        plt.title(f"Distribución de nodos explorados para N = {N}")
        plt.tight_layout()
        ruta_nodos = os.path.join(carpeta_imagenes, f"boxplot_nodos_N{N}.png")
        plt.savefig(ruta_nodos)
        plt.close()

        print(f"Boxplots generados para N = {N}:")
        print(f"  {ruta_tiempos}")
        print(f"  {ruta_nodos}")
        print()


if __name__ == "__main__":
    resultados = correr_experimentos(Ns=(4, 8, 10), num_semillas=30)
    calcular_estadisticas(resultados)
    generar_boxplots(resultados)
