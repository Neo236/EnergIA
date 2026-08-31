# ☕ Documentación del Back-End (Java / Spring Boot)

## 📌 Resumen
Documentación técnica del desarrollo de la API REST principal encargada de orquestar las peticiones, validaciones de datos y comunicación con el módulo de Machine Learning.

---

## 🛠️ Tecnologías y Versiones
- **Java:** 17+
- **Framework:** Spring Boot 4.0.7
- **Gestor de Dependencias:** Maven
- **Documentación API:** Swagger UI / OpenAPI 3.0

---

## 🔌 Endpoints

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `POST` | `/api/v1/analisis-energetico` | Procesa los datos de consumo y devuelve clasificación, costo y recomendaciones. |
| `GET`  | `/actuator/health` | Estado de salud del servicio backend (habilitado mediante `spring-boot-starter-actuator`). |
| `GET`  | `/actuator/health/liveness` | Sonda de *liveness*: el proceso JVM está vivo. No mira dependencias externas. |
| `GET`  | `/api/v1/analisis-energetico/{id}` | Recupera un análisis por su UUID. Es lo que hace que la URL de un resultado sea compartible y sobreviva a una recarga. |
| `GET`  | `/actuator/health/readiness` | Sonda de *readiness*: el proceso está disponible, PostgreSQL responde **y el motor es efectivamente PostgreSQL** (`readinessState` + `db` + `motorPersistencia`). Es el gate que usan el CD y el `HEALTHCHECK` del contenedor. |

### Verificar el `POST` sin ensuciar la base

Comprobar que el camino completo funciona —validación, llamada al modelo,
respuesta— exige un `POST` real, y cada `POST` real deja una fila. Si se hace
seguido, la tabla se llena de análisis que nadie pidió.

Para eso existe la cabecera `X-EnergIA-Sonda`: si su valor coincide con
`TOKEN_SONDA_SALUD`, el análisis se calcula y se devuelve igual, pero **no se
persiste**.

```bash
curl -X POST https://<host>/api/v1/analisis-energetico \
  -H 'Content-Type: application/json' \
  -H "X-EnergIA-Sonda: $TOKEN_SONDA_SALUD" \
  -d '{"consumo_kwh":420,"cantidad_equipos":10,"tipo_inmueble":"Casa", ... }'
```

> El token **no autoriza nada**: solo marca la petición como verificación. Si
> alguna vez se agrega un límite de peticiones, tiene que aplicarse por igual a
> las marcadas como sonda — de lo contrario esta cabecera dejaría de ser un
> detalle de persistencia y pasaría a ser una llave para saltear ese límite.
> Ver [`VerificadorSonda`](../../backend/analisis-energetico-api/src/main/java/com/energia/security/VerificadorSonda.java).

---

## 🐳 Dockerization del Backend y Orquestación

El backend se construye mediante un **Dockerfile multi-stage** optimizado para Java 17 y Spring Boot:

- **Etapa 1 (Builder):** Utiliza `maven:3.9-eclipse-temurin-17` para compilar el proyecto bajo `backend/analisis-energetico-api/` y generar el artefacto `.jar`.
- **Etapa 2 (Runner):** Utiliza `eclipse-temurin:17-jre` ejecutado con un usuario no root (`appuser`), exponiendo el puerto `8080` e incluyendo comprobación de salud (`HEALTHCHECK` mediante `wget` al endpoint `/actuator/health/readiness`, que además de la JVM valida la conexión con PostgreSQL).

> 💡 **Arquitectura ARM:** se usan las variantes Debian (no Alpine) porque la instancia OCI Compute del proyecto es **ARM**, y estas imágenes publican soporte `arm64` multi-arquitectura de forma confiable. Como estas variantes no incluyen `wget` por defecto, la etapa de runtime lo instala explícitamente para que el `HEALTHCHECK` siga funcionando.

### Orquestación con Docker Compose
La orquestación se gestiona mediante [`docker-compose.yml`](../../docker-compose.yml):
- Levanta el servicio `backend` aislado en la red interna `energia-network`.
- *Nota:* El servicio `ml-service` se encuentra temporalmente comentado hasta que el módulo de Data Science complete sus archivos fuente.

### Comando de Construcción y Ejecución:
```bash
# Construcción e inicio del contenedor Backend
docker compose up -d --build backend
```

---

## 🖼️ Archivos y Capturas (`assets/`)
Guarde las capturas de pantalla de Postman, Swagger o diagramas en `docs/backend/assets/`.

