# 🗓️ Informe Semanal – Back-End | EnergiAI

**Semana:** 1
**Período:** 20 de julio – 26 de julio de 2026
**Integrantes:** Alan Federico Cabrera · Leandro Moreno
**Área:** Back-End (Java / Spring Boot)
**Estado:** 🟢 Completado

---

## 📌 Resumen

Semana n° 1: Se inicializó el proyecto Spring Boot, se implementó el primer endpoint REST del MVP, se incorporaron validaciones con Bean Validation y la documentación interactiva Swagger/OpenAPI. Leandro Moreno fue el autor de la base del proyecto, del endpoint y realizó de los merges de integración. Alan Federico Cabrera aportó la versión V2 con validaciones, Swagger y realizó de los merges de integración.

---

## 🔀 Pull Requests

### PR #4 – `feature/setup-spring-boot-base`
- **Autor:** Leandro Moreno
- **Mergeado por:** Leandro Moreno (24/07/2026)
- **Enlace:** [PR #4](https://github.com/No-Country-simulation/G9-LATAM-TEAM-09/pull/4)

**"Inicialización del Proyecto V1":**

- Creación del proyecto base del back-end en `backend/analisis-energetico-api/` con la estructura estándar de Maven y artefacto `com.energiai:analisis-energetico-api`.
- Configuración de tecnologías en `pom.xml`:

| Componente | Versión |
|------------|---------|
| Spring Boot (parent) | 4.0.7 |
| Java | 17 |
| Gestor de dependencias | Maven |

| Dependencia | Uso |
|-------------|-----|
| `spring-boot-starter-webmvc` | Framework web MVC para construir endpoints REST. |
| `spring-boot-starter-data-jpa` | Acceso a datos con JPA/Hibernate. |
| `spring-boot-starter-validation` | Bean Validation para validar DTOs. |
| `spring-boot-h2console` | Consola web de H2 accesible desde el navegador. |
| `H2 (runtime)` | Base de datos en memoria para desarrollo y pruebas. |
| `Lombok` | Reduce código repetitivo (getters, builders, etc.). |
| `springdoc-openapi-starter-webmvc-ui` (v3.0.2) | Documentación interactiva Swagger UI / OpenAPI 3.0. |
| `spring-boot-starter-data-jpa-test` | Testing de la capa de acceso a datos JPA. |
| `spring-boot-starter-webmvc-test` | Testing de controllers/web MVC (MockMvc). |

- Clase principal `AnalisisEnergeticoApiApplication.java` (`@SpringBootApplication`).

### PR #5 – `feature/energy-controller-endpoint`
- **Autor:** Leandro Moreno
- **Mergeado por:** Leandro Moreno (24/07/2026)
- **Enlace:** [PR #5](https://github.com/No-Country-simulation/G9-LATAM-TEAM-09/pull/5)

**"implementación de EndPoint":**

- Implementación del endpoint base del dominio:

```http
POST /api/v1/analisis-energetico
```

- Implementación de ("/test") para asegurar que Spring Boot se ejecuta correctamente.
- Clases involucradas: `AnalisisEnergeticoController.java`
- Anotaciones: `@RestController` `@RequestMapping` `@GetMapping`

### PR #6 – `feature/dto-validation`
- **Autor:** Alan Federico Cabrera
- **Mergeado por:** Alan Federico Cabrera (24/07/2026)
- **Enlace:** [PR #6](https://github.com/No-Country-simulation/G9-LATAM-TEAM-09/pull/6)

**"V2, Validaciones, SWAGGER, openAI, etc":**

- **Bean Validation** en los DTO de entrada (`@Valid` en el controller).
- **Documentación interactiva** con Swagger UI / OpenAPI 3.0 (springdoc-openapi).
- Elimina la implementación de ("/test") y anotación `@GetMapping`
- Recibe los datos de consumo, los procesa de forma provicional y devuelve clasificación, costo estimado y recomendaciones en formato JSON.
- **Clases involucradas:**
  - `AnalisisEnergeticoController.java`
  - `AnalisisEnergeticoService.java`
  - `DatosErrorCampo.java`
  - `DatosErrorRespuesta.java`
  - `DatosRegistroAnalisis.java`
  - `DatosRegistroConsumo.java`
  - `GlobalExceptionHandler`
  - `RecursoNoEncontradoException.java`
  - `AnalisisEnergeticoApiApplicationTests.java`
  - `GlobalExceptionHandlerTest.java`
- **Anotaciones:**
  - `@Tag`
  - `@Autowired`
  - `@Operation`
  - `@ApiResponses`
  - `@PostMapping`
  - `@Schema`
  - `@JsonInclude`
  - `@Builder`
  - `@NotNull`
  - `@Positive`
  - `@Min`
  - `@Max`
  - `@NotBlank`
  - `@RestControllerAdvice`
  - `@ExceptionHandler`
  - `@Service`
  - `@SpringBootTest`
  - `@Test`
  - `@BeforeEach`

---

## 📋 Detalle de clases y anotaciones

### Clases involucradas

| PR | Clase | Propósito |
|----|-------|-----------|
| #5 | `AnalisisEnergeticoController.java` | Controller del endpoint `POST /api/v1/analisis-energetico` (V1, `/test`). |
| #6 | `AnalisisEnergeticoController.java` | Controller V2: `@Valid`, validaciones y Swagger. |
| #6 | `AnalisisEnergeticoService.java` | Lógica de negocio: procesa consumo → clasificación, costo y recomendaciones. |
| #6 | `DatosErrorCampo.java` | DTO de error por campo. |
| #6 | `DatosErrorRespuesta.java` | DTO de respuesta de error. |
| #6 | `DatosRegistroAnalisis.java` | DTO de respuesta del análisis. |
| #6 | `DatosRegistroConsumo.java` | DTO de entrada con datos de consumo. |
| #6 | `GlobalExceptionHandler` | Manejador global de excepciones (`@RestControllerAdvice`). |
| #6 | `RecursoNoEncontradoException.java` | Excepción de recurso no encontrado. |
| #6 | `AnalisisEnergeticoApiApplicationTests.java` | Test de integración del API. |
| #6 | `GlobalExceptionHandlerTest.java` | Test del manejador global. |

### Anotaciones

| PR | Anotación | Uso |
|----|-----------|-----|
| #5 | `@RestController` | Define el controller REST. |
| #5 | `@RequestMapping` | Mapea la ruta base `/api/v1/analisis-energetico`. |
| #5 | `@GetMapping` | Endpoint GET `/test` (eliminado en V2). |
| #6 | `@Tag` | Etiqueta de Swagger/OpenAPI. |
| #6 | `@Autowired` | Inyección de dependencias. |
| #6 | `@Operation` | Documenta la operación en OpenAPI. |
| #6 | `@ApiResponses` | Documenta respuestas posibles. |
| #6 | `@PostMapping` | Endpoint POST del análisis. |
| #6 | `@Schema` | Describe esquemas de los DTO. |
| #6 | `@JsonInclude` | Controla inclusión de campos JSON. |
| #6 | `@Builder` | Patrón builder (Lombok). |
| #6 | `@NotNull` | Validación de campo obligatorio. |
| #6 | `@Positive` | Validación de valor positivo. |
| #6 | `@Min` | Valor mínimo permitido. |
| #6 | `@Max` | Valor máximo permitido. |
| #6 | `@NotBlank` | Cadena no vacía. |
| #6 | `@RestControllerAdvice` | Manejador global de excepciones. |
| #6 | `@ExceptionHandler` | Maneja excepciones específicas. |
| #6 | `@Service` | Capa de servicio. |
| #6 | `@SpringBootTest` | Test de integración Spring. |
| #6 | `@Test` | Método de test. |
| #6 | `@BeforeEach` | Setup previo a cada test. |

## 👥 Commits de la semana

| Autor | Commits | Aportes principales | Merges |
|-------|:-------:|---------------------|--------|
| Leandro Moreno | 2 | Inicialización del proyecto V1 y primer endpoint. | Merges de integración (PR #4 y #5). |
| Alan Federico Cabrera | 1 | V2: validaciones, Swagger/OpenAPI y exploración ML. | Merges de integración (PR #6). |
---

## 🧭 Estado final

**Logrado:** proyecto Spring Boot 4.0.7 inicializado, endpoint `POST /api/v1/analisis-energetico` funcional, validaciones de DTO, Test y Swagger/OpenAPI incorporados.
