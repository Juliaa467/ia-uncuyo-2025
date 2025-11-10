import random
import time


def es_consistente(asignacion, fila_nueva, col_nueva):
    """
    Verifica si colocar una reina en (fila_nueva, col_nueva)
    es consistente con la asignación parcial actual.

    asignacion: diccionario {fila: columna}
    fila_nueva: fila donde se quiere colocar la nueva reina
    col_nueva: columna donde se quiere colocar la nueva reina
    """
    for fila_existente, col_existente in asignacion.items():
        # Misma columna
        if col_existente == col_nueva:
            return False
        # Misma diagonal
        if abs(col_existente - col_nueva) == abs(fila_existente - fila_nueva):
            return False
    return True


def resolver_n_reinas_backtracking(N, semilla=None):
    """
    Resuelve el problema de las N reinas usando backtracking simple.

    Devuelve:
      - solucion: diccionario {fila: columna} si se encontró solución, o None
      - nodos_explorados: cantidad de nodos visitados en el árbol de búsqueda
      - tiempo: tiempo de ejecución en segundos
    """
    if semilla is not None:
        random.seed(semilla)

    asignacion = {}
    nodos_explorados = 0

    def backtrack(fila):
        nonlocal nodos_explorados

        # Si ya asignamos todas las filas, encontramos una solución
        if fila == N:
            return True

        # Dominio de posibles columnas para esta fila
        valores = list(range(N))
        random.shuffle(valores)  # para variar el orden entre ejecuciones

        for col in valores:
            nodos_explorados += 1
            if es_consistente(asignacion, fila, col):
                asignacion[fila] = col
                if backtrack(fila + 1):
                    return True
                # backtrack
                del asignacion[fila]

        return False

    inicio = time.time()
    exito = backtrack(0)
    fin = time.time()

    if not exito:
        return None, nodos_explorados, fin - inicio
    return dict(asignacion), nodos_explorados, fin - inicio


def forward_check(asignacion, fila_asignada, col_asignada, dominios):
    """
    Aplica forward checking después de asignar (fila_asignada, col_asignada).

    dominios: dict {fila: lista de columnas posibles}
    Devuelve:
      - ok: True si no se vació ningún dominio, False en caso contrario
      - podas: lista de (fila, col) que se eliminaron para poder restaurarlas luego
    """
    podas = []

    for fila, valores in dominios.items():
        if fila == fila_asignada:
            continue
        if fila in asignacion:
            continue

        # Recorremos una copia porque vamos a modificar la lista
        for col in list(valores):
            # Misma columna o misma diagonal => valor inconsistente
            misma_columna = (col == col_asignada)
            misma_diagonal = (abs(col - col_asignada) == abs(fila - fila_asignada))

            if misma_columna or misma_diagonal:
                valores.remove(col)
                podas.append((fila, col))

        # Si algún dominio queda vacío, hay inconsistencia
        if len(valores) == 0:
            # deshacer podas antes de devolver False
            for f, c in podas:
                dominios[f].append(c)
            return False, []

    return True, podas


def resolver_n_reinas_forward_checking(N, semilla=None):
    """
    Resuelve el problema de las N reinas usando backtracking + forward checking.

    Devuelve:
      - solucion: diccionario {fila: columna} si se encontró solución, o None
      - nodos_explorados: cantidad de nodos visitados en el árbol de búsqueda
      - tiempo: tiempo de ejecución en segundos
    """
    if semilla is not None:
        random.seed(semilla)

    asignacion = {}
    nodos_explorados = 0

    # Dominio inicial: cualquier columna para cualquier fila
    dominios = {fila: list(range(N)) for fila in range(N)}

    def fc_rec(fila):
        nonlocal nodos_explorados

        # Si ya asignamos todas las filas, encontramos una solución
        if fila == N:
            return True

        # Trabajamos con una copia del dominio actual de la fila
        valores = list(dominios[fila])
        random.shuffle(valores)

        for col in valores:
            nodos_explorados += 1
            if es_consistente(asignacion, fila, col):
                asignacion[fila] = col

                # Aplicar forward checking
                ok, podas = forward_check(asignacion, fila, col, dominios)

                if ok:
                    if fc_rec(fila + 1):
                        return True

                # Restaurar dominios y asignación
                for f, c in podas:
                    dominios[f].append(c)
                del asignacion[fila]

        return False

    inicio = time.time()
    exito = fc_rec(0)
    fin = time.time()

    if not exito:
        return None, nodos_explorados, fin - inicio
    return dict(asignacion), nodos_explorados, fin - inicio


# Ejemplo de uso básico
if __name__ == "__main__":
    N = 8

    print("Backtracking puro:")
    solucion_bt, nodos_bt, tiempo_bt = resolver_n_reinas_backtracking(N, semilla=0)
    print("  Solución:", solucion_bt)
    print("  Nodos explorados:", nodos_bt)
    print("  Tiempo (s):", tiempo_bt)

    print("\nForward checking:")
    solucion_fc, nodos_fc, tiempo_fc = resolver_n_reinas_forward_checking(N, semilla=0)
    print("  Solución:", solucion_fc)
    print("  Nodos explorados:", nodos_fc)
    print("  Tiempo (s):", tiempo_fc)
