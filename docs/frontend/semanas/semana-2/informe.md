# 🗓️ Semana 2 (Sprint 2) — Informe de participación · Frontend

> ✅ **Versión final** — informe personal de participación (rol frontend).

**Lautaro Sebastián Mambrin** · **Período:** 27 al 31 de julio de 2026

## 🎯 Mis objetivos de la semana

- Atender la re-auditoría del PM (28/07): acotar el wireframe a P-01/P-02 y alinearlo al contrato real.
- Dejar la instancia de OCI lista para recibir la aplicación.
- Sostener el CI y asistir los PRs del equipo donde hiciera falta.

## ✅ Lo que hice

- **Re-auditoría atendida en su totalidad:** audité el wireframe contra el código real de `develop`, confirmé las desalineaciones y produje el **wireframe v2 en Figma** — P-01 y P-02 en móvil (360) y escritorio (1280), con estados de validación (mensajes del error 400), envío, error del servidor (500) y «servicio ML no disponible» (503 — propuesto en la demo e implementado por Backend el mismo 30/07). Armé además el flujo Sprint 2 en FigJam y la **adenda formal a la Etapa 3** con el contrato V1.1 documentado. P-03/P-04/P-05 pasaron a backlog, y seis preguntas abiertas quedaron respondidas por el código (PA-03, 04, 07, 13, 14, 19). Aclaré además el conteo del hallazgo del PM: las «18 páginas» eran 18 frames — 5 pantallas en variantes móvil/escritorio más estados críticos.
- **Instancia de OCI productiva desde el 27/07:** VM ARM `energiai-app-01`, red y firewall NSG, IP reservada, dominios con HTTPS automático ([energiai.unixsoluciones.com](http://energiai.unixsoluciones.com) y staging), runner de CD registrado y ruteo same-origin listo para el frontend (raíz → front, `/api/*` → backend).
- **Documentación del repo ([PR #15](https://github.com/No-Country-simulation/G9-LATAM-TEAM-09/pull/15), mergeado 29/07):** documenté **la instancia y lo que corre hoy en ella** — proxy inverso, runner de CD y Docker —, la arquitectura real con diagrama y la actualización del README. **La documentación de OCI fue trabajo de ambos con Sergio:** él documentó Object Storage y el acceso vía PAR, y yo integré las dos partes sin pisar la suya. Dejé además preparado el rediseño de los diagramas mermaid del repo (borrador del 30/07, pendiente de OK del equipo).
- **Asistencia en PRs:** en el [#10](https://github.com/No-Country-simulation/G9-LATAM-TEAM-09/pull/10) detecté y reproduje el bug del `mvnw` sin permisos y aporté 3 commits de fix (27/07); en el [#13](https://github.com/No-Country-simulation/G9-LATAM-TEAM-09/pull/13) hice el review del 28/07 y resolví el CI en rojo con un cherry-pick a la rama correcta conservando la autoría de Leandro (mergeado 30/07); el [#16](https://github.com/No-Country-simulation/G9-LATAM-TEAM-09/pull/16) lo diagnostiqué como duplicado del fix y coordiné su cierre sin dejar `develop` en rojo. Cerré la semana revisando y mergeando los PRs [#18](https://github.com/No-Country-simulation/G9-LATAM-TEAM-09/pull/18), [#19](https://github.com/No-Country-simulation/G9-LATAM-TEAM-09/pull/19), [#20](https://github.com/No-Country-simulation/G9-LATAM-TEAM-09/pull/20) y [#21](https://github.com/No-Country-simulation/G9-LATAM-TEAM-09/pull/21) (30/07), que materializaron los acuerdos de la demo: tarifa $ 0,75 en el servicio, error 503 del ML, contrato V1.1 publicado en `docs/backend/` y fix del README.
- **Propuesta de CD:** workflows de deploy automático staging/prod sobre el runner de la VM, verificados E2E en réplica — pendiente de OK del equipo.
- **Análisis del diccionario de datos:** crucé el `df_final` de Data Science contra el contrato V1.1 y el ml-service, detecté las incompatibilidades (catálogo de inmuebles, rangos, 6 features sin transporte, nombres viejos) y dejé registrados en la página TODOs y Notas los puntos de contrato a resolver con el equipo: identificador y fecha del análisis, campos opcionales del modelo e imputación de faltantes.
- **Gestión:** presenté todo en la Sprint Demo del jueves 30/07 con guion, informe y evidencias enlazables.

## 🔄 Cambios respecto a la Semana 1

- **Alcance de diseño:** del wireframe de 5 pantallas (18 frames) a solo P-01 y P-02; P-03/P-04/P-05, el enlace compartible con su estado 404, la advertencia RF-19 y el límite de consultas pasaron a backlog.
- **Contrato:** de supuestos sin validar («Oficina», «R$», equipos 1–500) al contrato V1.1 real implementado en `develop` y documentado en la adenda; 6 de las 19 preguntas abiertas de la Semana 1 quedaron respondidas por el código.
- **Herramienta de diseño:** el wireframe pasó del HTML estático en Vercel (v1) a Figma (v2); la v1 queda como referencia histórica.
- **Etapas 4 y 5:** se confirmó que fueron trabajo de más — el prototipo hi-fi y su documentación quedan sujetos a descarte; la implementación partirá del wireframe v2 y del contrato congelado, no del prototipo.
- **Mi relación con el repo:** de solo merges y reviews (Semana 1) a los primeros aportes propios — fixes en el PR #10, documentación en el #15 y resolución del CI en el #13.

## ▶️ Verificable hoy por cualquiera

- Dominios vivos con TLS válido y 502 esperado (proxy sin app detrás): `energiai.unixsoluciones.com` y `energiai-staging.unixsoluciones.com`.
- [CI en verde sobre `develop`](https://github.com/No-Country-simulation/G9-LATAM-TEAM-09/actions) — build + tests + imágenes Docker multi-arch para la VM ARM.
- Backend local: `./mvnw verify` en verde · `docker compose build` funciona en x86 y ARM.

## ⚠️ Problemas y errores

- Mis supuestos de la semana 1 en el wireframe (Oficina, R$, 1–500) resultaron efectivamente desalineados — corregidos en la v2; quedó como práctica auditar contra el código antes de entregar.
- El CI quedó en rojo tras el primer intento de fix del #13 (base equivocada); lo resolví con el cherry-pick coordinado.
- Deuda del backend que quedó anotada en la página TODOs y Notas del proyecto: la tarifa 100/120 en código vs $ 0,75/kWh documentada (✅ resuelta el mismo 30/07 con los PRs post-demo), el bug 404→500 en rutas inexistentes y la falta de persistencia con su endpoint de consulta (obligatorio del enunciado) — estos dos últimos siguen pendientes.

## 🔗 Evidencia

- Wireframe v2 (Figma): https://www.figma.com/design/CQNvYzt1HSeKODlx63hQPc · Flujo (FigJam): https://www.figma.com/board/kkarAUOiHV2DnjOzAmnfoC
- CI/Actions: https://github.com/No-Country-simulation/G9-LATAM-TEAM-09/actions
- Dominios: http://energiai.unixsoluciones.com · http://energiai-staging.unixsoluciones.com
- Doc OCI en el repo: [`docs/oci-cloud/`](https://github.com/No-Country-simulation/G9-LATAM-TEAM-09/blob/develop/docs/oci-cloud/README.md)

### Documentos del informe

Este informe referencia **dos documentos**, en la carpeta [`anexos/`](./anexos/):

1. [**Adenda Sprint 2 — alcance recortado y contrato V1.1**](./anexos/adenda-sprint-2.md) — la actualización formal de la Etapa 3 con el contrato real, pendiente de aprobación de Backend y PM.
2. [**Evidencias — Lautaro (30/07)**](./anexos/evidencias.md) — la recopilación de evidencias con enlaces a PRs, commits y resultados ejecutables presentada en la Sprint Demo.
