# Adenda Sprint 2 — Alcance recortado y contrato V1.1 (30/07)

> 📎 **Anexo del [Informe Semana 2](../informe.md)** — actualización formal de la Etapa 3 (wireframes y descriptivo funcional). **Estado:** pendiente de aprobación de Backend y PM.

Esta adenda actualiza la Etapa 3 tras la re-auditoría del PM (28/07) y el merge de las validaciones del Back-End ([PR #13](https://github.com/No-Country-simulation/G9-LATAM-TEAM-09/pull/13), rama `develop`, 30/07). No reemplaza el documento madre: acota su alcance para el Sprint 2 y corrige los supuestos que el contrato real resolvió.

**Versión:** 1.1-sprint2 · **Fecha:** 30 de julio de 2026 · **Revisión:** 31/07 — incorpora los PRs [#18](https://github.com/No-Country-simulation/G9-LATAM-TEAM-09/pull/18) a [#21](https://github.com/No-Country-simulation/G9-LATAM-TEAM-09/pull/21), posteriores a la Sprint Demo

**Wireframe v2 (Figma) — copia congelada del Sprint 2:** https://www.figma.com/design/D6MoRPJIYxUlPG2GFS0iPR
**Flujo Sprint 2 (FigJam):** https://www.figma.com/board/kkarAUOiHV2DnjOzAmnfoC
**Wireframe v1 (referencia):** https://energiai-wireframe.vercel.app/
**Documento madre — Etapas del diseño frontend:** [`../../semana-1/anexos/etapas-diseno-frontend.md`](../../semana-1/anexos/etapas-diseno-frontend.md)

> ℹ️ El archivo de Figma original siguió evolucionando en los sprints siguientes, así que el enlace de arriba apunta a una **copia congelada** del estado del Sprint 2 — de modo que este documento siga describiendo lo que efectivamente se entregó. El archivo vivo está enlazado desde el [Informe Semana 3](../../semana-3/informe.md).

---

## 1. Alcance del Sprint 2

Solo quedan comprometidas **P-01 (ingreso de datos)** y **P-02 (resultado del análisis)**, en móvil (360 px) y escritorio (1280 px), con estos estados dibujados:

- P-01: inicial · validación con errores · enviando · error del backend (500) · servicio ML no disponible (503, implementado en la API el 30/07)
- P-02: completo · sin recomendaciones (bloque oculto) · cargando con marcadores (pendiente de dibujo en Figma)

**Pasan a backlog futuro:** P-03 Simulador, P-04 Mis análisis, P-05 Datos agregados, enlace compartible y estado «no encontrado» (requieren un identificador que la response aún no incluye), advertencia por consumo elevado (RF-19 · PA-08) y límite de consultas (PA-07).

**Consecuencias en las pantallas comprometidas:**

- La navegación del encabezado queda reducida a «Analizar»: «Mis análisis» y «Datos agregados» se retiran hasta que sus pantallas vuelvan al alcance.
- En P-02 el bloque de acciones queda solo con «Nuevo análisis»; «Simular ahorro» y «Copiar enlace» se retiran con sus pantallas de destino.
- La interfaz no se conecta al Back-End mientras el contrato no esté congelado; primero estructura estática, después integración.

## 2. Contrato V1.1 (fuente: código en `develop`)

**Endpoint:** `POST /api/v1/analisis-energetico` · Swagger en `/swagger-ui.html` · salud en `/actuator/health` · El documento «Contrato JSON V1.1» vive en [`docs/backend/`](https://github.com/No-Country-simulation/G9-LATAM-TEAM-09/tree/develop/docs/backend) del repo desde el 30/07.

**Entrada** (todos los campos obligatorios):

```json
{
  "consumo_kwh": 450.5,
  "cantidad_equipos": 8,
  "tipo_inmueble": "Casa",
  "uso_horario_pico": true,
  "horas_alto_consumo": 6
}
```

- `consumo_kwh`: decimal mayor que 0
- `cantidad_equipos`: entero entre **1 y 100**
- `tipo_inmueble`: exactamente uno de **Casa · Departamento · Comercio · Pyme** (validado por expresión regular; «Oficina» no existe)
- `uso_horario_pico`: booleano (franja de 18 a 23 h)
- `horas_alto_consumo`: entero entre 0 y 24

**Salida 200** (con la tarifa acordada de $ 0,75/kWh, implementada el 30/07):

```json
{
  "categoria": "Ineficiente",
  "probabilidad": 0.81,
  "recomendaciones": ["…"],
  "costo_estimado_mensual": 337.88
}
```

La response **no incluye**: identificador del análisis, fecha, tarifa aplicada, proyección anual ni umbral de consumo. Todo lo que la interfaz muestre de eso es derivado en el cliente y queda anotado así en el wireframe.

**Errores** (formato uniforme `DatosErrorRespuesta`):

```json
{
  "timestamp": "2026-07-30T11:45:00",
  "status": 400,
  "error": "BAD_REQUEST",
  "mensaje": "Errores de validacion en los datos de entrada",
  "detalles": [ { "campo": "consumo_kwh", "mensaje": "Debe ser mayor que 0" } ]
}
```

- 400 validación (con `detalles` por campo) · 400 JSON malformado (sin `detalles`) · 404 recurso inexistente · 500 error interno genérico
- **503 `SERVICE_UNAVAILABLE`** cuando el servicio ML no responde — decisión D2, **implementada el 30/07** tras la Sprint Demo (`ServicioMlNoDisponibleException`, mismo formato de error), lo que permite a la interfaz distinguir «servicio de análisis no disponible» de «error del servidor»

## 3. Correcciones aplicadas en el wireframe v2

- Tipo de inmueble: «Oficina» → **«Pyme»**; las etiquetas visibles («Depto.») envían el valor exacto del contrato («Departamento»).
- Cantidad de equipos: límite corregido de 1–500 a **1–100**.
- Moneda: se elimina «R$»; tarifa de referencia **$ 0,75/kWh confirmada** — el servicio la implementó el 30/07 tras la Sprint Demo (decisión D1 resuelta).
- «Confianza del modelo» documentada como presentación del campo `probabilidad` (0.0–1.0 → porcentaje).
- Fecha del análisis y proyección anual: marcadas «derivadas en el cliente».
- Mensajes de validación: se muestran bajo cada campo desde `detalles[campo, mensaje]` del error 400.
- Nuevo estado dibujado: «Servicio ML no disponible» con datos conservados.

## 4. Preguntas abiertas que el contrato ya respondió

- **PA-03 (tipos de inmueble):** respondida — el catálogo del modelo/Back-End es Casa, Departamento, Comercio, **Pyme**. El supuesto «Oficina» queda descartado.
- **PA-04 (moneda y tarifa):** respondida — «R$» descartado y tarifa **$ 0,75/kWh implementada en el servicio** (30/07).
- **PA-07 (límite de consultas):** hoy no existe en el Back-End; el estado pasa a backlog con la pregunta.
- **PA-13 (proyección anual):** mientras no esté en la response, se calcula en el cliente (×12) y se rotula como derivada.
- **PA-14 (cantidad de recomendaciones):** la lógica actual devuelve 3–4; el diseño soporta 1–5. Se propone fijar 5 como máximo en el contrato.
- **PA-19 (valores derivados):** la response solo trae los cuatro campos del punto 2; tarifa, umbral, fecha e identificador no vienen. Cualquier incorporación futura pasa por congelar una nueva versión del contrato.

## 5. Decisiones planteadas y su estado

- **D1 · Moneda y tarifa única.** ✅ **Resuelta (30/07):** el servicio calcula con $ 0,75/kWh, alineado con el enunciado y el README.
- **D2 · Código HTTP cuando el ML no está.** ✅ **Resuelta (30/07):** 503 `SERVICE_UNAVAILABLE` implementado, distinguible del 500 genérico.
- **D3 · Congelar el catálogo de tipos de inmueble** (¿«Pyme» es definitivo?) — pendiente; el dataset de Data Science hoy solo cubre Casa y Departamento.
- **D5 · Publicar el contrato en un solo lugar.** Parcialmente resuelta: el «Contrato JSON V1.1» vive en `docs/backend/` del repo desde el 30/07; queda unificar la numeración de versiones y sumar el OpenAPI como respaldo.
- **D6 · Mensajes de validación en español** para todos los campos (hoy solo `tipo_inmueble` tiene mensaje personalizado) — pendiente.

---

**Cierre esperado:** contrato congelado → wireframe v2 aprobado por Backend y PM → enlace registrado en la tarjeta de Trello → maquetado estático del formulario.
