# 📝 Cambios Añadidos – Back-End

## 📌 Resumen

Refinamiento del manejo de errores en la comunicación con el servicio de Machine Learning y ajuste de los campos obligatorios/opcionales del DTO de entrada `DatosRegistroConsumo`.

---

## 🔀 Mapeo de errores en `MlClient`

**Antes:** cualquier excepción al llamar al servicio ML se traducía en `ServicioMlNoDisponibleException` (HTTP 503), sin distinguir el tipo de falla.

**Ahora:** se distingue el tipo de error para devolver el código HTTP correcto:

| Escenario | Excepción lanzada | HTTP resultante |
|-----------|-------------------|-----------------|
| FastAPI responde 4xx (ej: 422 de validación) | `DatosEntradaInvalidosException` | **400 Bad Request** |
| FastAPI responde 5xx (ej: 503 del ML) | `ServicioMlNoDisponibleException` | **503 Service Unavailable** |
| Error de conexión o timeout | `ServicioMlNoDisponibleException` | **503 Service Unavailable** |
| Respuesta inesperada o inválida (JSON no deserializable) | `MlRespuestaInvalidaException` | **502 Bad Gateway** |

Archivo modificado: `backend/analisis-energetico-api/src/main/java/com/energiai/client/MlClient.java`

---

## 🆕 Nuevas excepciones

| Excepción | Descripción | Ruta |
|-----------|-------------|------|
| `DatosEntradaInvalidosException` | El servicio ML rechazó los datos de entrada (respuesta 4xx). Extiende `RuntimeException` con constructores de mensaje y causa. | `src/main/java/com/energiai/exception/DatosEntradaInvalidosException.java` |
| `MlRespuestaInvalidaException` | El servicio ML devolvió una respuesta inesperada o inválida. Extiende `RuntimeException` con constructores de mensaje y causa. | `src/main/java/com/energiai/exception/MlRespuestaInvalidaException.java` |

---

## 🛡️ `GlobalExceptionHandler`

Se agregaron dos nuevos `@ExceptionHandler` con formato de respuesta uniforme (`DatosErrorRespuesta`):

- `manejarDatosEntradaInvalidos` → HTTP **400** `BAD_REQUEST`
- `manejarMlRespuestaInvalida` → HTTP **502** `BAD_GATEWAY`

Archivo modificado: `backend/analisis-energetico-api/src/main/java/com/energiai/exception/GlobalExceptionHandler.java`

---

## 📋 DTO `DatosRegistroConsumo`

Cambios de validación:

- Añadido `@JsonInclude(JsonInclude.Include.NON_NULL)` a nivel de record.
- **Nuevos obligatorios** (`@NotNull`): `cantidad_equipos`, `horas_alto_consumo`.
- **Ahora opcionales** (se quitó `@NotNull`): `uso_horario_pico`, `zona_fria`, `fuente_calefaccion`, `fuente_agua_caliente`.

### Campos del DTO

| Campo | Tipo | Obligatorio | Validación |
|-------|------|-------------|------------|
| `consumo_kwh` | `Double` | ✅ Sí | `@NotNull`, min 1.0, máx 1000.0 |
| `cantidad_equipos` | `Integer` | ✅ Sí | `@NotNull`, min 1, máx 100 |
| `tipo_inmueble` | `TipoInmueble` | ✅ Sí | `@NotNull` |
| `uso_horario_pico` | `Boolean` | ❌ No | Sin restricción |
| `horas_alto_consumo` | `Integer` | ✅ Sí | `@NotNull`, min 0, máx 24 |
| `metros_cuadrados` | `Integer` | ❌ No | min 26, máx 2000 |
| `antiguedad_vivienda` | `Integer` | ❌ No | min 0, máx 150 |
| `zona_fria` | `Boolean` | ❌ No | Sin restricción |
| `calidad_aislamiento` | `CalidadAislamiento` | ❌ No | Sin restricción |
| `fuente_calefaccion` | `FuenteEnergia` | ❌ No | Sin restricción |
| `fuente_agua_caliente` | `FuenteEnergia` | ❌ No | Sin restricción |

> 📌 **Total: 4 campos obligatorios y 7 opcionales.**

### Ejemplo de JSON mínimo válido (solo los obligatorios)

```json
{
  "consumo_kwh": 450.5,
  "cantidad_equipos": 8,
  "tipo_inmueble": "Casa",
  "horas_alto_consumo": 6
}
```

Archivo modificado: `backend/analisis-energetico-api/src/main/java/com/energiai/dto/DatosRegistroConsumo.java`

---

## ⚙️ Configuración

En `backend/analisis-energetico-api/src/main/resources/application.properties`:

- URL por defecto del servicio ML: `http://localhost:5000/predict` → **`http://localhost:8000`**

---

## 🧪 Tests añadidos / actualizados

| Archivo | Cambio |
|---------|--------|
| `src/test/java/com/energiai/client/MlClientTest.java` | **Nuevo.** 4 casos: FastAPI 422 → 400, FastAPI 503 → 503, body inválido → 502, error de conexión → 503. |
| `src/test/java/com/energiai/controller/AnalisisEnergeticoControllerTest.java` | Añade casos: `DatosEntradaInvalidosException` → 400 y `MlRespuestaInvalidaException` → 502. |
| `src/test/java/com/energiai/dto/DatosRegistroConsumoCamposTest.java` | Ajusta conteo de violaciones de 6 → 4 y el test de campos opcionales nulos. |
| `src/test/java/com/energiai/exception/GlobalExceptionHandlerTest.java` | Añade casos: handler de datos de entrada inválidos → 400 y de respuesta ML inválida → 502. |
