# Informe Semanal · Back-End | EnergiAI
> **Semana 3:** 3 de agosto – 9 de agosto de 2026  
> **Área:** Back-End · Java / Spring Boot  
> **Integrantes:** Alan Federico Cabrera · Leandro Moreno  
> **Estado:** 🟢 Completado  

Tercer informe semanal del área de Back-End (Java / Spring Boot). La semana más intensa del back-end: pruebas automáticas completas, cliente ML robusto con timeouts y mapeo de errores (400/502/503), DTO consolidado (4 obligatorios / 7 opcionales), Swagger corregido y contrato JSON V1.2 publicado. Cierre con merges PR #45, #46 y #47.

---

## 📌 Resumen de la Semana

Semana centrada en pruebas, integración con el servicio ML y pulido final. Se cerraron los merges PR #45, #46 y #47.

* **Pruebas Automáticas:** Se agregaron pruebas automáticas del controller, del cliente ML y del manejo de errores. 32 tests ejecutados, 0 fallos, build SUCCESS al cierre de la semana.
* **Cliente ML Robusto:** Se configuraron timeouts de conexión/lectura en el cliente HTTP (`RestClient`) y se refinó el mapeo de errores: `400 BAD_REQUEST`, `502 BAD_GATEWAY` y `503 SERVICE_UNAVAILABLE`.
* **DTO Consolidado y Contrato JSON V1.2:** DTO de entrada `DatosRegistroConsumo` consolidado con 4 campos obligatorios y 7 opcionales. Publicación del contrato JSON V1.2 alineando request/response con ejemplos para Swagger/OpenAPI.
* **Swagger / OpenAPI y Documentación:** Corrección de la documentación Swagger (campos opcionales vs. obligatorios, HTTP 502), enriquecimiento de descripciones `@Schema` y actualización del README con nuevas reglas de validación y ejemplos.

---

## 📊 Métricas de la Semana

| Métrica | Valor |
| :--- | :--- |
| **Pull Requests Propios** | 14 mergeados (entre 03/08 y 08/08) |
| **Commits Totales** | 27 (18 Alan · 9 Leandro) |
| **Tests Ejecutados** | 32 (0 fallos · Build SUCCESS) |
| **Contrato JSON** | V1.2 (Publicado y documentado) |

---

## 🔀 Pull Requests de la Semana

Se realizaron 14 Pull Requests propios durante la semana, además de 2 merges de PRs ajenos, entre el 03/08/2026 y el 08/08/2026.

| PR | Rama | Autor | Mergeado por | Descripción |
| :---: | :--- | :--- | :--- | :--- |
| **#26** | `feature/dto-validation` | Alan Cabrera | Leandro Moreno | Errores, Swagger y DTOs actualizados |
| **#27** | `feature/dto-validation` | Alan Cabrera | Alan Federico Cabrera | Pruebas automáticas, timeout, 503 y 404 |
| **#29** | `feature/dto-validation` | Alan Cabrera | Alan Federico Cabrera | Tests, fix de error y config FastAPI/Swagger |
| **#30** | `feature/dto-validation` | Alan Cabrera | Alan Federico Cabrera | Actualización en `consumo_kwh` |
| **#32** | `feature/dto-validation` | Alan Cabrera | Alan Federico Cabrera | Nuevas clases DTO, variables y properties |
| **#33** | `AlanFedericoCabrera-patch-1` | Alan Federico Cabrera | Alan Federico Cabrera | Add files via upload |
| **#35** | `feature/docs` | Leandro Moreno | Alan Federico Cabrera | Contrato JSON V1.2 |
| **#36** | `Leandro-tech687-patch-6` | Leandro Moreno | Alan Federico Cabrera | Revisión de ejemplos request/response y reglas de validación |
| **#37** | `feature/dto-validation` | Leandro Moreno | Alan Federico Cabrera | Orden visual del código y Swagger/OpenAPI |
| **#40** | `Leandro-tech687-patch-7` | Leandro Moreno | Alan Federico Cabrera | Update README con nuevas reglas y ejemplos |
| **#42** | `feature/dto-validation` | Alan Cabrera | Leandro Moreno | Actualización tests, nombres y service |
| **#45** | `feature/dto-validation` | Leandro Moreno | Leandro Moreno | Corrección manejo de errores y campos DTO |
| **#46** | `Leandro-tech687-patch-8` | Leandro Moreno | Leandro Moreno | DTO final consolidado |
| **#47** | `feature/dto-validation` | Leandro Moreno | Leandro Moreno | README, JSON V1.2, Swagger/OpenAPI y fix nota `ml-service` |

### Merges de PRs Ajenos

| PR | Rama | Mergeador | Descripción |
| :---: | :--- | :--- | :--- |
| **#43** | `chore/sync-main-into-develop` | Leandro Moreno | Sincronización de `main` → `develop` (incluye actualizaciones de Data Science/FastAPI, PR #39) |
| **#44** | `data` | Alan Federico Cabrera | Integración de Data Science/OCI Object Storage (trabajo de Nahuel Rosas) |

---

## 🛠️ Detalles de Implementación Técnicas

### 🛠️ PR #45 — Corrección de Manejo de Errores y Campos DTO
*Aporte de Leandro Moreno (mergeado 07/08/2026).*

#### Mapeo de Errores en `MlClient`

| Escenario | Excepción | Resultante HTTP |
| :--- | :--- | :---: |
| FastAPI responde 4xx (ej: 422) | `DatosEntradaInvalidosException` | `400 BAD_REQUEST` |
| FastAPI responde 5xx (ej: 503) | `ServicioMlNoDisponibleException` | `503 SERVICE_UNAVAILABLE` |
| Error de conexión o timeout | `ServicioMlNoDisponibleException` | `503 SERVICE_UNAVAILABLE` |
| Respuesta inesperada/inválida | `MlRespuestaInvalidaException` | `502 BAD_GATEWAY` |

#### DTO de Entrada — `DatosRegistroConsumo` (4 Obligatorios / 7 Opcionales)

| Campo | Tipo | Obligatorio | Validación |
| :--- | :--- | :---: | :--- |
| `consumo_kwh` | Double | ✅ Sí | `@NotNull`, min 1.0, máx 1000.0 |
| `cantidad_equipos` | Integer | ✅ Sí | `@NotNull`, min 1, máx 100 |
| `tipo_inmueble` | String (Enum) | ✅ Sí | `@NotNull` |
| `horas_alto_consumo` | Integer | ✅ Sí | `@NotNull`, min 0, máx 24 |
| `uso_horario_pico` | Boolean | ❌ No | Sin restricción |
| `metros_cuadrados` | Integer | ❌ No | min 26, máx 2000 |
| `antiguedad_vivienda` | Integer | ❌ No | min 0, máx 150 |
| `zona_fria` | Boolean | ❌ No | Sin restricción |
| `calidad_aislamiento` | String (Enum) | ❌ No | Sin restricción |
| `fuente_calefaccion` | String (Enum) | ❌ No | Sin restricción |
| `fuente_agua_caliente` | String (Enum) | ❌ No | Sin restricción |

---

## 👥 Resumen de Aportes Individuales

### Alan Cabrera (18 commits · PRs #26, #27, #29, #30, #32, #33, #42)
* Tests automáticos (`controller`, cliente ML y manejo de errores).
* Timeouts de conexión/lectura en `RestClient`.
* Mapeo de errores 400/502/503, validación 404.
* Nuevas clases DTO, variables y `properties`.
* Configuración FastAPI y Swagger.

### Leandro Moreno (9 commits · PRs #35, #36, #37, #40, #45, #46, #47 + merges #43, #44)
* Contrato JSON V1.2 publicado.
* Corrección de manejo de errores y campos DTO (PR #45).
* DTO final consolidado (PR #46).
* README, Swagger/OpenAPI y fix nota `ml-service` (PR #47).
* Revisión de ejemplos, reglas de validación y orden visual.

---

## 🧭 Estado Final de la Semana 3

1. **Pruebas Automáticas Completas:** Tests del `controller`, cliente ML y manejo de errores implementados. 32 tests ejecutados, 0 fallos, build SUCCESS.
2. **Cliente ML Robusto con Timeouts y Mapeo de Errores:** Timeouts de conexión/lectura configurados en `RestClient`. Mapeo completo: 400 (4xx FastAPI), 502 (respuesta inválida) y 503 (timeout / ML no disponible). Nuevas excepciones: `DatosEntradaInvalidosException` y `MlRespuestaInvalidaException`.
3. **Manejo Global de Errores Ampliado (404 Incluido):** `GlobalExceptionHandler` extendido con formato uniforme `DatosErrorRespuesta` y validación de ruta inexistente (HTTP 404).
4. **DTO Consolidado — 4 Obligatorios / 7 Opcionales:** DTO de entrada `DatosRegistroConsumo` estabilizado, documentado en `docs/backend/cambiosPR44.md` y reflejado correctamente en Swagger.
5. **Contrato JSON V1.2 y Swagger Corregido:** Contrato JSON V1.2 publicado (`API-Contract-JSON-V1.2.pdf`). Swagger corregido: campos obligatorios/opcionales, HTTP 502 documentado y descripciones `@Schema` enriquecidas (documentado en `cambiosPR49.md`).
