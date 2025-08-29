# Reporte de evaluacion de desempeño
Vacuum Cleaner World - comparacion Random vs Reflex
## Descripcion del experimento
- Agentes evaluados: Random y Simple Reflex

## Metricas
- Cobertura
- Acciones = numeros de pasos consumidos por corrida
- Eficiencia = celdas limpiadas por accion
- Tasa de exito
- Tiempo de ejecucion = duracion por corrida

## Resultados
### Rendimiento por tamaño de grilla
- La cobertura cae fuertemente a medida que crece la grilla
- Reflex mantiene sistematicamente mayor  cobertura que Random en casi todos los tamaños
- En grillas grandes ambos agentes logran coberturas bajas, lo que surgiere que el tope de acciones limita la limpieza completa

#### Costo por tamaño de grilla
- Para grillas pequeñas, Reflex suele requerir menos acciones que Random
- A partir de grillas medianas, ambos de apoyan en el tope de 1000 acciones, convergiendo en el mismo costo y volviendo la comparacion sensible a la eficiencia con esa tope
- Con el mismo presupuesto de 1000 acciones, Reflex limpia sensiblemente mas celdas que Random, indicando mejor eficiencia bajo resticcion de pasos
- En corridas con menos acciones, tambien se observa que Reflex tiende a convertir acciones en celdas limpiadas de manera mas favorable
#### Tasa de exito
- La tasa de exito es 100% en ambos agentes a lo largo de los tamaños evaluados, es decir no se registraron fallas de ejecucion
#### Analisis por la tasa de suciedad
- En grillas pequeñas, mayor dirt_rate incrementa la cobertura porque el agente encuentra suciedad con mas facilidad. Reflex se beneficia mas de este efecto
#### Tiempos de ejecucion
- Random presenta mayor tiempo de ejecucion promedio y una dispersion relevante
- Simple Reflex tiende a ejecutar mas rapido, aunque con outliers en escenarios puntuales
## Discusion
### Ventajas de Simple Reflex
- Mejor cobertura que Random para la mayoria de los tamaños de grilla
- Mejor eficiencia bajo retriccione de 1000 accienoes: a igualdad de pasos, limpia mas celdas
- Menores tiempos de ejecucion promedio

### Desventajas de Reflex
- Recorre toda la grilla casi siempre -> en entornos con muy poca suciedad ineficiente

## Reproducibilidad
- Code estaba en una capeta `student_agents` y los resultados se generan en csv en la carpeta `batch_results`
- Generacion de la csv: `python3 -m student_agents.tests_julia_kroepfl`
- Generacion de graficos: `python student_agents/evaluacion.py --csv results_1756153529.csv`(nombre de la csv varia)