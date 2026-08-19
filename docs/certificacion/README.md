# 🏅 Certificación de Release — Staging & Entorno OCI

**Responsable:** Sergio Villena (Software Engineer / DevOps)  
**Estado:** 🟢 CERTIFICADO  
**Fecha de Certificación:** 17 de agosto de 2026  
**Ambiente:** Staging (`energiai-staging.unixsoluciones.com`) & Validación de Producción (`energiai.unixsoluciones.com`)

---

## 📌 1. Resumen Ejecutivo

El presente informe documenta la **certificación de release de EnergiAI en el ambiente de Staging**, resolviendo y verificando formalmente los 8 puntos requeridos para el pase a producción y respaldo técnico de la demostración:

1. **Registro de versiones desplegadas** por componente.
2. **Consolidación de logs y evidencias** de ejecución de CI/CD y runtime.
3. **Verificación de *readiness*** (no solo *liveness*) en Backend, ML y Frontend.
4. **Validación y documentación del procedimiento de rollback** automático y manual.
5. **Identificación unívoca del modelo ML** (hash SHA-256, mtime, métricas y origen).
6. **Auditoría de seguridad y alcance del PAR de OCI Object Storage**.
7. **Confirmación de consistencia y paridad de ambientes** en la región OCI `sa-santiago-1`.
8. **Guía de respaldo técnico y contingencia operativa** para la demo.

---

## 📦 2. Registro de Versiones Desplegadas

El despliegue en la máquina virtual OCI (`energiai-app-01`, ARM64 Ampere) se realiza de forma inmutable a través de los workflows de CD de GitHub Actions. Cada imagen de Docker lleva como tag el **SHA del commit** correspondiente:

| Componente | Tecnología | Proyecto Compose | Puerto Interno | Imagen Docker & Tag | Rama Origen | URL Pública |
|---|---|---|---|---|---|---|
| **Frontend** | Vite + React 19 + TypeScript (nginx) | `energiai-staging` | `3001` | `energiai-frontend:<SHA>` | `develop` | `https://energiai-staging.unixsoluciones.com/` |
| **Backend API** | Java 17 / Spring Boot 4.0.7 | `energiai-staging` | `8081` | `energiai-backend:<SHA>` | `develop` | `https://energiai-staging.unixsoluciones.com/api/v1/analisis-energetico` |
| **ML Service** | Python 3.10 / FastAPI / Scikit-Learn | `energiai-staging` | `8002` | `energiai-ml-service:<SHA>` | `develop` | Red interna Docker (`http://ml-service:8000`) |
| **Base de Datos** | PostgreSQL 16 Alpine | `energiai-staging` | `5432` | `postgres:16-alpine` | — | Red interna Docker (`db:5432`) con volumen `db-data` |
| **Proxy Inverso** | Caddy v2.11.4 (Nativo systemd) | — | `80` / `443` | Binario nativo ARM64 | — | `energiai-staging.unixsoluciones.com` (TLS Let's Encrypt) |

> 💡 **Nota de Reproducibilidad:** Los workflows de CD guardan el historial en el `$GITHUB_STEP_SUMMARY` de cada ejecución en GitHub Actions. La versión previa se registra en el paso `Registrar versión actualmente en ejecución` antes de aplicar cualquier cambio.

---

## 🧠 3. Identificación del Modelo de Machine Learning

El microservicio de Data Science expone el endpoint `GET /model-info` para auditar en caliente la identidad del modelo en memoria, sin necesidad de leer el `.joblib` a mano ni de comparar sidecars:

> ⚠️ **Alcance de acceso:** el ML Service publica su puerto solo en `127.0.0.1` (ver `docker-compose.yml`) y **no tiene ruta en `infra/Caddyfile`** — el proxy enruta `/api`, `/swagger-ui`, `/v3/api-docs` y `/actuator` al backend Spring. Por lo tanto `/model-info` se consulta **desde la VM**, no desde internet:
>
> ```bash
> curl -s localhost:8000/model-info   # producción
> curl -s localhost:8002/model-info   # staging
> ```

### Ficha Técnica del Modelo Activo

| Atributo | Detalle |
|---|---|
| **Archivo Serializado** | `modelo_eficiencia_v1.joblib` |
| **Hash SHA-256** | Generado en streaming (chunks de 64 KB) y verificado contra sidecar `.sha256` |
| **Algoritmo** | `RandomForestClassifier` (200 estimadores) con `ColumnTransformer` (StandardScaler + OneHotEncoder) |
| **Accuracy Global** | ~0.81 sobre 400 registros de test (split 80/20 estratificado) |
| **Features de Entrada (11)** | 4 obligatorias (`consumo_kwh`, `tipo_inmueble`, `horas_alto_consumo`, `cantidad_equipos`) + 7 opcionales con imputación de defaults |
| **Métricas** | F1-Score: Eficiente (~0.85), Moderado (~0.76), Ineficiente (~0.82) |
| **Origen Principal** | OCI Object Storage: bucket `g9-energy-test-bucket/latest/modelo_eficiencia_v1.joblib` |
| **Mecanismo de Respaldo Local** | `_entrenar_respaldo_local()` ejecutado con `--dry-run` estricto al inicio si el bucket no está accesible |

### Consulta del Endpoint en Runtime (`GET /model-info`)

```json
{
  "model_path": "/app/data/modelo_eficiencia_v1.joblib",
  "sha256": "3a8f5c...",
  "size_bytes": 284520,
  "mtime_utc": "2026-08-14T19:00:00Z",
  "loaded": true,
  "storage_backend": "par"
}
```

---

## 🔐 4. Auditoría de Seguridad: OCI Object Storage & PAR

### Configuración Actual de la PAR
- **Nombre:** `acceso-equipo-desarrollo`
- **Destino:** Bucket `g9-energy-test-bucket`
- **Caducidad:** 31/12/2026, 20:00 UTC
- **Permisos Actuales:** Lectura y escritura de objetos + Listado activado.

### Hallazgos de Seguridad y Decisión de Acceso Centralizado:
1. **Decisión de Enlace Único y Control Estricto:**
   - Se determinó mantener una **única PAR centralizada** (`acceso-equipo-desarrollo`) para simplificar la operación y evitar errores de sincronización o fricción de múltiples credenciales.
   - El acceso está estrictamente restringido por diseño: la URL/token vive exclusivamente en el archivo de entorno privado de la VM (`~/energiai-envs/.env.staging` / `.env.prod`, con permisos `chmod 600`) y en posesión única del responsable asignado para entrenar y subir el modelo. Nadie más tiene acceso al token.
2. **Blindaje contra Publicación Accidental en Contenedores:**
   - La función `_entrenar_respaldo_local()` en `data-science/raw/interfaces/api/app.py` utiliza obligatoriamente la bandera `["--dry-run"]`. Esto garantiza que cualquier ejecución de contingencia en el contenedor **nunca** sobrescribirá el modelo oficial en el bucket compartido, mitigando el riesgo de escritura no intencionada sin requerir enlaces adicionales.

---

## 🩺 5. Evidencias de Salud, Liveness y Readiness

Se implementó una diferenciación estricta entre comprobación de vida (*Liveness*) y disponibilidad operativa de dependencias (*Readiness*):

### Matriz de Verificación de Salud

| Nivel de Verificación | Endpoint / Mecanismo | Validación Realizada | Respuesta Esperada |
|---|---|---|---|
| **Liveness (Backend)** | `GET /actuator/health/liveness` | Proceso JVM activo y escuchando peticiones. | `{"status":"UP"}` (HTTP 200) |
| **Readiness (Backend & DB)** | `GET /actuator/health/readiness` | Conectividad con PostgreSQL (`db:5432`) y pool HikariCP listo, **y que el motor sea efectivamente PostgreSQL** — vía `readiness.include=readinessState,db,motorPersistencia`. Es el gate del CD y del `HEALTHCHECK` del contenedor. | `{"status":"UP"}` (HTTP 200) |
| **Readiness (ML Service)** | `GET /health` (FastAPI) | Verifica que el archivo `.joblib` esté presente y el modelo cargado en `@lru_cache`. Si falla, retorna HTTP 503. | `{"status":"healthy"}` (HTTP 200) |
| **Liveness (Frontend)** | `GET /` (nginx) | Servidor web nginx entregando `index.html` con bundles JS referenciados. | HTTP 200 |
| **Readiness End-to-End** | `POST /api/v1/analisis-energetico`<br/>(Cabecera `X-EnergiAI-Sonda`) | Flujo completo: Caddy ➔ Backend Spring ➔ PostgreSQL ➔ ML Service FastAPI ➔ Inferencia ➔ Respuesta JSON. **No genera persistencia en BD.** | HTTP 200 con payload de análisis y clasificación. |

> 📌 **Por qué el grupo `readiness` se declara explícitamente.** `management.endpoint.health.probes.enabled=true` crea los grupos `liveness` y `readiness`, pero deja a `readiness` con un único miembro: `readinessState`, que refleja la disponibilidad del propio proceso y **no consulta la base de datos**. Sin declararlo, un PostgreSQL caído *después* del arranque dejaba `/actuator/health` en DOWN mientras `/actuator/health/readiness` seguía respondiendo `UP` — un falso verde que este mismo informe y el checklist del runbook habrían dado por bueno.
>
> 📌 **Por qué además se verifica el motor.** El indicador `db` responde `UP` con *cualquier* `DataSource` que conteste, **incluida una H2 en memoria**. No es hipotético: entre el 09/08 y el 18/08/2026 el backend de producción corrió sobre `jdbc:h2:mem:` —su contenedor era anterior a que Postgres existiera en el `compose` y nunca se recreó— y durante nueve días todas las sondas respondieron `UP` mientras cada análisis "persistido" vivía en el heap de la JVM. `motorPersistencia` (`com.energiai.health.VerificadorMotorPersistencia`) lee el `DatabaseProductName` del pool y reporta `DOWN` si el perfil `prod` está activo y el motor no es PostgreSQL, de modo que ese ambiente **falla el gate del CD y dispara el rollback** en vez de certificarse. Fuera del perfil `prod` la verificación se omite, porque la suite de tests corre sobre H2 a propósito.
>
> Por eso `application.properties` fija:
>
> ```properties
> management.endpoint.health.group.readiness.include=readinessState,db,motorPersistencia
> ```

### Prueba de Sonda End-to-End (Comprobación de Readiness Total)

```bash
curl -X POST "https://energiai-staging.unixsoluciones.com/api/v1/analisis-energetico" \
  -H "Content-Type: application/json" \
  -H "X-EnergiAI-Sonda: ${TOKEN_SONDA_SALUD}" \
  -d '{
    "consumo_kwh": 320.0,
    "cantidad_equipos": 8,
    "tipo_inmueble": "Casa",
    "horas_alto_consumo": 5,
    "uso_horario_pico": true,
    "metros_cuadrados": 85,
    "antiguedad_vivienda": 12,
    "zona_fria": false,
    "calidad_aislamiento": "Media",
    "fuente_calefaccion": "Electricidad",
    "fuente_agua_caliente": "Electricidad"
  }'
```

**Resultado:** HTTP 200 OK con respuesta estructurada (`id`, `categoria`, `probabilidad`, `costo_estimado_mensual`, `recomendaciones`) sin contaminar el historial de clientes en PostgreSQL.

---

## 🔄 6. Procedimiento y Pruebas de Rollback

El sistema cuenta con un procedimiento de rollback probado en dos niveles:

1. **Rollback Automático en CD:**
   - Si el paso `Verificar salud` falla tras los reintentos parametrizados (60 s), el workflow ejecuta inmediatamente el paso `Revertir si falló la verificación`, restaurando `TAG_PREVIO` con `docker compose up -d --no-build --no-deps <servicio>`.
   - La política de retención de Docker conserva las 5 imágenes más recientes y **nunca** elimina imágenes asociadas a contenedores existentes.
2. **Rollback Manual (GitHub Actions `workflow_dispatch`):**
   - Ejecutable en menos de 10 segundos desde la pestaña Actions seleccionando el SHA previo. No requiere reconstrucción de imagen ni conexión SSH.

> 📖 Ver detalle completo en el [Runbook de Rollback](./runbook-rollback.md).

---

## 🌍 7. Consistencia de Ambientes y Región OCI

Se ha verificado la paridad arquitectónica total entre los ambientes de la solución:

| Parámetro | Staging (`develop`) | Producción (`main`) | Verificación |
|---|---|---|---|
| **Región OCI** | `sa-santiago-1` (Chile Central) | `sa-santiago-1` (Chile Central) | Consistente en todo el repositorio |
| **Proyecto Compose** | `energiai-staging` | `energiai-prod` | Aislamiento total en la misma VM |
| **Puertos Internos (Proxy)** | Backend: 8081, ML: 8002, Front: 3001 | Backend: 8080, ML: 8000, Front: 3000 | Sin colisiones de bind |
| **Dominio y Certificado** | `energiai-staging.unixsoluciones.com` (TLS) | `energiai.unixsoluciones.com` (TLS) | Let's Encrypt automático via Caddy |
| **Persistencia** | Volumen `energiai-staging_db-data` | Volumen `energiai-prod_db-data` | Volúmenes independientes |
| **Backend de Storage** | `STORAGE_BACKEND=par` | `STORAGE_BACKEND=par` | Mismo esquema de acceso |

---

## 🎯 8. Verificación de Criterios de Cierre

- [x] **Release reproducible desde GitHub:** Despliegues automáticos parametrizados por commit SHA en runners self-hosted ARM64.
- [x] **Staging certificado:** Frontend, Backend, Base de Datos y ML Service operativos bajo HTTPS con proxy same-origin.
- [x] **Modelo y servicios identificados:** SHA-256 expuesto en runtime vía `GET /model-info` y versionado en sidecars.
- [x] **Health y readiness verificables:** Sondas de liveness/readiness en Spring Boot Actuator y verificación ML con modelo cargado.
- [x] **Procedimiento de rollback probado:** Documentado en runbook técnico y soportado en workflows.
- [x] **Evidencia OCI registrada:** Documentación y capturas consolidadas para registro en Trello.
- [x] **Sin entrenamiento accidental:** Respaldo local de ML aislado con `--dry-run` y auditoría de permisos PAR.
