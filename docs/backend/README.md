# ☕ Documentación del Back-End (Java / Spring Boot)

## 📌 Resumen
Documentación técnica del desarrollo de la API REST principal encargada de orquestar las peticiones, validaciones de datos y comunicación con el módulo de Machine Learning.

---

## 🛠️ Tecnologías y Versiones
- **Java:** 17+
- **Framework:** Spring Boot 3.x
- **Gestor de Dependencias:** Maven
- **Documentación API:** Swagger UI / OpenAPI 3.0

---

## 🔌 Endpoints

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `POST` | `/api/v1/analisis-energetico` | Procesa los datos de consumo y devuelve clasificación, costo y recomendaciones. |
| `GET`  | `/actuator/health` | Estado de salud del servicio backend. |

---

## 🐳 Dockerization del Backend

El backend se construye mediante un **Dockerfile multi-stage** optimizado para Java 17 y Spring Boot:

- **Etapa 1 (Builder):** Utiliza `maven:3.9.6-eclipse-temurin-17-alpine` para compilar el proyecto bajo `backend/analisis-energetico-api/` y generar el artefacto `.jar` omitiendo los tests en empaquetado (`./mvnw clean package -DskipTests`).
- **Etapa 2 (Runner):** Utiliza `eclipse-temurin:17-jre-alpine` ejecutado con un usuario no root (`appuser`), exponiendo el puerto `8080` e incluyendo comprobación de salud (`HEALTHCHECK`).

### Comando de Construcción Directo:
```bash
docker build -t energiai-backend -f backend/Dockerfile .
```

---

## 🖼️ Archivos y Capturas (`assets/`)
Guarde las capturas de pantalla de Postman, Swagger o diagramas en `docs/backend/assets/`.

