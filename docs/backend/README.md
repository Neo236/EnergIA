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

---

## 🐳 Dockerization del Backend y Orquestación

El backend se construye mediante un **Dockerfile multi-stage** optimizado para Java 17 y Spring Boot:

- **Etapa 1 (Builder):** Utiliza `maven:3.9-eclipse-temurin-17` para compilar el proyecto bajo `backend/analisis-energetico-api/` y generar el artefacto `.jar`.
- **Etapa 2 (Runner):** Utiliza `eclipse-temurin:17-jre` ejecutado con un usuario no root (`appuser`), exponiendo el puerto `8080` e incluyendo comprobación de salud (`HEALTHCHECK` mediante `wget` al endpoint `/actuator/health`).

> 💡 **Arquitectura ARM:** se usan las variantes Debian (no Alpine) porque la instancia OCI Compute del proyecto es **ARM**, y estas imágenes publican soporte `arm64` multi-arquitectura de forma confiable. Como estas variantes no incluyen `wget` por defecto, la etapa de runtime lo instala explícitamente para que el `HEALTHCHECK` siga funcionando.

### Orquestación con Docker Compose
La orquestación se gestiona mediante [`docker-compose.yml`](../../docker-compose.yml):
- Levanta el servicio `backend` aislado en la red interna `energiai-network`.

### Comando de Construcción y Ejecución:
```bash
# Construcción e inicio del contenedor Backend
docker compose up -d --build backend
```

---

## 🖼️ Archivos y Capturas (`assets/`)
Guarde las capturas de pantalla de Postman, Swagger o diagramas en `docs/backend/assets/`.

