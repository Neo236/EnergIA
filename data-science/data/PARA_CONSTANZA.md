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
significa "qué tan seguro está el modelo de su respuesta".

| Probabilidad | Cómo interpretarlo en español |
|---|---|
| 0.95 – 1.00 | "Estoy muy seguro. Casi con certeza este hogar es Eficiente." |
| 0.80 – 0.95 | "Bastante seguro. Probablemente acierte, pero podría sorprenderse." |
| 0.60 – 0.80 | "Más probable que no, pero hay dudas reales. Conviene revisar." |
| < 0.60 | "Es un caso borderline — el modelo no se anima a definirse." |

**En la práctica**: si la probabilidad es alta (>0.85), podés tomar
la predicción casi como un hecho. Si es media (0.60–0.80), usala
como una pista, no como veredicto.

---

## 3. Limitaciones — lo que el modelo NO hace

Para ser honestos: el modelo no es perfecto. Tiene tres limitaciones
que hay que tener presentes antes de tomar decisiones con él:

### a) A veces se confunde con los hogares ineficientes

De cada 10 hogares que **realmente** son ineficientes, el modelo
detectará correctamente solo ~4-5. Los otros los va a marcar como
"Moderado". Es su punto débil.

**Qué hacer**: si el modelo dice "Moderado" y vos tenés la sospecha
de que ese hogar es Ineficiente (por ejemplo, factura altísima),
**no le creas al modelo sin revisarlo**.

### b) Aprendió de datos sintéticos (no de hogares reales)

El modelo fue entrenado sobre 2000 hogares **generados por una
simulación** que replica los patrones típicos de consumo
energético de Argentina. NO aprendió de facturas reales.

Implicación: las tendencias son correctas (alto consumo +
mal aislamiento = Ineficiente), pero los casos raros del mundo
real pueden no estar bien representados.

### c) No considera todo lo que afecta el consumo

El modelo mira 11 variables (consumo, metros cuadrados, antigüedad,
aislamiento, fuentes de energía, etc.). NO mira:

- Hábitos puntuales (por ejemplo, si el mes pasado hubo una fiesta
  y eso disparó el consumo).
- Cambios recientes (mudanza, nuevo electrodoméstico).
- Calidad real de las instalaciones eléctricas.
- Tarifa específica que paga el hogar.

**Qué hacer**: si la predicción no coincide con lo que esperás,
preguntale al usuario qué pasó ese mes. La predicción es un mapa,
no un satélite.

---

## 4. Cuando NO usar el modelo

- ❌ Para **cortar el servicio** o tomar acciones punitivas.
- ❌ Como **única fuente** de verdad en una disputa con el usuario.
- ❌ Para hogares con datos muy incompletos (muchos campos vacíos
  → la predicción usa defaults y pierde precisión).
- ❌ Para decisiones regulatorias o legales.

## 5. Cuando SÍ usarlo

- ✅ Para **orientar** al usuario sobre dónde puede ahorrar.
- ✅ Como **alerta temprana** en una flota grande de hogares
  (mejor detectar 4 de cada 10 ineficientes que no detectar ninguno).
- ✅ Para **priorizar** auditorías o visitas técnicas.
- ✅ Como punto de partida en una conversación con el usuario:
  "según nuestros datos, tu hogar es Moderado — ¿querés ver qué
  podés mejorar?"

---

## 6. Resumen en una frase

**"El modelo te dice a qué categoría parece pertenecer un hogar
según sus datos, con un nivel de confianza. Sirve para orientar,
no para sentenciar. Si dice Ineficiente, casi seguro acierta.
Si dice Moderado, no descarta que sea Ineficiente."**

---

## 7. Glosario mínimo

| Término técnico | En español |
|---|---|
| Modelo | El "cerebro" artificial que mira los datos y decide |
| Categoría | Eficiente / Moderado / Ineficiente |
| Probabilidad | Qué tan seguro está de su respuesta (0 a 1) |
| Features | Las 11 variables que el modelo mira del hogar |
| Accuracy | De cada 100 predicciones, ~81 son correctas |
| Recall (Ineficiente) | De cada 10 hogares ineficientes reales, detecta ~4-5 |
| F1 | Número que combina precision y recall (más alto = mejor) |

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
