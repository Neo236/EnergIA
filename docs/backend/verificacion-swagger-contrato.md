# Verificación Swagger ↔ Contrato 4+7

> Evidencia de la confirmación de coincidencia entre el OpenAPI servido por el backend
> (`/v3/api-docs`, que es lo que renderiza Swagger UI) y el contrato de datos V1.2/V2
> (4 campos obligatorios + 7 opcionales).

## Registro de la prueba

| Campo | Valor |
|---|---|
| **Ambiente** | Local — Docker Compose (`docker compose up -d --build backend`), imágenes `energiai-backend:latest` y `energiai-ml-service:latest` |
| **Fecha** | 2026-08-21 (04:49 UTC-3 aprox., según `fecha` de las respuestas) |
| **SHA probado** | `86c93ddc720d478b296389d28a80b4a1528219db` (`86c93dd` — "Colección Insomnia y Postman") |
| **URL base** | `http://localhost:8080` |
| **Evidencia cruda** | [`assets/api-docs-SHA-86c93dd.json`](./assets/api-docs-SHA-86c93dd.json) — export íntegro de `/v3/api-docs` contra ese SHA |

## Fuentes cruzadas

1. **OpenAPI real**: `GET /v3/api-docs` (springdoc-openapi-starter-webmvc-ui) → guardado en `assets/`.
2. **Código**: `backend/analisis-energetico-api/src/main/java/com/energiai/dto/DatosRegistroConsumo.java` (request) y `DatosRegistroAnalisis.java` (response).
3. **Contrato documentado**: tabla V1.2 en `docs/frontend/semanas/semana-3/anexos/adenda-sprint-3.md` y `API-Contract-JSON-V1.2.pdf`.
4. **Fuente única del front**: `frontend/src/lib/contrato.ts` (V2).

## Resultado — Request `DatosRegistroConsumo`

**Coincide ✅** — 11 propiedades, `required` = exactamente los 4 obligatorios.

### Obligatorios (4)

| Campo | Contrato V1.2 | api-docs | ¿OK? |
|---|---|---|---|
| `consumo_kwh` | decimal, 1–1000 | number, min=1.0 max=1000.0, required | ✅ |
| `tipo_inmueble` | Casa · Departamento · Comercio · Pyme | enum idéntico, required | ✅ |
| `cantidad_equipos` | entero, 1–100 | integer, min=1 max=100, required | ✅ |
| `horas_alto_consumo` | entero, 0–24 | integer, min=0 max=24, required | ✅ |

### Opcionales (7)

| Campo | Contrato V1.2 | api-docs | ¿OK? |
|---|---|---|---|
| `metros_cuadrados` | 26–2000 | integer, min=26 max=2000, no required | ✅ |
| `antiguedad_vivienda` | 0–150 | integer, min=0 max=150, no required | ✅ |
| `zona_fria` | booleano | boolean, no required | ✅ |
| `calidad_aislamiento` | Muy Alta · Alta · Media · Baja · Muy Baja | enum idéntico, no required | ✅ |
| `fuente_calefaccion` | Solar · Electricidad · Otros | enum idéntico, no required | ✅ |
| `fuente_agua_caliente` | Solar · Electricidad · Otros | enum idéntico, no required | ✅ |
| `uso_horario_pico` | booleano | boolean, no required | ✅ |

## Resultado — Response `DatosRegistroAnalisis`

**Coincide ✅** con `contrato.ts` (V2): `id` (string), `fecha` (string), `categoria` (enum Eficiente/Moderado/Ineficiente), `probabilidad` (number, min=0.0 max=1.0), `costo_estimado_mensual` (number), `recomendaciones` (array).

## Resultado — Códigos HTTP documentados vs. probados en vivo

| Código | Documentado en Swagger | Probado en vivo | Resultado |
|---|---|---|---|
| 200 | POST y GET | POST con los 4 obligatorios | ✅ `{"id":"01a022a6-e160-…","fecha":"2026-08-21T04:49:17","categoria":"Moderado","probabilidad":0.61,…}` |
| 400 | POST (validación / JSON malformado) | falta `consumo_kwh`; `consumo_kwh=1500`; enum inválido | ✅ `error:"BAD_REQUEST"` con `detalles[]` en validaciones; sin `detalles` en enum inválido (ver hallazgo H-2) |
| 404 | GET con id inexistente | GET `/00000000-0000-7000-8000-000000000000` | ✅ `error:"NOT_FOUND"` |
| 500 | POST y GET | No provocado (no forma parte del alcance 4+7) | ℹ️ solo documentación |
| 502 | POST (ML responde inválido) | Cubierto por colección Postman (setup manual con proxy) | ℹ️ ver README Postman |
| 503 | POST (ML caído) | Cubierto por colección Postman (`docker stop ml-service`) | ℹ️ ver README Postman |

El body de error coincide con `DatosErrorRespuesta`: `timestamp`, `status`, `error`, `mensaje`, `detalles`.

## Cruce con la colección Postman

Las aserciones automáticas de `docs/backend/postman/EnergiAI.postman_collection.json` cubren los códigos **200, 400, 404, 422, 502, 503** y validan exactamente las propiedades de estos esquemas (`id`, `fecha`, `categoria`, `probabilidad`, `costo_estimado_mensual`, `recomendaciones`, y en errores `timestamp/status/error/mensaje/detalles`). **Sin desviaciones.**

## Hallazgos de esta verificación

| # | Hallazgo | Estado |
|---|---|---|
| H-1 | El README raíz (línea ~177) dice que "el DTO utiliza @NotNull en los 11 campos". **Está desactualizado**: el código actual tiene `@NotNull` solo en los 4 obligatorios, `api-docs` los lista como únicos `required`, y un POST con solo los 4 devuelve 200. Corregir esa nota. | 🔴 Doc a corregir |
| H-2 | Enum inválido (`tipo_inmueble="CasaEstilo"`) responde 400 genérico *"El formato de la solicitud (JSON) es invalido…"* sin `detalles[]` ni campo afectado. Coincide con el hallazgo F-02 de la adenda Sprint 3: sigue vigente. | 🟡 Conocido |
| H-3 | La adenda Sprint 3 afirma que la salida 200 "no incluye identificador ni fecha" (contrato V1.2). La API actual sí devuelve `id` + `fecha` — evolución ya registrada por `contrato.ts` como V2. El PDF `API-Contract-JSON-V1.2.pdf` quedó una versión atrás del código. | 🟡 Doc a actualizar |

## Conclusión

**Swagger coincide con el contrato 4+7.** Los 4 obligatorios y los 7 opcionales, sus tipos, rangos y enums, el schema de respuesta y los códigos HTTP documentados son idénticos a lo que sirve `/v3/api-docs` y a lo que responde la API en vivo, contra el SHA `86c93dd`.
