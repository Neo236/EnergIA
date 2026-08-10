# 🗓️ Semana 3 (Sprint 3) — Informe de participación · Frontend

> ✅ **Versión final** — informe personal de participación (rol frontend).

**Lautaro Sebastián Mambrin** · **Período:** 3 al 9 de agosto de 2026

## 🎯 Mis objetivos de la semana

- Alinear el wireframe al contrato V1.2 que entró en `develop` y completar las pantallas de escritorio que quedaban pendientes desde el Sprint 2.
- Sacar el frontend del papel: pasar de wireframe a código desplegable.
- Poner la aplicación en la VM de OCI — los dominios seguían devolviendo 502 desde el 27/07.
- Dejar el despliegue automatizado, no manual.

## ✅ Lo que hice

- **Wireframe v2.2 alineado al contrato V1.2:** llevé el formulario a **4 campos obligatorios + 7 opcionales**, y dejé cada opcional mostrando en su propio control el valor por defecto que aplica el back-end si no se envía. Dibujé las **cinco pantallas de escritorio** que faltaban (validación, enviando, error 500, servicio no disponible, y P-02 sin recomendaciones), reorganicé el tablero en tres filas rotuladas sin solapes, y corregí un problema de accesibilidad que venía del wireframe original: el gris de los textos secundarios daba **3,36:1** de contraste, por debajo del mínimo 4,5:1 de WCAG AA. Lo llevé a 5,02:1 en **302 nodos de texto**. Congelé una copia del wireframe del Sprint 2 y dejé el archivo vivo renombrado para el Sprint 3.

- **Front-end mínimo P-01/P-02 ([PR #41](https://github.com/No-Country-simulation/G9-LATAM-TEAM-09/pull/41), mergeado 07/08):** lo implementé en HTML, CSS y JS puros, sin build ni dependencias — decisión deliberada para que el PR fuera revisable por el equipo, que es mayoritariamente Java y Python. Cubrí los ocho estados dibujados con respuestas simuladas, y lo armé para que envíe el **payload mínimo**: los obligatorios y solo los opcionales que el usuario tocó. Lo desplegué además en Vercel, para poder demostrarlo sin depender del back-end.

- **Contenedor, proxy y despliegue continuo del front ([PR #50](https://github.com/No-Country-simulation/G9-LATAM-TEAM-09/pull/50), mergeado 09/08):** empaqueté el front como imagen `nginx-unprivileged` no-root y multi-arquitectura, versioné el `Caddyfile` de la VM en `infra/` (hasta entonces existía **solo** en la instancia, uno de los pendientes que el propio runbook de OCI marcaba), y escribí `cd-frontend.yml` con despliegue por rama y **rollback sin reconstrucción** — la versión desplegada es el tag de la imagen, que es el SHA del commit, así que volver atrás relevanta el mismo binario que ya corrió.

- **CI/CD para los tres componentes — trabajo conjunto con Sergio Villena.** Mi `cd-frontend.yml` sirvió de plantilla; Sergio construyó sobre esa base `cd-backend.yml` y `cd-ml.yml` con el mismo esquema de concurrencia, rollback y healthcheck ([PR #51](https://github.com/No-Country-simulation/G9-LATAM-TEAM-09/pull/51), [#52](https://github.com/No-Country-simulation/G9-LATAM-TEAM-09/pull/52), [#53](https://github.com/No-Country-simulation/G9-LATAM-TEAM-09/pull/53), [#55](https://github.com/No-Country-simulation/G9-LATAM-TEAM-09/pull/55)), y sumó la verificación de `.env` por ambiente y el backend de storage vía PAR. Yo aporté el endurecimiento de los tres workflows en [PR #54](https://github.com/No-Country-simulation/G9-LATAM-TEAM-09/pull/54): tag explícito, healthcheck con diagnóstico y rollback seguro. **El resultado es de los dos, no de ninguno por separado.**

- **Primer despliegue real del proyecto:** puse la aplicación en la VM y los dominios pasaron de 502 —como estaban desde el 27/07— a servir con HTTPS. Hoy corren **los dos ambientes completos**, cada uno con sus tres servicios.

- **Migración a Vite + React + TypeScript ([PR #57](https://github.com/No-Country-simulation/G9-LATAM-TEAM-09/pull/57), mergeado 09/08):** pasé el contrato a `contrato.ts` tipado, así que un cambio de campo ahora rompe la **compilación** en vez de fallar en ejecución. Sumé router con tres rutas, escribí mensajes de error propios en vez de mostrar los crudos de la API, y documenté la arquitectura en [`docs/frontend/README.md`](../../README.md) con dos diagramas mermaid. Archivé el prototipo en HTML puro conservando su historia de git.

- **Verificación de la integración contra la API real:** monté un clon aislado del stack completo en la VM —proyecto compose separado, puertos propios, sin tocar los ambientes desplegados— y probé el endpoint punta a punta. De ahí salieron los hallazgos del anexo.

## 🔄 Cambios respecto a la Semana 2

- **De wireframe a producto desplegado:** la Semana 2 cerró con la infraestructura lista y los dominios en 502; esta semana cierra con las dos pantallas corriendo en los dos ambientes.
- **De despliegue manual a CD:** el primer deploy lo hice a mano para validar cada paso; al cierre, los tres componentes se despliegan solos al mergear.
- **De contrato V1.1 a V1.2:** 4 obligatorios + 7 opcionales con defaults, en el wireframe y en el código.
- **De un stack sin build a Vite + React + TS:** arrancar en HTML puro fue lo correcto para el primer PR; migré cuando el alcance lo justificó.

## ▶️ Verificable hoy por cualquiera

- **Aplicación desplegada** en [energiai-staging.unixsoluciones.com](https://energiai-staging.unixsoluciones.com) → **200**, con la pantalla propia de «no encontrado» al probar cualquier ruta inexistente, y en [energiai.unixsoluciones.com](https://energiai.unixsoluciones.com) → **200**, con `/actuator/health` respondiendo **200**.
- **Mockup de demostración** (Vercel, respuestas simuladas): [energiai-mockup-p01-p02.vercel.app](https://energiai-mockup-p01-p02.vercel.app)
- Los cuatro workflows en [Actions](https://github.com/No-Country-simulation/G9-LATAM-TEAM-09/actions): el CI —con sus jobs de backend, data-science, frontend y build de imágenes— más los tres CD, uno por componente.
- **Estado de la integración:** el endpoint de análisis responde 400 mientras el back-end y el servicio de ML terminan de alinear el tipo de dos campos. La interfaz ya interpreta y muestra esa respuesta; el detalle técnico está en la [adenda](./anexos/adenda-sprint-3.md).

## 🔗 Evidencia

- Wireframe v2.2 vivo (Figma): https://www.figma.com/design/CQNvYzt1HSeKODlx63hQPc
- Wireframe Sprint 2 congelado (referencia histórica): https://www.figma.com/design/D6MoRPJIYxUlPG2GFS0iPR
- Flujo Sprint 2 (FigJam): https://www.figma.com/board/kkarAUOiHV2DnjOzAmnfoC
- Arquitectura del front en el repo: [`docs/frontend/README.md`](../../README.md)
- Código y cómo correrlo: [`frontend/README.md`](../../../../frontend/README.md)

### Documentos del informe

Este informe referencia **dos documentos**, en la carpeta [`anexos/`](./anexos/):

1. [**Adenda Sprint 3 — contrato V1.2 y hallazgos de integración**](./anexos/adenda-sprint-3.md) — la actualización formal del contrato desde la óptica del frontend, y los hallazgos verificados con la fecha y el commit contra el que se comprobó cada uno.
2. [**Evidencias — Lautaro (09/08)**](./anexos/evidencias.md) — recopilación con enlaces a PRs, resultados ejecutables y bloqueos.
