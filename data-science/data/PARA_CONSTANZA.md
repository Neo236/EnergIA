# Para Constanza — Cómo leer una predicción del modelo EnergiAI

> Explicación en lenguaje simple, sin jerga técnica, para quien no
> trabaja con machine learning. Si después de leer esto algo no queda
> claro, podemos sentarnos y mirarlo juntos con un caso real.

---

## 1. Qué hace el modelo

El modelo mira los datos de un hogar (consumo de luz, tipo de casa,
aislamiento, calefacción, etc.) y dice **a cuál de tres categorías
energéticas pertenece**:

- 🟢 **Eficiente**: el hogar usa la energía de manera inteligente.
  No hay mucho para mejorar.
- 🟡 **Moderado**: el hogar está en el medio. Tiene cosas que podría
  optimizar, pero no está mal.
- 🔴 **Ineficiente**: el hogar gasta más energía de la que debería.
  Probablemente hay ahorros importantes esperándolo.

Es como un médico que ve tu resumen clínico y te dice "estás sano",
"deberías cuidarte más" o "necesitamos trabajar en esto".

---

## 2. Qué significa el número "probabilidad"

Cuando el modelo responde, además de la categoría te da un número
entre 0 y 1, por ejemplo `0.94`. Eso se llama **probabilidad** y
representa el porcentaje de árboles del bosque aleatorio que
votaron por esa categoría.

**Pero ojo: no está calibrada formalmente.** Esto significa que
"0.94" no es lo mismo que "hay un 94% de chances de que sea X". Es
más bien un indicador de cuánta evidencia interna encontró el modelo
a favor de esa categoría. Para una calibración real habría que
aplicar Platt scaling o isotonic regression y luego medir con
diagrams de reliability — eso no se hizo en este modelo.

En la práctica, usalo así:

| Probabilidad | Cómo interpretarlo en español |
|---|---|
| 0.95 – 1.00 | "El modelo encontró evidencia muy fuerte. Probablemente acierte." |
| 0.80 – 0.95 | "Hay bastante evidencia. Vale la pena confiar, pero no descartar nada." |
| 0.60 – 0.80 | "Es lo más probable según el modelo, pero hay dudas reales." |
| < 0.60 | "Es un caso borderline. No tomes decisiones importantes solo con esto." |

**En la práctica**: una probabilidad alta (>0.85) sugiere que el
modelo encontró evidencia consistente, pero **no garantiza** que la
predicción sea correcta. Siempre conviene cruzar con la métrica de
precision de esa clase específica (ver METRICS.md). Por ejemplo, para
`Ineficiente` la precision es 0.90, así que cuando el modelo dice
"Ineficiente" con probabilidad alta, hay ~90% de chances de que sea
correcto.

---

## 3. Limitaciones — lo que el modelo NO hace

Para ser honestos: el modelo no es perfecto. Tiene varias limitaciones
que hay que tener presentes antes de tomar decisiones con él.

### a) Recall bajo en hogares Ineficientes

De cada 10 hogares que **realmente** son ineficientes, el modelo
detectará correctamente solo ~4-5. Los otros los va a marcar como
"Moderado". Esto es por dos razones combinadas:
- El dataset de entrenamiento tiene 2/3 de hogares Moderados y solo
  ~16% Ineficientes — el modelo aprende que "Moderado" es la respuesta
  más probable.
- La métrica F1 de Ineficiente (0.60) es la más baja de las tres
  clases.

**Qué hacer**: si el modelo dice "Moderado" y vos tenés la sospecha
de que ese hogar es Ineficiente (por ejemplo, factura altísima o
reclamo del usuario), **no le creas al modelo sin revisarlo**.

### b) Aprendió de datos sintéticos, no de hogares reales

El modelo fue entrenado sobre 2000 hogares **generados por una
simulación** que replica los patrones típicos de consumo energético
de Argentina. NO aprendió de facturas reales de clientes.

**Esto es importante.** Las tendencias generales son razonables (alto
consumo + mal aislamiento = Ineficiente), pero:
- Los casos raros del mundo real pueden no estar bien representados.
- Patrones regionales, estacionales o económicos específicos no están
  capturados.
- Si el usuario tiene un comportamiento atípico (ej: trabaja desde
  casa, familia numerosa), el modelo puede equivocarse más de lo
  habitual.

**Qué hacer**: tratá la predicción como una hipótesis inicial, no
como un veredicto. Si los datos del usuario no encajan con el
"patrón típico argentino", la confianza en la predicción debería
bajar.

### c) No considera todo lo que afecta el consumo

El modelo mira 11 variables (consumo, metros cuadrados, antigüedad,
aislamiento, fuentes de energía, etc.). NO mira:

- Hábitos puntuales (por ejemplo, si el mes pasado hubo una fiesta
  y eso disparó el consumo).
- Cambios recientes (mudanza, nuevo electrodoméstico).
- Calidad real de las instalaciones eléctricas.
- Tarifa específica que paga el hogar.
- Ubicación geográfica precisa (solo zona fría sí/no).

**Qué hacer**: si la predicción no coincide con lo que esperás,
preguntale al usuario qué pasó ese mes. La predicción es un mapa,
no un satélite.

### d) La precision/recall se midió sobre el mismo tipo de dataset

Las métricas de accuracy (0.81), F1, etc. se midieron sobre los 400
hogares de test del dataset sintético. Esas métricas describen qué
tan bien le va al modelo **en datos similares a los de
entrenamiento**. En datos muy diferentes (ej: usuarios reales con
patrones no simulados), el desempeño puede ser peor.

---

## 4. Cuando NO usar el modelo

- ❌ Para **cortar el servicio** o tomar acciones punitivas.
- ❌ Como **única fuente** de verdad en una disputa con el usuario.
- ❌ Para hogares con datos muy incompletos (muchos campos vacíos
  → la predicción usa defaults y pierde precisión).
- ❌ Para decisiones regulatorias o legales.
- ❌ Para extrapolar más allá de los patrones del dataset sintético
  (ej: predecir consumo futuro, comparar entre ciudades).

## 5. Cuando SÍ usarlo

- ✅ Como **punto de partida** en una conversación con el usuario:
  "según nuestros datos, tu hogar es Moderado — ¿querés ver qué
  podés mejorar?"
- ✅ Para **orientar** al usuario sobre dónde puede ahorrar.
- ✅ Como **alerta temprana** en una flota grande de hogares
  (mejor detectar 4-5 de cada 10 ineficientes que no detectar
  ninguno).
- ✅ Para **priorizar** auditorías o visitas técnicas, entendiendo
  que se va a escapar ~la mitad de los ineficientes.

---

## 6. Resumen en una frase

**"El modelo te dice a qué categoría parece pertenecer un hogar
según sus datos, con un nivel de confianza. Sirve para orientar,
no para sentenciar. Aprendió de casos típicos simulados, no de
casos reales. Si dice Ineficiente, es bastante confiable. Si dice
Moderado, no descarta que sea Ineficiente."**

---

## 7. Glosario mínimo

| Término técnico | En español |
|---|---|
| Modelo | El "cerebro" artificial que mira los datos y decide |
| Categoría | Eficiente / Moderado / Ineficiente |
| Probabilidad | Cuánta evidencia encontró el modelo a favor de esa respuesta (no es un porcentaje calibrado) |
| Features | Las 11 variables que el modelo mira del hogar |
| Accuracy | De cada 100 predicciones, ~81 son correctas |
| Recall (Ineficiente) | De cada 10 hogares ineficientes reales, detecta ~4-5 |
| F1 | Número que combina precision y recall (más alto = mejor) |
| Calibración | Ajuste para que la probabilidad refleje chances reales — no se hizo en este modelo |

---

## 8. Si te queda una duda

Cualquiera de estas preguntas es bienvenida:
- "¿Por qué a este hogar le dijo Moderado y no Ineficiente?"
- "¿Cómo le explico al usuario su resultado?"
- "¿Puedo confiar en esta predicción para X decisión?"

Las predicciones individuales se pueden inspeccionar abriendo
`/tmp/ml-evidence/EVIDENCIA.md` (ejemplos completos con requests
y responses reales) o haciendo `curl localhost:8000/model-info`
en el servicio en producción.