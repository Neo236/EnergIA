# 📋 Evidencias — Lautaro (09/08)

> 📎 **Anexo del [Informe Semana 3](../informe.md)** — evidencias con enlaces, resultados ejecutables y bloqueos. Todos los enlaces a PRs son públicos (repo de la organización).

## 🧑‍💻 Contexto del rol

Rol: **frontend**. Esta semana el aporte fue el frontend en sí —de wireframe a aplicación desplegada en los dos ambientes— más el despliegue continuo, construido **en conjunto con Sergio Villena**.

## ✅ Evidencias con enlace

| Aporte | Evidencia | Estado |
|---|---|---|
| **Wireframe v2.2 alineado a V1.2**: formulario 4+7 con defaults visibles, 5 pantallas nuevas de escritorio, tablero reorganizado, contraste corregido en 302 nodos de texto (3,36:1 → 5,02:1, WCAG AA) | [Figma — archivo vivo](https://www.figma.com/design/CQNvYzt1HSeKODlx63hQPc) · [copia congelada del Sprint 2](https://www.figma.com/design/D6MoRPJIYxUlPG2GFS0iPR) | ✅ 07/08 |
| **Front-end mínimo P-01/P-02** con respuestas simuladas, ocho estados, payload mínimo | [PR #41](https://github.com/No-Country-simulation/G9-LATAM-TEAM-09/pull/41) | ✅ Mergeado 07/08 |
| **Mockup navegable** para demostrar sin depender del back-end | [energiai-mockup-p01-p02.vercel.app](https://energiai-mockup-p01-p02.vercel.app) | ✅ En línea |
| **Contenedor + proxy same-origin + CD del front**: imagen no-root multi-arquitectura, `Caddyfile` versionado en `infra/`, rollback por tag sin reconstrucción | [PR #50](https://github.com/No-Country-simulation/G9-LATAM-TEAM-09/pull/50) | ✅ Mergeado 09/08 |
| **CD de los tres componentes — con Sergio Villena.** `cd-frontend.yml` sirvió de plantilla; Sergio construyó `cd-backend.yml` y `cd-ml.yml` sobre ese esquema, más la verificación de `.env` por ambiente y el storage vía PAR | [PR #51](https://github.com/No-Country-simulation/G9-LATAM-TEAM-09/pull/51) · [#52](https://github.com/No-Country-simulation/G9-LATAM-TEAM-09/pull/52) · [#53](https://github.com/No-Country-simulation/G9-LATAM-TEAM-09/pull/53) · [#55](https://github.com/No-Country-simulation/G9-LATAM-TEAM-09/pull/55) | ✅ Mergeados 09/08 |
| **Endurecimiento de los tres workflows de CD**: tag explícito, healthcheck con diagnóstico, rollback seguro | [PR #54](https://github.com/No-Country-simulation/G9-LATAM-TEAM-09/pull/54) | ✅ Mergeado 09/08 |
| **Primer despliegue real del proyecto**: los dominios pasaron de 502 (desde el 27/07) a servir la aplicación con HTTPS, en los dos ambientes | Dominios vivos, abajo | ✅ 09/08 |
| **Migración a Vite + React + TypeScript**: contrato tipado, router con tres rutas, mensajes de error propios, documentación de arquitectura con diagramas | [PR #57](https://github.com/No-Country-simulation/G9-LATAM-TEAM-09/pull/57) | ✅ Mergeado 09/08 |
| **Verificación de la integración contra la API real**: clon aislado del stack completo en la VM, sin tocar los ambientes desplegados | Hallazgos en la [adenda](./adenda-sprint-3.md#2-hallazgos-verificados) | ✅ 09/08 |

## ▶️ Resultados ejecutables (hoy, cualquiera puede verificarlos)

```bash
curl -o /dev/null -w "%{http_code}\n" https://energiai.unixsoluciones.com/            # 200
curl -o /dev/null -w "%{http_code}\n" https://energiai.unixsoluciones.com/actuator/health   # 200
curl -o /dev/null -w "%{http_code}\n" https://energiai-staging.unixsoluciones.com/   # 200
```

- **Los dos ambientes sirven la aplicación con HTTPS válido.** Es el primer despliegue del proyecto: hasta el 09/08 los dominios devolvían 502.
- **Swagger y la spec OpenAPI** quedaron accesibles desde el mismo dominio (`/swagger-ui/index.html`, `/v3/api-docs`) gracias al ruteo del proxy — sin eso, el patrón same-origin los habría mandado al frontend y habrían devuelto 404.
- **Cuatro workflows** en [Actions](https://github.com/No-Country-simulation/G9-LATAM-TEAM-09/actions): el CI (con jobs de backend, data-science, frontend y build de imágenes) y los tres CD, uno por componente.
- **Mockup de demostración** con cuatro respuestas forzables desde la barra inferior (200, 200 sin recomendaciones, 500 y 503): [energiai-mockup-p01-p02.vercel.app](https://energiai-mockup-p01-p02.vercel.app)

## ⛔ Bloqueos y dependencias

- **La aplicación no completa un análisis todavía.** `POST /api/v1/analisis-energetico` devuelve 400 por el corte Java↔ML ([F-01](./adenda-sprint-3.md#f-01--el-que-bloquea-todo)): Java envía booleanos donde el ML exige `"Si"`/`"No"`. Es de Back-End o Data Science; el frontend ya muestra ese error correctamente. **Es el único bloqueo para que el MVP funcione punta a punta.**
- **Sin identificador en la respuesta** (PA-19): bloquea enlaces compartibles y la pantalla «mis análisis».
- **Identidad visual sin definir**: la paleta actual es temporal.
- **`tipo_inmueble` sin peso confirmado en el modelo**: pendiente de re-verificar contra la lógica que Data Science reescribió el 05/08.
- **Persistencia**: sigue sin motor de base de datos definido, y el endpoint de consulta es obligatorio del enunciado.

## 🔁 Prácticas que quedaron incorporadas

- **Registrar contra qué versión se verifica cada cosa.** El código de los otros componentes cambió varias veces durante el sprint, así que cada hallazgo de la adenda lleva el commit contra el que se comprobó.
- **Probar con el cliente real, no solo con `curl`.** Varias diferencias solo aparecen desde el navegador — por ejemplo, Spring localiza los mensajes de validación según la cabecera `Accept-Language`, que `curl` no envía.
- **Revisar el estado de los contenedores, no solo la respuesta del sitio.** Un healthcheck mal apuntado deja el contenedor marcado `unhealthy` sin que el sitio deje de responder: no hay síntoma visible hasta que se mira.
