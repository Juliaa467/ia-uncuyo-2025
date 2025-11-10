# Trabajo Práctico 7B – Parte II  
## Desafío Kaggle: Peligrosidad del arbolado público de Mendoza

---

## 1. Preprocesamiento de los datos

Para este desafío se trabajó con los conjuntos generados en la Parte I:

- `tp7-ml/data/arbolado-mendoza-dataset-train.csv`
- `tp7-ml/data/arbolado-mendoza-dataset-validation.csv`

El objetivo es predecir la variable binaria `inclinacion_peligrosa` a partir de variables biológicas y geográficas del arbolado.

### 1.1. Selección de variables

Se eliminaron columnas no informativas o redundantes:

- `id`
- `ultima_modificacion`
- `nombre_seccion`

Las variables restantes se agruparon según su tipo:

- Numéricas: `circ_tronco_cm`, `long`, `lat`, `seccion`, `area_seccion`
- Categóricas: `especie`, `altura`, `diametro_tronco`

### 1.2. Transformaciones aplicadas

- Se utilizó un `ColumnTransformer` para aplicar:
  - **OneHotEncoder** sobre las variables categóricas.
  - **Passthrough** (sin transformación) sobre las numéricas.
- No se aplicó escalado ya que los árboles no lo requieren.
- Se estableció `class_weight="balanced_subsample"` para compensar el desbalance entre clases.

---

## 2. Modelo propuesto

El modelo principal fue un **RandomForestClassifier** con los siguientes parámetros:

- `n_estimators = 400`
- `max_depth = None`
- `random_state = 42`
- `class_weight = "balanced_subsample"`
- `n_jobs = -1`

Este modelo combina múltiples árboles de decisión entrenados con subconjuntos aleatorios del dataset, reduciendo la varianza y mejorando la capacidad de generalización.

---

## 3. Validación cruzada (5 folds)

Se aplicó una validación cruzada estratificada con 5 particiones (`StratifiedKFold`), evaluando la métrica **ROC AUC**.

Resultados obtenidos:

| Fold | AUC  |
|------|------:|
| 1 | 0.7475 |
| 2 | 0.7606 |
| 3 | 0.7317 |
| 4 | 0.7507 |
| 5 | 0.7191 |

**Promedio AUC (CV): 0.7419 ± 0.0147**

---

## 4. Resultados sobre el conjunto de validación

El modelo final entrenado sobre el conjunto de entrenamiento obtuvo:

**AUC(validation) = 0.7493**

Este valor supera ampliamente el umbral de 0.69 solicitado por la cátedra.

### 4.1. Matriz de confusión

Umbral de decisión: 0.5

|                     | Pred. No Peligroso | Pred. Peligroso |
|---------------------|--------------------:|----------------:|
| **Real No Peligroso** | 5530 | 137 |
| **Real Peligroso**    | 638 | 78 |

### 4.2. Métricas de clasificación

| Métrica | Valor |
|----------|-------:|
| Accuracy | 0.8786 |
| Precision (clase 1) | 0.3628 |
| Recall (clase 1) | 0.1089 |
| Specificity | 0.9758 |
| F1-score (clase 1) | 0.1676 |

Comentarios:
- Excelente desempeño en la clase mayoritaria (árboles no peligrosos).
- Sensibilidad baja en la clase minoritaria, esperable por el desbalance.
- AUC elevado indica buena capacidad de discriminación global.

---

## 5. Envío a Kaggle

Para el envío se entrena nuevamente el modelo usando `train + validation` y se predicen probabilidades para el conjunto de evaluación (`arbolado-mendoza-dataset-eval.csv`).

El archivo final se guarda como: `tp7-ml/code/desafio/submission.csv` 
con el formato:

```text
ID,inclinacion_peligrosa
1,0.14
2,0.03
3,0.89
...

