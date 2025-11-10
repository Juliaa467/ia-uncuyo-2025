import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split, StratifiedKFold
from sklearn.metrics import confusion_matrix
from sklearn.tree import DecisionTreeClassifier

# -------------------------------------------------------------------
# 0. Configuración básica
# -------------------------------------------------------------------

RANDOM_STATE = 42

DATA_DIR = "tp7-ml/data"
FIG_DIR = "tp7-ml/figures"

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(FIG_DIR, exist_ok=True)

# Nombre del archivo original descargado desde Kaggle
ORIGINAL_CSV = os.path.join(DATA_DIR, "dataset", "arbolado-mza-dataset.csv")

# Si querés automatizar la descarga desde Python (opcional):
# os.system("kaggle competitions download -c arbolado-publico-mendoza-2025 -p tp7-ml/data")
# os.system(f"unzip -o {os.path.join(DATA_DIR, 'arbolado-publico-mendoza-2025.zip')} -d {DATA_DIR}")


# -------------------------------------------------------------------
# 1. Cargar y dividir el dataset en train / validation
#    (Ejercicio 1)
# -------------------------------------------------------------------

def cargar_dataset(path=ORIGINAL_CSV):
    df = pd.read_csv(path)
    return df


def crear_train_validation(df, test_size=0.2, random_state=RANDOM_STATE, estratificado=True):
    if estratificado:
        train_df, val_df = train_test_split(
            df,
            test_size=test_size,
            random_state=random_state,
            stratify=df["inclinacion_peligrosa"]
        )
    else:
        train_df, val_df = train_test_split(
            df,
            test_size=test_size,
            random_state=random_state
        )
    return train_df, val_df


def guardar_splits(train_df, val_df):
    train_path = os.path.join(DATA_DIR, "arbolado-mendoza-dataset-train.csv")
    val_path = os.path.join(DATA_DIR, "arbolado-mendoza-dataset-validation.csv")
    train_df.to_csv(train_path, index=False)
    val_df.to_csv(val_path, index=False)
    print("Guardado:", train_path, val_path)


# -------------------------------------------------------------------
# 2. Análisis de distribución de clases, secciones y especies
#    (Ejercicio 2)
# -------------------------------------------------------------------

def plot_distribucion_clase(train_df):
    plt.figure(figsize=(5, 4))
    ax = sns.countplot(
        x="inclinacion_peligrosa",
        data=train_df
    )
    ax.set_title("Distribución de la clase inclinacion_peligrosa")
    ax.set_xlabel("inclinacion_peligrosa")
    ax.set_ylabel("Cantidad de árboles")

    for p in ax.patches:
        altura = p.get_height()
        ax.annotate(
            f"{altura}",
            (p.get_x() + p.get_width() / 2., altura),
            ha='center', va='bottom', fontsize=9
        )

    out_path = os.path.join(FIG_DIR, "dist_inclinacion_peligrosa.png")
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()
    print("Gráfico guardado:", out_path)


def plot_secciones_peligrosas(train_df, min_muestras=50):
    # detectar nombre correcto de la columna sección
    col_seccion = "Seccion" if "Seccion" in train_df.columns else "seccion"

    # Proporción de inclinación peligrosa por sección
    secc = (
        train_df
        .groupby(col_seccion, dropna=False)["inclinacion_peligrosa"]
        .agg(["mean", "count"])
        .reset_index()
    )
    secc_filtrado = secc[secc["count"] >= min_muestras].copy()
    secc_filtrado = secc_filtrado.sort_values("mean", ascending=False)

    plt.figure(figsize=(8, 4))
    ax = sns.barplot(
        data=secc_filtrado,
        x=col_seccion,
        y="mean"
    )
    ax.set_xticklabels(ax.get_xticklabels(), rotation=90)
    ax.set_ylabel("Proporción de árboles peligrosos")
    ax.set_xlabel("Sección")
    ax.set_title("Proporción de inclinación peligrosa por sección")

    out_path = os.path.join(FIG_DIR, "secciones_peligrosas.png")
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()
    print("Gráfico guardado:", out_path)



def plot_especies_peligrosas(train_df, top_n=15, min_muestras=30):
    especies = (
        train_df
        .groupby("especie", dropna=False)["inclinacion_peligrosa"]
        .agg(["mean", "count"])
        .reset_index()
    )
    especies_filtrado = especies[especies["count"] >= min_muestras].copy()
    especies_filtrado = especies_filtrado.sort_values("mean", ascending=False).head(top_n)

    plt.figure(figsize=(8, 6))
    ax = sns.barplot(
        data=especies_filtrado,
        x="mean",
        y="especie"
    )
    ax.set_xlabel("Proporción de árboles peligrosos")
    ax.set_ylabel("Especie")
    ax.set_title("Especies con mayor proporción de inclinación peligrosa")

    out_path = os.path.join(FIG_DIR, "especies_peligrosas_top.png")
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()
    print("Gráfico guardado:", out_path)


# -------------------------------------------------------------------
# 3. Histograma circ_tronco_cm y variable categórica
#    (Ejercicio 3)
# -------------------------------------------------------------------

def plot_hist_circ_tronco(train_df, bins_list=(10, 20, 50)):
    for bins in bins_list:
        plt.figure(figsize=(6, 4))
        train_df["circ_tronco_cm"].hist(bins=bins)
        plt.xlabel("circ_tronco_cm")
        plt.ylabel("Frecuencia")
        plt.title(f"Histograma circ_tronco_cm (bins = {bins})")

        out_path = os.path.join(FIG_DIR, f"hist_circ_tronco_cm_bins_{bins}.png")
        plt.tight_layout()
        plt.savefig(out_path)
        plt.close()
        print("Gráfico guardado:", out_path)


def plot_hist_circ_tronco_por_clase(train_df, bins=30):
    plt.figure(figsize=(7, 4))
    sns.histplot(
        data=train_df,
        x="circ_tronco_cm",
        hue="inclinacion_peligrosa",
        bins=bins,
        kde=False,
        stat="count",
        common_norm=False
    )
    plt.xlabel("circ_tronco_cm")
    plt.ylabel("Frecuencia")
    plt.title("Histograma circ_tronco_cm por clase de inclinación peligrosa")

    out_path = os.path.join(FIG_DIR, f"hist_circ_tronco_cm_por_clase_bins_{bins}.png")
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()
    print("Gráfico guardado:", out_path)


def agregar_categorias_circ_tronco(train_df):
    """
    Crea la variable circ_tronco_cm_cat con 4 categorías.
    Acá uso los cuartiles como ejemplo de cortes.
    Podés ajustar estos puntos de corte según lo que veas en los histogramas.
    """
    serie = train_df["circ_tronco_cm"].dropna()
    q = serie.quantile([0.25, 0.5, 0.75])

    bins = [-np.inf, q[0.25], q[0.5], q[0.75], np.inf]
    labels = ["bajo", "medio", "alto", "muy alto"]

    train_df = train_df.copy()
    train_df["circ_tronco_cm_cat"] = pd.cut(
        train_df["circ_tronco_cm"],
        bins=bins,
        labels=labels,
        include_lowest=True
    )
    return train_df, bins, labels


def guardar_train_con_categorias(train_df):
    train_df_cat, bins, labels = agregar_categorias_circ_tronco(train_df)
    out_path = os.path.join(DATA_DIR, "arbolado-mendoza-dataset-circ_tronco_cm-train.csv")
    train_df_cat.to_csv(out_path, index=False)
    print("Guardado:", out_path)
    print("Cortes usados para circ_tronco_cm_cat:", bins, "con labels", labels)
    return train_df_cat


# -------------------------------------------------------------------
# 4. Clasificador aleatorio
#    (Ejercicio 4)
# -------------------------------------------------------------------

def random_classifier(df, threshold=0.5, random_state=None):
    rng = np.random.default_rng(random_state)
    df = df.copy()
    df["prediction_prob"] = rng.random(len(df))
    df["prediction_class"] = (df["prediction_prob"] > threshold).astype(int)
    return df


def confusion_y_metricas(y_true, y_pred):
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()

    accuracy = (tp + tn) / (tp + tn + fp + fn)
    precision = tp / (tp + fp) if (tp + fp) > 0 else np.nan
    sensitivity = tp / (tp + fn) if (tp + fn) > 0 else np.nan
    specificity = tn / (tn + fp) if (tn + fp) > 0 else np.nan

    return {
        "TP": tp,
        "TN": tn,
        "FP": fp,
        "FN": fn,
        "Accuracy": accuracy,
        "Precision": precision,
        "Sensitivity": sensitivity,
        "Specificity": specificity
    }


def evaluar_random_classifier(val_df, random_state=RANDOM_STATE):
    df_pred = random_classifier(val_df, random_state=random_state)
    y_true = df_pred["inclinacion_peligrosa"].values
    y_pred = df_pred["prediction_class"].values
    resultados = confusion_y_metricas(y_true, y_pred)
    return df_pred, resultados


# -------------------------------------------------------------------
# 5. Clasificador por clase mayoritaria
#    (Ejercicio 5)
# -------------------------------------------------------------------

def clase_mayoritaria(train_df):
    return train_df["inclinacion_peligrosa"].value_counts().idxmax()


def biggerclass_classifier(df, clase_mayor):
    df = df.copy()
    df["prediction_class"] = clase_mayor
    return df


def evaluar_biggerclass_classifier(train_df, val_df):
    may = clase_mayoritaria(train_df)
    df_pred = biggerclass_classifier(val_df, may)
    y_true = df_pred["inclinacion_peligrosa"].values
    y_pred = df_pred["prediction_class"].values
    resultados = confusion_y_metricas(y_true, y_pred)
    return df_pred, resultados, may


# -------------------------------------------------------------------
# 6. Cross-validation con árbol de decisión
#    (Ejercicio 7 adaptado a Python)
# -------------------------------------------------------------------

def preparar_features(df):
    """
    Prepara X e y para el árbol de decisión.
    Asume que inclinacion_peligrosa es la variable objetivo.
    Convierte columnas categóricas (ej. altura, seccion, especie) a códigos numéricos.
    Ajusta los nombres según las columnas reales del CSV.
    """
    df_enc = df.copy()

    # Nombres de columnas según el dataset de Kaggle
    col_altura = "altura"              # en tu dataset es categórica tipo "Medio (4 - 8 mts)"
    col_circ = "circ_tronco_cm"
    col_lat = "Lat" if "Lat" in df_enc.columns else "lat"
    col_long = "Long" if "Long" in df_enc.columns else "long"
    col_seccion = "Seccion" if "Seccion" in df_enc.columns else "seccion"
    col_especie = "especie"            # viene en minúscula

    feature_cols = [col_altura, col_circ, col_lat, col_long, col_seccion, col_especie]

    # Cualquier columna de estas que sea tipo object, la factorizamos
    for col in feature_cols:
        if df_enc[col].dtype == "object":
            df_enc[col], _ = pd.factorize(df_enc[col])

    X = df_enc[feature_cols]
    y = df_enc["inclinacion_peligrosa"].astype(int)

    return X, y, feature_cols




def cross_validation_tree(df, k=5, random_state=RANDOM_STATE):
    X, y, feature_cols = preparar_features(df)

    skf = StratifiedKFold(n_splits=k, shuffle=True, random_state=random_state)

    registros = []

    for fold, (train_idx, test_idx) in enumerate(skf.split(X, y), start=1):
        X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
        y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]

        clf = DecisionTreeClassifier(random_state=random_state)
        clf.fit(X_train, y_train)
        y_pred = clf.predict(X_test)

        metr = confusion_y_metricas(y_test, y_pred)
        metr["fold"] = fold
        registros.append(metr)

    df_metrics = pd.DataFrame(registros)

    resumen = pd.DataFrame({
        "Métrica": ["Accuracy", "Precision", "Sensitivity", "Specificity"],
        "Media": [
            df_metrics["Accuracy"].mean(),
            df_metrics["Precision"].mean(),
            df_metrics["Sensitivity"].mean(),
            df_metrics["Specificity"].mean()
        ],
        "DesvStd": [
            df_metrics["Accuracy"].std(ddof=1),
            df_metrics["Precision"].std(ddof=1),
            df_metrics["Sensitivity"].std(ddof=1),
            df_metrics["Specificity"].std(ddof=1)
        ]
    })

    return df_metrics, resumen, feature_cols


# -------------------------------------------------------------------
# 7. Ejemplo de flujo completo si ejecutás este script directamente
# -------------------------------------------------------------------

if __name__ == "__main__":
    # 1) Cargar y dividir
    df = cargar_dataset()
    train_df, val_df = crear_train_validation(df)
    guardar_splits(train_df, val_df)

    # 2) EDA: gráficos
    plot_distribucion_clase(train_df)
    plot_secciones_peligrosas(train_df)
    plot_especies_peligrosas(train_df)

    # 3) Histograma circ_tronco_cm y categorización
    plot_hist_circ_tronco(train_df)
    plot_hist_circ_tronco_por_clase(train_df, bins=30)
    train_df_cat = guardar_train_con_categorias(train_df)

    # 4) Clasificador aleatorio
    _, res_random = evaluar_random_classifier(val_df)
    print("Resultados clasificador aleatorio:", res_random)

    # 5) Clasificador clase mayoritaria
    _, res_majority, may = evaluar_biggerclass_classifier(train_df, val_df)
    print("Clase mayoritaria:", may)
    print("Resultados clasificador clase mayoritaria:", res_majority)

    # 6) Cross-validation con árbol de decisión
    df_folds, resumen_cv, features = cross_validation_tree(train_df)
    print("Features usadas en el árbol:", features)
    print("Resumen CV:")
    print(resumen_cv)
