# Adenda Sprint 3 — Contrato V1.2 y hallazgos de integración (09/08)

> 📎 **Anexo del [Informe Semana 3](../informe.md)** — actualización del contrato desde la óptica del frontend, y hallazgos de la verificación contra la API real.

Esta adenda sucede a la [Adenda Sprint 2](../../semana-2/anexos/adenda-sprint-2.md), que documentaba el contrato V1.1. No la reemplaza: registra lo que cambió y lo que se verificó.

**Versión:** 1.2-sprint3 · **Fecha:** 9 de agosto de 2026

---

## 1. Contrato V1.2 — 4 obligatorios + 7 opcionales

**Endpoint:** `POST /api/v1/analisis-energetico`

El front habla con la **API de Java**, no con el servicio de ML. Esta tabla es el espejo de `DatosRegistroConsumo`, y es la fuente única de `frontend/src/lib/contrato.ts`.

### Obligatorios (4)

| Campo | Tipo | Restricciones |
|---|---|---|
| `consumo_kwh` | decimal | 1 ≤ valor ≤ 1000 |
| `tipo_inmueble` | enum | Casa · Departamento · Comercio · Pyme |
| `cantidad_equipos` | entero | 1 ≤ valor ≤ 100 |
| `horas_alto_consumo` | entero | 0 ≤ valor ≤ 24 |

### Opcionales (7), con el valor por defecto que aplica el back-end

| Campo | Default | Rango / valores |
|---|---|---|
| `metros_cuadrados` | `1000` | 26–2000 |
| `antiguedad_vivienda` | `50` | 0–150 |
| `zona_fria` | `false` | booleano |
| `calidad_aislamiento` | `Media` | Muy Alta · Alta · Media · Baja · Muy Baja |
| `fuente_calefaccion` | `Electricidad` | Solar · Electricidad · Otros |
| `fuente_agua_caliente` | `Electricidad` | Solar · Electricidad · Otros |
| `uso_horario_pico` | `false` | booleano |

**Decisión de interfaz:** cada campo opcional muestra su valor por defecto en el propio control. Si el back-end va a enviar algo cuando el usuario no completa, el usuario tiene derecho a ver qué. El formulario arma el **payload mínimo**: manda los obligatorios y solo los opcionales que se tocaron.

**Salida 200** — sin cambios respecto a V1.1: `categoria`, `probabilidad`, `costo_estimado_mensual`, `recomendaciones`. Sigue **sin incluir identificador ni fecha** (PA-19), así que la fecha se deriva en el cliente y no existe forma de recuperar un análisis por enlace.

---

## 2. Hallazgos verificados

Cada hallazgo indica **contra qué commit se verificó**. No es formalidad: el código de los otros componentes cambió varias veces durante el sprint —Data Science reescribió el servicio de ML el 05/08—, así que sin esa referencia nadie puede saber si un hallazgo sigue vigente al momento de leerlo.

| # | Hallazgo | Verificado contra | Estado | Dueño |
|---|---|---|---|---|
| **F-01** | Integración Java↔ML rota: Java envía `uso_horario_pico` y `zona_fria` como booleanos, el ML exige los strings `"Si"`/`"No"` | `develop@72f68a0` (09/08) | 🔴 Abierto | Back / ML |
| **F-02** | Un enum inválido devuelve *"El formato de la solicitud (JSON) es invalido"*, sin `detalles[]` ni indicar el campo | `develop@72f68a0` (09/08) | 🟡 Abierto | Back |
| **F-03** | Healthcheck del contenedor del front contra `localhost` (resuelve a `::1`, nginx escucha IPv4) | `develop@742833b` (09/08) | ✅ Corregido | Front |
| **F-04** | `/favicon.ico` caía en el fallback del router y devolvía 200 con la aplicación entera | rama `feature/frontend-vite-react` (09/08) | ✅ Corregido | Front |
| **F-05** | El mock del front replicaba una fórmula de puntaje ya reescrita por Data Science | `develop@72f68a0` (09/08) | 🟡 Conocido | Front |
| **F-06** | ~~Mensajes de validación en inglés~~ | — | ❌ **Descartado** | — |

### F-01 — el que bloquea todo

Es el único que impide que la aplicación funcione punta a punta. Verificado pegándole directamente al servicio de ML, con una diferencia de una línea:

```
POST con "zona_fria": false   → HTTP 422 · Input should be 'Si' or 'No'
POST con "zona_fria": "No"    → HTTP 200 · {"categoria":"Eficiente", ...}
```

Java declara esos dos campos como `Boolean` y Jackson los serializa como `true`/`false`; el esquema Pydantic del ML los tipa como `Literal["Si","No"]`. **Ningún payload posible funciona hoy**: probado con los 4 obligatorios y también con los 11 campos completos, el resultado es el mismo.

Efecto visible en los dos ambientes: `POST /api/v1/analisis-energetico` devuelve **400** con el mensaje *"El servicio de Machine Learning rechazó los datos de entrada (HTTP 422)"*.

El front ya maneja ese error correctamente —lo muestra como aviso con el mensaje real disponible en un detalle técnico plegable—, pero la corrección corresponde a Back-End o a Data Science.

### F-06 — descartado

Había quedado registrado que los mensajes de validación llegaban en inglés (`"must not be null"`), pero eso solo ocurre con `curl`, que no envía cabecera `Accept-Language`. Desde el navegador Spring los localiza correctamente: llega **`"no debe ser nulo"`**. La decisión D6 sobre mensajes en español está más resuelta de lo que parecía.

---

## 3. Cosas del contrato que siguen abiertas

- **`tipo_inmueble` no influye en el resultado.** Verificado el 04/08 contra `develop@8514084`: no aparecía en la generación del dataset ni en el cálculo del puntaje. **Pendiente de re-verificar** — Data Science reescribió esa lógica el 05/08 y no volví a comprobarlo. Se anota como pregunta abierta, no como hecho.
- **Sin identificador en la respuesta (PA-19).** Mientras siga así, no hay enlaces compartibles ni pantalla «mis análisis». La ruta `/analisis/:id` existe en el front y siempre cae en «no encontrado», documentando el hueco en vez de esconderlo.
- **Región de OCI mal escrita.** ~~`santiago-chile-1` en `docker-compose.yml` y en la documentación; la región correcta es `sa-santiago-1`. No rompe hoy porque el storage local no la usa.~~ → **Corregido** en `fix/oci-region-identifiers`: `sa-santiago-1` en todos los archivos de configuración, código y documentación.

---

## 4. Alcance del frontend al cierre del Sprint 3

**Terminado:** P-01 y P-02 en móvil y escritorio, con los ocho estados. Pantalla de no encontrado. Despliegue continuo en los dos ambientes. Migración a Vite + React + TypeScript.

**Sigue en backlog:** P-03 simulador, P-04 mis análisis, P-05 datos agregados, enlace compartible (bloqueado por PA-19), y la identidad visual definitiva — la paleta actual es temporal y vive completa en `frontend/src/styles/tokens.css`.
