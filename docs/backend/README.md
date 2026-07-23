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

## 🖼️ Archivos y Capturas (`assets/`)
Guarde las capturas de pantalla de Postman, Swagger o diagramas en `docs/backend/assets/`.
