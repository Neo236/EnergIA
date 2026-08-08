# 📝 Cambios de Documentación – Back-End (Swagger / OpenAPI)

## 📌 Resumen

Corrección de la documentación Swagger/OpenAPI del endpoint `POST /api/v1/analisis-energetico`. **Sin cambios de comportamiento**: la lógica, validaciones y respuestas HTTP no se modificaron; solo se ajustó la descripción que ve el consumidor de la API en Swagger UI.

---

## 🔧 1. Campos obligatorios en Swagger

Los campos `cantidad_equipos` y `horas_alto_consumo` son **obligatorios** (`@NotNull`), pero su descripción en `@Schema` decía *"Es un dato opcional."*, contradiciendo la validación. Se eliminó el texto para reflejar la realidad.

| Campo | Descripción antes | Descripción después | Rango | Validación | ¿Obligatorio? |
|-------|-------------------|---------------------|-------|------------|---------------|
| `cantidad_equipos` | "Cantidad de equipos activos. Es un dato opcional." | "Cantidad de equipos activos." | min 1, máx 100 | `@NotNull` | ✅ Sí |
| `horas_alto_consumo` | "Horas estimadas de uso de equipos de alto consumo al dia. Es un dato opcional." | "Horas estimadas de uso de equipos de alto consumo al dia." | min 0, máx 24 | `@NotNull` | ✅ Sí |

> 📌 Todos los campos opcionales (sin `@NotNull`) llevan el texto *"Es un dato opcional."*: `metros_cuadrados`, `antiguedad_vivienda`, `uso_horario_pico`, `zona_fria`, `calidad_aislamiento`, `fuente_calefaccion`, `fuente_agua_caliente`. Los valores admitidos detallados en sus descripciones se documentan en la sección 5.

### Estado actual del DTO de entrada

| Campo | Tipo | Obligatorio | Rango | Validación |
|-------|------|-------------|-------|------------|
| `consumo_kwh` | `Double` | ✅ | min 1.0, máx 1000.0 | `@NotNull` |
| `cantidad_equipos` | `Integer` | ✅ | min 1, máx 100 | `@NotNull` |
| `tipo_inmueble` | `TipoInmueble` | ✅ | Casa, Departamento, Comercio, Pyme | `@NotNull` |
| `uso_horario_pico` | `Boolean` | ❌ | true o false | Sin restricción |
| `horas_alto_consumo` | `Integer` | ✅ | min 0, máx 24 | `@NotNull` |
| `metros_cuadrados` | `Integer` | ❌ | min 26, máx 2000 | Sin restricción |
| `antiguedad_vivienda` | `Integer` | ❌ | min 0, máx 150 | Sin restricción |
| `zona_fria` | `Boolean` | ❌ | true o false | Sin restricción |
| `calidad_aislamiento` | `CalidadAislamiento` | ❌ | Muy alto, Alto, Medio, Bajo, Muy bajo | Sin restricción |
| `fuente_calefaccion` | `FuenteEnergia` | ❌ | Solar, Electricidad, Otros | Sin restricción |
| `fuente_agua_caliente` | `FuenteEnergia` | ❌ | Solar, Electricidad, Otros | Sin restricción |

> 📌 **Total: 4 campos obligatorios y 7 opcionales.**

Archivo modificado: `backend/analisis-energetico-api/src/main/java/com/energiai/dto/DatosRegistroConsumo.java`

---

## 🧾 2. Descripción del endpoint (eliminación de "provisional")

Se eliminó la palabra *"provisional"* de la descripción del `@Operation` del endpoint, ya que la clasificación es provista por el servicio de Machine Learning y no es un resultado provisional por umbrales.

| Aspecto | Antes | Después |
|---------|-------|---------|
| `summary` | "Realizar analisis de consumo energetico" | "Realizar analisis de consumo energetico" (sin cambio) |
| `description` | "Evalua los datos de consumo de un inmueble y devuelve la clasificacion **provisional**, costos estimados y recomendaciones." | "Evalua los datos de consumo de un inmueble y devuelve la clasificacion, costos estimados y recomendaciones." |

Archivo modificado: `backend/analisis-energetico-api/src/main/java/com/energiai/controller/AnalisisEnergeticoController.java`

---

## ⚠️ 3. Ejemplo HTTP 400 actualizado

El ejemplo de la respuesta 400 en Swagger mostraba a `fuente_calefaccion` como campo faltante con mensaje *"La fuente de energia para calefaccion es obligatoria"*. Ese campo **no** tiene `@NotNull` en el DTO, por lo que el ejemplo era incorrecto.

Ahora el ejemplo refleja un caso real: un cuerpo sin `cantidad_equipos` y `horas_alto_consumo`, con los mensajes reales generados por Bean Validation (`no debe ser nulo`).

| Campo del error | Mensaje antes | Mensaje después |
|-----------------|---------------|-----------------|
| `fuente_calefaccion` | "La fuente de energia para calefaccion es obligatoria" | *(eliminado)* |
| `cantidad_equipos` | *(no aparecía)* | `no debe ser nulo` |
| `horas_alto_consumo` | *(no aparecía)* | `no debe ser nulo` |

### Ejemplo JSON documentado en Swagger

```json
{
  "timestamp": "2026-08-01T16:45:00",
  "status": 400,
  "error": "BAD_REQUEST",
  "mensaje": "Errores de validacion en los datos de entrada",
  "detalles": [
    { "campo": "cantidad_equipos",
        "mensaje": "no debe ser nulo" },
    { "campo": "horas_alto_consumo",
        "mensaje": "no debe ser nulo" }
  ]
}
```

Archivo modificado: `backend/analisis-energetico-api/src/main/java/com/energiai/controller/AnalisisEnergeticoController.java`

---

## 🌐 4. Nueva documentación HTTP 502

El código **ya devolvía** HTTP 502 (BAD_GATEWAY) cuando el servicio de ML respondía con un JSON inesperado o inválido, pero faltaba documentarlo en Swagger. Se agregó el `@ApiResponse` correspondiente.

| Código | Error | Descripción en Swagger | Mapeo en código |
|--------|-------|-------------------------|-----------------|
| 502 | `BAD_GATEWAY` | "El servicio de Machine Learning devolvió una respuesta inesperada o inválida." | `MlRespuestaInvalidaException` → `GlobalExceptionHandler.manejarMlRespuestaInvalida` |

### Ejemplo JSON documentado en Swagger

```json
{
  "timestamp": "2026-08-01T16:45:00",
  "status": 502,
  "error": "BAD_GATEWAY",
  "mensaje": "El servicio de Machine Learning devolvió una respuesta inesperada o inválida"
}
```

### Códigos HTTP documentados en el endpoint

| Código | Descripción |
|--------|-------------|
| 200 | Análisis realizado exitosamente. |
| 400 | Datos de entrada inválidos o formato JSON incorrecto. |
| 404 | El recurso solicitado o la ruta no fueron encontrados. |
| 500 | Error interno del servidor. |
| 502 | El servicio de Machine Learning devolvió una respuesta inesperada o inválida. *(nuevo)* |
| 503 | El servicio de Machine Learning no se encuentra disponible. |

Archivo modificado: `backend/analisis-energetico-api/src/main/java/com/energiai/controller/AnalisisEnergeticoController.java`

---

## ✏️ 5. Descripciones de `@Schema` de los campos opcionales actualizadas

Se enriquecieron las descripciones de los campos opcionales en `DatosRegistroConsumo` para indicar que son datos opcionales y, en los campos de tipo enumerado, listar los valores admitidos. **Sin cambios de comportamiento.**

| Campo | Descripción antes | Descripción después |
|-------|-------------------|---------------------|
| `uso_horario_pico` | "Indica si la medicion incluye franja de horario pico (18hs a 23hs)" | "Indica si la medicion incluye franja de horario pico (18hs a 23hs). Es un dato opcional." |
| `zona_fria` | "Indica si la vivienda se encuentra ubicada en una zona climatica considerada fria." | "Indica si la vivienda se encuentra ubicada en una zona climatica considerada fria. Es un dato opcional." |
| `calidad_aislamiento` | "Nivel de eficiencia del aislamiento térmico. Es un dato opcional." | "Nivel de eficiencia del aislamiento térmico. Tipo de aislamiento (Muy alta, Alta, Medio, Baja, Muy baja). Es un dato opcional." |
| `fuente_calefaccion` | "Fuente principal de energia utilizada para la calefaccion." | "Fuente principal de energia utilizada para la calefaccion. Fuente de calefacción (Solar, Electricidad, Otros). Es un dato opcional." |
| `fuente_agua_caliente` | "Fuente de energia uitlizada para la produccion de agua caliente sanitaria." | "Fuente de energia uitlizada para la produccion de agua caliente sanitaria. Fuente de agua caliente (Solar, Electricidad, Otros). Es un dato opcional." |

Archivo modificado: `backend/analisis-energetico-api/src/main/java/com/energiai/dto/DatosRegistroConsumo.java`

---

## 📁 Archivos modificados

| Archivo | Cambios |
|---------|---------|
| `backend/analisis-energetico-api/src/main/java/com/energiai/dto/DatosRegistroConsumo.java` | Se quita "Es un dato opcional." en `cantidad_equipos` y `horas_alto_consumo`; se agrega en `uso_horario_pico`, `zona_fria`, `fuente_calefaccion` y `fuente_agua_caliente`; se detallan los valores admitidos en `calidad_aislamiento`, `fuente_calefaccion` y `fuente_agua_caliente`. |
| `backend/analisis-energetico-api/src/main/java/com/energiai/controller/AnalisisEnergeticoController.java` | Descripción del `@Operation` sin "provisional"; ejemplo 400 actualizado; nuevo `@ApiResponse` 502. |

---

## 🧪 Verificación

No se requirieron cambios de lógica ni de tests. Suite completa ejecutada con `.\mvnw.cmd test`:

| Resultado | Valor |
|-----------|-------|
| Tests ejecutados | 32 |
| Fallos | 0 |
| Errores | 0 |
| Build | **SUCCESS** |
