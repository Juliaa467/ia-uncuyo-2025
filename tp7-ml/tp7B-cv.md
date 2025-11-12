# Trabajo Práctico 7B – Parte I  
## Validación cruzada con árbol de decisión

---

### 1. Descripción general

Se implementó la validación cruzada k-fold para estimar el rendimiento de un **árbol de decisión** sobre el dataset *arbolado público de Mendoza*.  
El proceso consiste en dividir el conjunto de entrenamiento en *k* subconjuntos estratificados y evaluar el modelo rotando cada fold como conjunto de test.  
Las métricas calculadas en cada iteración fueron: Accuracy, Precision, Sensitivity y Specificity.

---

### 2. Código utilizado

```r
# Ejemplo en R (adaptado del ejercicio 7)
library(rpart)

create_folds <- function(df, k) {
  set.seed(42)
  n <- nrow(df)
  folds <- sample(rep(1:k, length.out = n))
  split(1:n, folds)
}

cross_validation <- function(df, k = 5) {
  folds <- create_folds(df, k)
  resultados <- data.frame()

  for (i in 1:k) {
    test_idx <- folds[[i]]
    train_data <- df[-test_idx, ]
    test_data <- df[test_idx, ]

    modelo <- rpart(inclinacion_peligrosa ~ altura + circ_tronco_cm +
                    lat + long + seccion + especie,
                    data = train_data, method = "class")

    pred <- predict(modelo, test_data, type = "class")

    cm <- table(test_data$inclinacion_peligrosa, pred)
    TP <- cm[2, 2]; TN <- cm[1, 1]
    FP <- cm[1, 2]; FN <- cm[2, 1]

    accuracy <- (TP + TN) / sum(cm)
    precision <- TP / (TP + FP)
    sensitivity <- TP / (TP + FN)
    specificity <- TN / (TN + FP)

    resultados <- rbind(resultados, data.frame(
      fold = i, accuracy, precision, sensitivity, specificity
    ))
  }

  resumen <- data.frame(
    Métrica = c("Accuracy", "Precision", "Sensitivity", "Specificity"),
    Media = c(mean(resultados$accuracy),
              mean(resultados$precision),
              mean(resultados$sensitivity),
              mean(resultados$specificity)),
    DesvStd = c(sd(resultados$accuracy),
                sd(resultados$precision),
                sd(resultados$sensitivity),
                sd(resultados$specificity))
  )

  return(resumen)
}
```
### 3. Resultados obtenidos

| Métrica       | Media   | DesvStd |
|----------------|---------|---------|
| Accuracy       | 0.8251  | 0.0035  |
| Precision      | 0.2377  | 0.0101  |
| Sensitivity    | 0.2536  | 0.0119  |
| Specificity    | 0.8972  | 0.0040  |

El modelo de árbol de decisión muestra un rendimiento estable a lo largo de los folds, con una precisión general alta (≈82.5%) y una especificidad cercana al 90%.  
La precisión y sensibilidad son moderadas, lo que sugiere que el modelo identifica correctamente la mayoría de los árboles no peligrosos, aunque aún falla en detectar una parte importante de los peligrosos.

---

### 4. Conclusión

La validación cruzada refleja un comportamiento típico en conjuntos desbalanceados: el árbol de decisión logra buena exactitud global gracias a su alta especificidad, pero su capacidad de detección de la clase minoritaria (árboles peligrosos) es limitada.  
Estos resultados constituyen una base sólida sobre la cual mejorar el desempeño mediante modelos más avanzados (por ejemplo, Random Forest o técnicas de balanceo de clases) en el desafío de Kaggle.

