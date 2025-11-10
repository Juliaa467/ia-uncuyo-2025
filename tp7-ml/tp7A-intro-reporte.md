# Trabajo Práctico 7A – Introducción

## 1. Métodos flexibles vs inflexibles

### a) n extremadamente grande, p pequeño
Un método flexible suele comportarse mejor. Hay muchos datos para estimar una relación compleja sin que la varianza del estimador explote. El riesgo de sobreajuste baja al crecer n, mientras que un método rígido puede tener demasiado sesgo si la relación real no es tan simple.

### b) p extremadamente grande, n pequeño
Un método flexible tiende a funcionar peor. Con pocos datos y muchos predictores la varianza del modelo flexible es muy alta y se sobreajusta el ruido. Un método menos flexible suele ser preferible porque reduce la varianza, aunque aumente el sesgo.

### c) Relación altamente no lineal
En este escenario un método flexible se espera que funcione mejor, porque puede aproximar relaciones no lineales complejas entre X e Y. Un método inflexible tendría un sesgo grande al no poder capturar bien la forma verdadera de la función.

### d) Varianza del error σ² extremadamente alta
Si el ruido es muy grande, un método flexible corre más riesgo de “perseguir” el ruido y sobreajustar. Un método menos flexible, al ser más suave, suele ser preferible: mantiene menor varianza del estimador y no reacciona tanto a fluctuaciones aleatorias.

---

## 2. Clasificación vs regresión, inferencia vs predicción, n y p

### a) Empresas y salario del CEO
- Variable respuesta: salario del CEO (cuantitativa continua).  
- Tipo de problema: regresión.  
- Interés principal: inferencia.  
- n = 500 (empresas).  
- p = 3 (ganancias, número de empleados, industria).  

### b) Nuevo producto: éxito o fracaso
- Variable respuesta: éxito / fracaso (categórica binaria).  
- Tipo de problema: clasificación.  
- Interés principal: predicción.  
- n = 20 (productos previos).  
- p = 13 (precio, presupuesto de marketing, precio de la competencia, 10 variables adicionales).  

### c) % de cambio USD/Euro
- Variable respuesta: % de cambio semanal (cuantitativa).  
- Tipo de problema: regresión.  
- Interés principal: predicción.  
- n ≈ 52 (observaciones semanales).  
- p = 3 (mercados estadounidense, británico, alemán).

---

## 3. Ventajas y desventajas de un enfoque muy flexible

### Ventajas
- Menor sesgo, capaz de aproximar relaciones complejas.  
- Mejor desempeño predictivo cuando la relación real es no lineal.  

### Desventajas
- Mayor varianza, mayor riesgo de sobreajuste.  
- Menor interpretabilidad.  
- Mayor costo computacional y sensibilidad a outliers.

### Cuándo preferir cada uno
- **Más flexible:** relaciones no lineales, n grande, objetivo predictivo.  
- **Menos flexible:** n pequeño o p grande, objetivo interpretativo, relaciones simples.

---

## 4. Enfoque paramétrico vs no paramétrico

### Enfoque paramétrico
- Supone una forma funcional (ej. lineal) y estima pocos parámetros.  
- Ventajas: menor varianza, interpretabilidad, menos datos necesarios.  
- Desventajas: alto sesgo si el modelo está mal especificado, poca flexibilidad.

### Enfoque no paramétrico
- No asume forma funcional fija; se adapta a los datos.  
- Ventajas: mucha flexibilidad, bajo sesgo si la relación es compleja.  
- Desventajas: alta varianza, requiere muchos datos, menos interpretabilidad.

**Resumen:**  
Paramétrico → interpretabilidad y simplicidad.  
No paramétrico → flexibilidad y capacidad de modelar relaciones complejas.

---

## 5. K vecinos más cercanos (KNN)

Datos: (X1, X2, X3, Y)  
Punto de prueba: X1 = X2 = X3 = 0

### a) Distancias Euclidianas

| Obs | (X1, X2, X3) | Y     | Distancia |
|-----|---------------|-------|------------|
| 1   | (0, 3, 0)     | Rojo  | 3,0000     |
| 2   | (2, 0, 0)     | Rojo  | 2,0000     |
| 3   | (0, 1, 3)     | Rojo  | 3,1623     |
| 4   | (0, 1, 2)     | Verde | 2,2361     |
| 5   | (−1, 0, 1)    | Verde | 1,4142     |
| 6   | (1, 1, 1)     | Rojo  | 1,7321     |

### b) Predicción con K = 1
Vecino más cercano: obs. 5 → Verde.  
**Predicción:** Verde.

### c) Predicción con K = 3
Vecinos más cercanos: obs. 5 (Verde), obs. 6 (Rojo), obs. 2 (Rojo).  
**Clase mayoritaria:** Rojo.  
**Predicción:** Rojo.

### d) Elección de K según límite de Bayes
Si el límite de Bayes es altamente no lineal, se prefiere un **K pequeño** para mayor flexibilidad (bajo sesgo, alta varianza).  
K grande produce fronteras más suaves y simples (alto sesgo, baja varianza).
