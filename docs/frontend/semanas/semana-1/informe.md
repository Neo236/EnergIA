# 🗓️ Semana 1 (Sprint 1) — Informe de participación · Frontend

> ✅ **Versión final** — informe personal de participación (rol frontend).

**Lautaro Sebastián Mambrin** · **Período:** 20 al 26 de julio de 2026

## 🎯 Mis objetivos de la semana

- Producir el wireframe del MVP con su descriptivo funcional.
- Acompañar la integración del trabajo del equipo en el repo (merges y reviews).

## ✅ Lo que hice

- **Diseño del frontend — el grueso de la semana (en Notion y Vercel, sin subir nada al repo):** construí el prototipo navegable de alta fidelidad ([energiaimockup.vercel.app](https://energiaimockup.vercel.app/)) con su documentación (etapa 5). Después, para darle base formal, escribí las etapas 1 a 3 — especificación de requerimientos, arquitectura de información y flujos, y wireframes con descriptivo funcional — y dibujé el wireframe estructural de baja fidelidad de 18 frames ([energiai-wireframe.vercel.app](https://energiai-wireframe.vercel.app/)). El proceso dejó documentadas 19 preguntas abiertas (PA-01 a PA-19) con su supuesto vigente.
- **Propuesta técnica inicial:** ofrecí una propuesta técnica antes de que el Software Engineer se integrara al equipo; no fue la versión final que quedó, pero ayudó a establecer el stack definitivo.
- **Integración del trabajo de otros:** mergeé los PRs [#7](https://github.com/No-Country-simulation/G9-LATAM-TEAM-09/pull/7) y [#8](https://github.com/No-Country-simulation/G9-LATAM-TEAM-09/pull/8) (Docker Compose y docs de Sergio, 24/07) y hice el review con sugerencias inline del [PR #9](https://github.com/No-Country-simulation/G9-LATAM-TEAM-09/pull/9) (gobernanza y CI, 25/07); el 26/07 revisé y aprobé el [PR #10](https://github.com/No-Country-simulation/G9-LATAM-TEAM-09/pull/10), cuyos fixes aporté ya en la semana 2.

**Aclaración de trazabilidad:** al cierre de la semana no había subido ningún archivo propio al repo — mis únicas acciones allí fueron merges y reviews. La documentación del proyecto en el repo (plan de semana 1, estructura de docs) fue trabajo de Sergio. Mi participación en documentos del repo empezó en la semana 2 (PR #15).

## ⚠️ Problemas y errores (míos)

- **Empecé por el final:** construí las etapas 4 y 5 antes que las etapas 1–3, que omití por error al iniciar. Al completarlas después quedó claro que el prototipo y su documentación se apoyaban en un contrato **asumido**, no real: trabajo de más que **probablemente quede descartado** — la etapa 3 quedó establecida como fuente de verdad y el prototipo se corrige (o rehace) contra ella.
- **Supuestos sin validar contra el backend:** el wireframe asumió catálogo con «Oficina», moneda «R$» y equipos 1–500. La re-auditoría del PM los marcaría como desalineados la semana siguiente.
- **La lección:** primero requerimientos y contrato, después dibujar. Las 19 preguntas abiertas son la parte rescatable de ese desvío — el proceso inverso las hizo visibles.

## 📋 Estado de mi frente al cierre

- Wireframe de 18 frames entregado, pendiente de aprobación del equipo.
- Contrato JSON todavía en discusión; sin validaciones implementadas en el backend.
- Nada mío subido al repo aún — primer aporte propio de código/docs recién en semana 2.

## 🔗 Evidencia

- Wireframe (etapa 3): https://energiai-wireframe.vercel.app/ · Prototipo (etapa 4): https://energiaimockup.vercel.app/
- Reviews y merges: PR #7, #8 (merges 24/07) · PR #9 (review 25/07) · PR #10 (review y approve 26/07)

### Documentos del informe

Este informe referencia **dos documentos**, en la carpeta [`anexos/`](./anexos/):

1. [**Etapas del diseño frontend (1–5) — snapshot Semana 1**](./anexos/etapas-diseno-frontend.md) — las cuatro etapas documentadas, centralizadas en un solo documento y preservadas tal como estaban en ese momento (la etapa 4 no tiene documento propio: es el prototipo desplegado en Vercel).
2. [**EnergiAI — Propuesta Técnica**](./anexos/propuesta-tecnica.md) — la propuesta inicial del 21/07, previa a la integración del Software Engineer al equipo.
