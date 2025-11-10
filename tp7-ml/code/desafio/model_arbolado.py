import os
import numpy as np
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    roc_auc_score,
    confusion_matrix,
    classification_report,
)
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder


RANDOM_STATE = 42

# Rutas RELATIVAS asumiendo que ejecutás el script desde el root del proyecto:
#   /home/julia/Hochschule/7.Semester/IA/ia-uncuyo-2025
DATA_DIR = "tp7-ml/data"
OUT_DIR = "tp7-ml/code/desafio"
os.makedirs(OUT_DIR, exist_ok=True)

TRAIN_CSV = os.path.join(DATA_DIR, "arbolado-mendoza-dataset-train.csv")
VAL_CSV   = os.path.join(DATA_DIR, "arbolado-mendoza-dataset-validation.csv")

# Ajustá este nombre al archivo de evaluación real de Kaggle:
EVAL_CSV  = os.path.join(DATA_DIR, "arbolado-mza-dataset-test.csv")

SUBMISSION_CSV = os.path.join(OUT_DIR, "submission.csv")


# -------------------------------------------------------------------
# Carga de datos
# -------------------------------------------------------------------


def cargar_train_val(train_path=TRAIN_CSV, val_path=VAL_CSV):
    train_df = pd.read_csv(train_path)
    val_df = pd.read_csv(val_path)
    return train_df, val_df


def cargar_eval(eval_path=EVAL_CSV):
    if not os.path.exists(eval_path):
        print(
            f"[AVISO] Archivo de evaluación no encontrado en: {eval_path}\n"
            "Ajustá la variable EVAL_CSV para que apunte al archivo correcto."
        )
        return None
    return pd.read_csv(eval_path)


# -------------------------------------------------------------------
# Preparación de features y pipeline
# -------------------------------------------------------------------


def preparar_X_y(df, target_col="inclinacion_peligrosa"):
    """
    Separa X e y, dropeando columnas irrelevantes:
    - id        (solo identificador)
    - ultima_modificacion (timestamp)
    - nombre_seccion      (texto redundante de seccion)
    """
    df = df.copy()

    # columnas a eliminar si existen
    drop_cols = []
    for col in ["id", "ultima_modificacion", "nombre_seccion"]:
        if col in df.columns:
            drop_cols.append(col)

    if target_col in df.columns:
        drop_cols.append(target_col)

    X = df.drop(columns=drop_cols)
    y = df[target_col].astype(int) if target_col in df.columns else None

    return X, y


def construir_pipeline(X):
    """
    Construye un pipeline de preprocesamiento + modelo:
    - OneHotEncoder para categóricas
    - RandomForestClassifier como modelo base
    """
    # Detectar tipos
    cat_cols = X.select_dtypes(include=["object"]).columns.tolist()
    num_cols = X.select_dtypes(exclude=["object"]).columns.tolist()

    print("[INFO] Columnas numéricas:", num_cols)
    print("[INFO] Columnas categóricas:", cat_cols)

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", "passthrough", num_cols),
            (
                "cat",
                OneHotEncoder(handle_unknown="ignore", sparse_output=False),
                cat_cols,
            ),
        ]
    )

    model = RandomForestClassifier(
        n_estimators=400,
        max_depth=None,
        min_samples_split=2,
        min_samples_leaf=1,
        n_jobs=-1,
        random_state=RANDOM_STATE,
        class_weight="balanced_subsample",
    )

    clf = Pipeline(
        steps=[
            ("preprocess", preprocessor),
            ("model", model),
        ]
    )

    return clf


# -------------------------------------------------------------------
# Evaluación local con validación y AUC
# -------------------------------------------------------------------


def evaluacion_local(train_df, val_df):
    """
    Entrena el modelo en train_df y evalúa en val_df con:
    - ROC AUC
    - Matriz de confusión (umbral 0.5 para clase 1)
    - classification_report simple
    """
    print("=== Evaluación local (train vs validation) ===")

    # Separar X,y
    X_train, y_train = preparar_X_y(train_df)
    X_val, y_val = preparar_X_y(val_df)

    # Construir pipeline
    clf = construir_pipeline(X_train)

    # Validación cruzada (AUC) solo con train_df (opcional pero útil)
    cv = StratifiedKFold(
        n_splits=5, shuffle=True, random_state=RANDOM_STATE
    )
    auc_scores = cross_val_score(
        clf, X_train, y_train, cv=cv, scoring="roc_auc"
    )
    print("AUC por fold (CV 5-fold):", auc_scores)
    print(
        "AUC media (CV): {:.4f} ± {:.4f}".format(
            auc_scores.mean(), auc_scores.std()
        )
    )

    # Entrenar en train completo y evaluar en validation
    clf.fit(X_train, y_train)

    # Probabilidades y clases para el conjunto de validación
    y_proba = clf.predict_proba(X_val)[:, 1]
    y_pred = (y_proba >= 0.5).astype(int)

    # AUC en validation
    auc_val = roc_auc_score(y_val, y_proba)
    print("AUC en validation: {:.4f}".format(auc_val))

    # Matriz de confusión
    cm = confusion_matrix(y_val, y_pred)
    print("Matriz de confusión (validation, umbral=0.5):")
    print(cm)

    print("Reporte de clasificación (validation):")
    print(classification_report(y_val, y_pred, digits=4))

    return clf, auc_val


# -------------------------------------------------------------------
# Entrenamiento final y generación de submission
# -------------------------------------------------------------------


def entrenar_modelo_final(train_df, val_df):
    """
    Entrena el modelo final usando train+validation completos.
    """
    df_full = pd.concat([train_df, val_df], ignore_index=True)
    X_full, y_full = preparar_X_y(df_full)

    clf = construir_pipeline(X_full)
    clf.fit(X_full, y_full)

    return clf


def generar_submission(clf, eval_df, out_path=SUBMISSION_CSV):
    """
    Genera archivo submission.csv con:
    ID,inclinacion_peligrosa
    usando predict_proba sobre el dataset de evaluación de Kaggle.
    """
    if "id" not in eval_df.columns:
        raise ValueError(
            "El dataset de evaluación debe contener una columna 'id'"
        )

    X_eval, _ = preparar_X_y(eval_df, target_col="inclinacion_peligrosa")

    # En el dataset de evaluación no está la variable objetivo; preparar_X_y la ignorará.
    # Nos aseguramos de no intentar acceder a y.

    X_eval = eval_df.drop(
        columns=[col for col in ["ultima_modificacion", "nombre_seccion"] if col in eval_df.columns]
    )
    # Volvemos a separar X para que coincida con las columnas usadas en entrenamiento
    # (sin 'id', sin target)
    if "inclinacion_peligrosa" in X_eval.columns:
        X_eval = X_eval.drop(columns=["inclinacion_peligrosa"])
    if "id" in X_eval.columns:
        X_eval = X_eval.drop(columns=["id"])

    # Probabilidades para la clase 1
    proba_eval = clf.predict_proba(X_eval)[:, 1]

    submission = pd.DataFrame(
        {
            "ID": eval_df["id"],
            "inclinacion_peligrosa": proba_eval,
        }
    )

    submission.to_csv(out_path, index=False)
    print(f"Archivo de submission guardado en: {out_path}")


# -------------------------------------------------------------------
# Main
# -------------------------------------------------------------------


def main():
    # 1) Cargar datasets
    train_df, val_df = cargar_train_val()

    # 2) Evaluación local
    _, auc_val = evaluacion_local(train_df, val_df)

    print("\n=== AUC en validation ===")
    print("AUC(validation) = {:.4f}".format(auc_val))
    print(
        "Recuerda que el objetivo es superar AUC > 0.69 en Kaggle; "
        "los valores locales pueden diferir del leaderboard."
    )

    # 3) Entrenar modelo final con train+validation completos
    print("\nEntrenando modelo final (train+validation completos)...")
    clf_final = entrenar_modelo_final(train_df, val_df)

    # 4) Generar submission sobre el dataset de evaluación de Kaggle
    eval_df = cargar_eval()
    if eval_df is not None:
        generar_submission(clf_final, eval_df, out_path=SUBMISSION_CSV)
    else:
        print(
            "No se generó submission porque no se encontró el archivo de evaluación. "
            "Ajustá la ruta EVAL_CSV cuando lo tengas."
        )


if __name__ == "__main__":
    main()
