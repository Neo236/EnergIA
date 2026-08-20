# 🗓️ Informe Semanal – Back-End | EnergiAI

**Semana:** 2
**Período:** 27 de julio – 2 de agosto de 2026
**Integrantes:** Alan Federico Cabrera · Leandro Moreno
**Área:** Back-End (Java / Spring Boot)
**Estado:** 🟢 Completado

---

## 📌 Resumen

Semana n° 2: Se amplió el manejo global de excepciones (incluido el error http 503 del servicio de Machine Learning), se evolucionó el DTO de entrada con nuevas variables y catálogos de enums (V2.1), se incorporó el costo mensual a la respuesta, se publicó el contrato JSON V1.1 y se actualizó la documentación README con la versión de Spring Boot.

---

## 🔀 Pull Requests

### PR #13 – `feature/dto-validation`
- **Autores:** Leandro Moreno
- **Mergeado por:** Lautaro Sebastian Mambrin (30/07/2026)
- **Enlace:** [PR #13](https://github.com/No-Country-simulation/G9-LATAM-TEAM-09/pull/13)

- **"V2.1, Validaciones, JSON, Test." – Implementación del contrato JSON V1.1:**
  - **Campos del DTO de entrada renombrados a `snake_case`** en `DatosRegistroConsumo`:
    - `consumo` → `consumo_kwh`
    - `cantidadEquipos` → `cantidad_equipos`
    - `tipoInmueble` → `tipo_inmueble`
    - `horarioPico` → `uso_horario_pico`
    - `horasAltoConsumo` → `horas_alto_consumo`
    - Límite máximo de `cantidad_equipos` ajustado de 500 a 100.
    - Nueva validación `@Pattern` para `tipo_inmueble` (Casa, Departamento, Comercio, Pyme).
  - **`recomendaciones` pasa de `String` a `List<String>`** en el DTO de respuesta `DatosRegistroAnalisis`, con listas de recomendaciones por categoría (Eficiente, Moderado, Ineficiente) en `AnalisisEnergeticoService`.
  - **Reestructuración del código** (controller, DTOs y service) para mayor legibilidad y detección de errores, sin modificar su funcionalidad.
  - **Modificación parcial de los mensajes de respuesta** (ej.: error de JSON inválido → "El formato de la solicitud (JSON) es invalido o esta ausente").
  - **Pruebas manuales en Insomnia** (campos/datos inválidos, formato JSON inválido y entradas válidas Eficiente/Moderado/Ineficiente).
  - Actualización del mensaje de error en `GlobalExceptionHandlerTest.java`

**Clases involucradas:**
  - `AnalisisEnergeticoController.java`
  - `DatosErrorCampo.java`
  - `DatosErrorRespuesta.java`
  - `DatosRegistroAnalisis.java`
  - `DatosRegistroConsumo.java`
  - `GlobalExceptionHandler.java`
  - `AnalisisEnergeticoService.java`
  - `GlobalExceptionHandlerTest.java`

### PR #18 – `Leandro-tech687-patch-2`
- **Autor:** Leandro Moreno
- **Mergeado por:** Lautaro Sebastian Mambrin (30/07/2026)
- **Enlace:** [PR #18](https://github.com/No-Country-simulation/G9-LATAM-TEAM-09/pull/18)

**"Update Spring Boot version in README":**

- Actualización de la versión de Spring Boot (4.0.7) en el README principal del proyecto.

### PR #19 – `feature/dto-validation`
- **Autor:** Leandro Moreno
- **Mergeado por:** Lautaro Sebastian Mambrin (30/07/2026)
- **Enlace:** [PR #19](https://github.com/No-Country-simulation/G9-LATAM-TEAM-09/pull/19)

**"costo mensual":**

- Incorporación del campo `costo_estimado_mensual` en el DTO de respuesta `DatosRegistroAnalisis`, alineado con el cálculo financiero del MVP (`consumo_kwh × tarifa_kwh`).

### PR #20 – `Leandro-tech687-patch-3`
- **Autor:** Leandro Moreno
- **Mergeado por:** Lautaro Sebastian Mambrin (30/07/2026)
- **Enlace:** [PR #20](https://github.com/No-Country-simulation/G9-LATAM-TEAM-09/pull/20)

**"Contrato JSON V1.1":**

- Publicación de la **versión 1.1 del contrato JSON** de la API, alineando request/response con los DTOs del back-end (campos obligatorios/opcionales y catálogos de enums).

### PR #21 – `feature/dto-validation`
- **Autor:** Alan Cabrera
- **Mergeado por:** Lautaro Sebastian Mambrin (30/07/2026)
- **Enlace:** [PR #21](https://github.com/No-Country-simulation/G9-LATAM-TEAM-09/pull/21)

**"Agrege el error 503":**

- Manejo del escenario en el que el servicio de Machine Learning no está disponible:
  - Excepción `ServicioMlNoDisponibleException`.
  - Handler en `GlobalExceptionHandler` que responde **HTTP 503 SERVICE_UNAVAILABLE**.
  - Actualización del mensaje de error y del test correspondiente.

### PR #22 – `feature/docs-frontend`
- **Mergeado por:** Leandro Moreno (31/07/2026)
- **Enlace:** [PR #22](https://github.com/No-Country-simulation/G9-LATAM-TEAM-09/pull/22)

**Qué se hizo (rol de Leandro Moreno):**

- Integración del merge del PR correspondiente a la documentación del frontend (informes de participación de semanas 1, 2, anexos, y renombre de la propuesta técnica a obsoleta). Corresponde a un PR ajeno, integrado por Leandro Moreno.

### PR #24 – `Leandro-tech687-patch-4`
- **Autor:** Leandro Moreno
- **Mergeado por:** Lautaro Sebastian Mambrin (02/08/2026)
- **Enlace:** [PR #24](https://github.com/No-Country-simulation/G9-LATAM-TEAM-09/pull/24)

**"Update logo Spring Boot version in README":**

- Actualización del logo/badge de la versión de Spring Boot en el README.

### PR #25 – `Leandro-tech687-patch-5`
- **Autor:** Leandro Moreno
- **Mergeado por:** Lautaro Sebastian Mambrin (02/08/2026)
- **Enlace:** [PR #25](https://github.com/No-Country-simulation/G9-LATAM-TEAM-09/pull/25)

**"Update Spring Boot version in README doc Backend":**

- Actualización de la versión de Spring Boot (4.0.7) en `docs/backend/README.md`.

---

## 🔀 Merges de PRs ajenos

| PR | Rama | Mergeador | Descripción |
|----|------|-----------|-------------|
| [#22](https://github.com/No-Country-simulation/G9-LATAM-TEAM-09/pull/22) | `feature/docs-frontend` | Leandro Moreno | Documentación del frontend (informes semanas 1–2). |

---

## 👥 Commits de la semana

| Autor | Commits | Aportes principales |
|-------|:-------:|---------------------|
| Leandro Moreno | 7 | GlobalExceptionHandler, DTO, tests, contrato JSON V1.1 y READMEs de versión. |
| Leandro Moreno | 2 | V2.1 de validaciones/JSON y costo mensual. |
| Alan Cabrera | 1 | Manejo del error 503. |

---

## 🧭 Estado final de la semana 2

**Logrado:** manejo global de errores ampliado (503 incluido), DTOs con catálogos y nuevas variables, costo mensual en la respuesta, contrato JSON V1.1 y documentación README actualizada.
