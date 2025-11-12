a) **Jugar al CS**  
Performance: kills, muertes, distancia cumplida, victoria  
Environment: mapa del juego  
Actuators: disparar, correr, esconderse, cambiar munición  
Sensors: imágenes de la pantalla, sonidos, cantidad de munición, vida (hitpoints)  

**Propiedades del entorno:**  
- Parcialmente observable (el agente no ve detrás de paredes ni al enemigo oculto)  
- Estocástico (hay incertidumbre en los movimientos del rival y disparos)  
- Secuencial (las acciones afectan los estados futuros)  
- Dinámico (el entorno cambia con el tiempo y las acciones de otros agentes)  
- Continuo (movimiento y percepción en tiempo real)  
- Multiagente (interacción con otros jugadores)

---

b) **Explorar los océanos**  
Performance: número de objetos descubiertos e identificados, distancia recorrida  
Environment: océano  
Actuators: moverse (abajo/arriba/derecha/izquierda), grabar videos o fotos, encender/apagar luz  
Sensors: cámara, ubicación, sensores de profundidad y temperatura  

**Propiedades del entorno:**  
- Parcialmente observable (limitación por visibilidad o alcance de sensores)  
- Estocástico (condiciones del mar y fauna impredecibles)  
- Secuencial (cada decisión afecta futuras posiciones y hallazgos)  
- Dinámico (el entorno puede cambiar constantemente)  
- Continuo (espacio tridimensional y tiempo real)  
- Agente único (el explorador actúa solo)

---

c) **Comprar y vender tokens crypto**  
Performance: ganancia o pérdida de dinero  
Environment: mercado financiero  
Actuators: comprar, vender  
Sensors: precios, volumen, noticias externas  

**Propiedades del entorno:**  
- Parcialmente observable (no se conocen todas las variables que afectan el mercado)  
- Estocástico (fluctuaciones de precios impredecibles)  
- Secuencial (las decisiones pasadas influyen en la estrategia futura)  
- Dinámico (el entorno cambia constantemente con cada transacción)  
- Discreto (acciones y estados definidos en pasos temporales)  
- Multiagente (muchos participantes influyen en el mercado)

---

d) **Practicar tenis contra una pared**  
Performance: precisión, consistencia, velocidad  
Environment: pista y pared  
Actuators: golpe de raqueta, desplazamiento  
Sensors: cámara, micrófono, distancia hasta la pared  

**Propiedades del entorno:**  
- Totalmente observable (el agente percibe la pelota y la pared)  
- Determinístico (el rebote sigue leyes físicas predecibles)  
- Secuencial (cada golpe influye en el siguiente)  
- Semidinámico (si el jugador se mueve o cambia su fuerza, el entorno responde)  
- Continuo (movimientos y tiempo reales)  
- Agente único

---

e) **Realizar un salto de altura**  
Performance: altura alcanzada, cantidad de intentos hasta el éxito  
Environment: pista de salto  
Actuators: carrera, impulso, salto  
Sensors: cámara, acelerómetro, posición del cuerpo  

**Propiedades del entorno:**  
- Totalmente observable (todas las variables relevantes son visibles)  
- Determinístico (el resultado depende de la técnica y la fuerza)  
- Secuencial (la carrera influye en el salto)  
- Estático (el entorno no cambia durante la ejecución)  
- Continuo (movimiento fluido)  
- Agente único

---

f) **Pujar por un artículo en una subasta**  
Performance: número de artículos ganados, monto pagado  
Environment: sala o plataforma de subasta  
Actuators: enviar, actualizar o retirar una puja  
Sensors: precio actual, historial de pujas, tiempo restante  

**Propiedades del entorno:**  
- Parcialmente observable (no se conocen las estrategias de los otros pujadores)  
- Estocástico (las ofertas de los demás son impredecibles)  
- Secuencial (cada acción depende del estado actual de la puja)  
- Dinámico (el precio y los participantes cambian durante la subasta)  
- Discreto (acciones en momentos puntuales)  
- Multiagente
