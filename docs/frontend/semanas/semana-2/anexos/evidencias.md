# 📋 Evidencias — Lautaro (30/07)

> 📎 **Anexo del [Informe Semana 2](../informe.md)** — recopilación breve de evidencias reales con enlaces, resultados ejecutables y bloqueos, presentada en la Sprint Demo del 30/07. Los enlaces a PRs y docs son públicos (repo de la org).

## 🧑‍💻 Contexto del rol

Rol: **frontend**. El aporte de estas semanas fue **infraestructura, CI/CD, documentación y asistencia en PRs de otros** — todo con evidencia enlazable abajo. La infra ya quedó lista para recibir el frontend (ruteo same-origin en el proxy: raíz del dominio → front, `/api/*` → backend).

## ✅ Evidencias reales (con enlace)

| Aporte | Evidencia | Estado |
|---|---|---|
| **Infraestructura OCI completa**: VM ARM (`energiai-app-01`), red + firewall NSG, IP reservada, dominios con HTTPS automático (Caddy + Let's Encrypt), runner de CD registrado | Doc completa en develop: [docs/oci-cloud/README.md](https://github.com/No-Country-simulation/G9-LATAM-TEAM-09/blob/develop/docs/oci-cloud/README.md) · URLs vivas: [energiai.unixsoluciones.com](http://energiai.unixsoluciones.com) y [energiai-staging.unixsoluciones.com](http://energiai-staging.unixsoluciones.com) | ✅ Productiva desde el 27/07 |
| **Documentación del repo**: OCI, arquitectura (diagrama mermaid) y actualización del README — integrando el trabajo de Object Storage/PAR de Sergio sin pisarlo | [PR #15](https://github.com/No-Country-simulation/G9-LATAM-TEAM-09/pull/15) · commits `2a91bf8`, `59672a6`, `8f94cbb` | ✅ Mergeado 29/07 |
| **Asistencia PR #9 (CI de Sergio)**: review con sugerencias inline + approve | [PR #9](https://github.com/No-Country-simulation/G9-LATAM-TEAM-09/pull/9) | ✅ Mergeado 25/07 |
| **Asistencia PR #10 (actuator/Docker de Sergio)**: review que detectó y reprodujo el bug del `mvnw` sin permisos de ejecución (docker build roto en clones frescos) + 3 commits propios en su rama con los fixes | [PR #10](https://github.com/No-Country-simulation/G9-LATAM-TEAM-09/pull/10) · commits `c938a97`, `562eec3`, `5684660` | ✅ Mergeado 27/07 |
| **Asistencia PR #13 (validaciones de Leandro)**: review del 28/07 (tests rotos por mensajes del handler, `@Schema` inconsistente) + resolución final del CI (cherry-pick del fix a la rama correcta conservando la autoría de Leandro) | [PR #13](https://github.com/No-Country-simulation/G9-LATAM-TEAM-09/pull/13) · commit `9291a72` | ✅ Mergeado 30/07 |
| **Análisis PR #16**: diagnóstico de que era la otra mitad del fix del #13 sobre la base equivocada (develop) → cambio llevado al #13 y cierre coordinado sin dejar develop en rojo | [PR #16](https://github.com/No-Country-simulation/G9-LATAM-TEAM-09/pull/16) | ✅ Cerrado 30/07 |
| **Propuesta de CD**: workflows de deploy automático staging/prod sobre el runner de la VM, verificados E2E en réplica | Páginas de la documentación interna — workflows listos en workspace local | 🟡 Pendiente de aprobación del equipo |

*Los commits se referencian por SHA corto — en GitHub se accede navegando el PR correspondiente (pestaña Commits).*

## ▶️ Resultados ejecutables (hoy, cualquiera puede verificarlos)

- Un `curl -I` (o abrir en el navegador) el dominio de producción o el de staging → **TLS válido + 502 esperado** (proxy vivo, aún sin app detrás): prueba de punta a punta DNS → firewall → Caddy → HTTPS.
- **CI verde en develop**: [Actions del repo](https://github.com/No-Country-simulation/G9-LATAM-TEAM-09/actions) — build + tests del backend y build de imágenes Docker (multi-arch, compatibles con la VM ARM).
- **Backend local**: `./mvnw verify` en `backend/analisis-energetico-api/` → tests en verde · `docker compose build` → las imágenes buildean en x86 y ARM.
- **Con el primer deploy** quedan ejecutables sobre los dominios públicos: Swagger UI (`/swagger-ui/index.html`), spec OpenAPI (`/v3/api-docs`) y salud (`/actuator/health`).

## ⛔ Bloqueos y dependencias

- **Primer deploy** depende de: (1) aprobación del PR de workflows de CD, (2) recrear los `.env` por ambiente en la VM, (3) `requirements.txt` del ml-service — sigue en la rama `data` sin mergear.
- **Persistencia**: el endpoint de consulta del MVP requiere una base de datos; el motor es decisión pendiente del equipo (el backend hoy no tiene ninguna configurada).
- **Backend vs contrato** (anotado en TODOs y Notas): tarifa 100/120 en código vs $0,75/kWh del contrato · bug 404→500 en rutas inexistentes.
- **Object Storage**: el bucket vive en la tenancy personal de Sergio (vía PAR funciona; conversar administración y rotación).
- **Backup de secretos** (`.env`, wallet, Caddyfile) sin definir — hoy solo existen en la VM.
