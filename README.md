<div align="center">

# ⚡ EnergiAI – Inteligencia para el Consumo Energético

### Hackathon ONE — G9 | Alura + Oracle | LATAM

![Java](https://img.shields.io/badge/Java-17+-ED8B00?style=for-the-badge&logo=openjdk&logoColor=white)
![Spring Boot](https://img.shields.io/badge/Spring_Boot-3.x-6DB33F?style=for-the-badge&logo=springboot&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Machine Learning](https://img.shields.io/badge/Data_Science-ML-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![OCI](https://img.shields.io/badge/Oracle_Cloud-OCI-F80000?style=for-the-badge&logo=oracle&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-MVP_En_Desarrollo-yellow?style=for-the-badge)

</div>

---

## 📌 Descripción del Proyecto

### El Problema

Millones de hogares y pequeñas empresas reciben mensualmente facturas de energía elevadas **sin entender qué hábitos las generan**. La falta de visibilidad sobre el propio consumo eléctrico impide tomar decisiones informadas, genera desperdicios evitables y aumenta innecesariamente el gasto familiar y operativo.

### La Solución

**Analizador Inteligente de Eficiencia Energética** es un MVP que convierte datos crudos de consumo eléctrico en información accionable. La solución recibe información del consumo de una vivienda o pequeño establecimiento (kWh mensuales, horarios de uso, cantidad de equipos, tipo de inmueble) y entrega:

- 🔍 **Clasificación del perfil energético** mediante Machine Learning (`Eficiente`, `Moderado`, `Ineficiente`).
- 💡 **Recomendaciones personalizadas** para reducir desperdicios y adoptar hábitos más sostenibles.
- 💰 **Estimación del costo mensual** basada en la tarifa de referencia estándar (**$0.75 / kWh**).
- 📊 Resultados entregados vía **API REST en formato JSON**, listos para integrarse con cualquier sistema o aplicación front-end.

---

## 🛠️ Stack Tecnológico y Estrategia de Integración

El proyecto se divide en dos áreas principales: Backend (Java) y Data Science (Python). 

| Capa | Tecnología | Rol |
|------|-----------|-----|
| **Back-End** | Java 17+ / Spring Boot 4.0.7 | API REST principal, orquestación y validaciones. |
| **Data Science** | Python 3.10+ / Pandas / Scikit-Learn | Análisis de datos (EDA), entrenamiento del modelo ML y generación de reglas. |
| **Infraestructura** | Oracle Cloud (OCI) + Docker | Almacenamiento (Object Storage) y Despliegue (Compute). |

### Alternativas de Integración (Python ↔ Java)
El equipo decidirá entre las siguientes opciones para integrar el modelo ML con la API:
- **Alternativa A (Microservicios):** Desplegar el modelo Python como una API independiente usando **FastAPI** o **Flask** (comunicación vía HTTP interno).
- **Alternativa B (Embebido):** Exportar el modelo entrenado a formato **ONNX** y ejecutarlo directamente dentro de la aplicación Spring Boot en Java.

---

## 📐 Arquitectura de la Solución (MVP)

```text
[Cliente / App / Postman]
       │
       ▼ (POST /api/v1/analisis-energetico)
       │
┌───────────────────────────────────────────┐
│        API Spring Boot (Backend)          │
│  - Validaciones de entrada                │
│  - Orquestación de la respuesta           │
└──────────────────┬────────────────────────┘
                   │
                   ▼ (Consulta al Modelo ML)
                   │
┌───────────────────────────────────────────┐
│          Módulo Machine Learning          │
│  (Vía API FastAPI o Modelo ONNX Embebido) │
│  - Clasificación de eficiencia            │
│  - Generación de recomendaciones          │
└──────────────────┬────────────────────────┘
                   │
                   ▼ (Lectura/Escritura)
                   │
┌───────────────────────────────────────────┐
│       OCI (Oracle Cloud Infrastructure)   │
│  - Object Storage (Datasets / Modelos)    │
│  - OCI Compute (Despliegue Docker)        │
└───────────────────────────────────────────┘
```

---

## 🔌 Contrato de Datos Unificado (API REST)

### Endpoint Principal

```
POST /api/v1/analisis-energetico
Content-Type: application/json
```

### Request Body

```json
{
  "consumo_kwh": 420.0,
  "uso_horario_pico": true,
  "cantidad_equipos": 10,
  "tipo_inmueble": "Casa",
  "horas_alto_consumo": 8
}
```

### Response Body (HTTP 200 OK)

```json
{
  "categoria": "Ineficiente",
  "probabilidad": 0.81,
  "costo_estimado_mensual": 315.00,
  "recomendaciones": [
    "Reducir el uso de equipos durante los horarios pico",
    "Evaluar equipos con alto consumo energético",
    "Distribuir las actividades de mayor consumo a lo largo del día"
  ]
}
```

---

## 📋 Validaciones del DTO (Reglas de Entrada)

| Campo | Tipo | Obligatorio | Restricciones |
|-------|------|:-----------:|---------------|
| `consumo_kwh` | `Double` | ✅ | Debe ser **> 0** |
| `uso_horario_pico` | `Boolean` | ✅ | `true` o `false` |
| `cantidad_equipos` | `Integer` | ✅ | Debe ser **≥ 1** |
| `tipo_inmueble` | `String` | ✅ | Solo valores: `Casa`, `Departamento`, `Comercio`, `Pyme` |
| `horas_alto_consumo` | `Integer` | ✅ | Rango: **0 – 24** |

---

## 🌐 Configuración de Puertos y Red

| Servicio | Puerto Local | Puerto Producción (OCI) |
|----------|:------------:|:-----------------------:|
| API Spring Boot | `8080` | `443` (HTTPS) vía proxy inverso |
| Frontend (en desarrollo) | `3000` | raíz del dominio vía proxy (same-origin) |
| Microservicio ML (Opcional) | `8000` | interno (solo red Docker) |

---

## 📖 Documentación Interactiva de la API

Una vez levantado el back-end, la documentación estará accesible en:

| Herramienta | URL Local |
|-------------|-----------|
| **Swagger UI** (interfaz visual) | `http://localhost:8080/swagger-ui.html` |
| **OpenAPI JSON** (spec completa) | `http://localhost:8080/v3/api-docs` |
| **Health check** (Actuator) | `http://localhost:8080/actuator/health` |

> 💡 **Nota sobre buenas prácticas en Producción:** 
> Durante la fase de desarrollo local se mantiene la ruta estándar de Swagger UI (`/swagger-ui.html`). Al momento de desplegar en producción, como buena práctica, se puede configurar una ruta más limpia (ej. `/docs`), proteger el acceso mediante autenticación o incluso deshabilitar Swagger completamente por motivos de seguridad.

---

## 🌿 Estrategia de Ramas (Git Workflow)

```text
main          ◀── Producción / Evaluación Hackathon (protegida)
  │
  └── develop ◀── Rama base de integración (merges vía PR)
        │
        ├── feature/setup-spring-boot-base
        ├── feature/energy-controller-endpoint
        ├── feature/dto-validation
        ├── feature/python-eda-notebook
        ├── feature/ml-model-training
        ├── feature/fastapi-inference-service
        ├── feature/docker-compose-integration
        ├── feature/docs
        └── feature/oci-object-storage-config
```

> [!IMPORTANT]
> 1. **Nunca hacer push directo a `main`** — Solo mediante Pull Request desde `develop`.
> 2. **Nunca hacer push directo a `develop`** — Solo mediante Pull Request desde `feature/*`.

---

## 🚀 Instrucciones de Ejecución Local

### Prerrequisitos
- Java 17+ y Maven 3.8+
- Python 3.10+
- Docker Desktop

### 1. Clonar el repositorio
```bash
git clone https://github.com/No-Country-simulation/G9-LATAM-TEAM-09.git
cd G9-LATAM-TEAM-09
```

### 2. Ejecutar con Docker Compose (Recomendado)
Para levantar todos los servicios de forma orquestada:
```bash
docker compose up --build -d
```

### 3. Ejecutar servicios individualmente (Modo Desarrollo)
**Para el Backend (Java):**
```bash
cd backend
./mvnw spring-boot:run
```
**Para el servicio de Machine Learning (Si se usa la Alternativa A):**
```bash
cd data-science
python -m venv .venv
# Activar el entorno virtual (depende del OS)
pip install -r requirements.txt
uvicorn src.api.main:app --reload --port 8000
```

---

## 💡 Ejemplos de Uso

### Ejemplo 1 — Perfil Eficiente
```json
{
  "consumo_kwh": 120.0,
  "uso_horario_pico": false,
  "cantidad_equipos": 4,
  "tipo_inmueble": "Departamento",
  "horas_alto_consumo": 2
}
```

### Ejemplo 2 — Perfil Ineficiente
```json
{
  "consumo_kwh": 420.0,
  "uso_horario_pico": true,
  "cantidad_equipos": 10,
  "tipo_inmueble": "Casa",
  "horas_alto_consumo": 8
}
```

---

## ☁️ Integración con OCI (Oracle Cloud Infrastructure)

| Servicio OCI | Uso en el Proyecto | Estado |
|-------------|-------------------|--------|
| **OCI Compute** | VM ARM64 con los dos ambientes (producción y staging) detrás de proxy con HTTPS. | ✅ Desplegado |
| **OCI Object Storage** | Almacenamiento del modelo serializado (`.pkl` / `.onnx`) y datasets de entrenamiento. | 🟡 Bucket + PAR listos |

Detalle completo de la infraestructura (red, VM, dominios, seguridad, runbook): [`docs/oci-cloud/`](docs/oci-cloud/README.md).

### Configuración del Object Storage

> ✅ **Bucket y región confirmados (Sprint 2)** — ver evidencia completa en [`docs/oci-cloud/README.md`](./docs/oci-cloud/README.md).
> Namespace y archivo de autenticación se configuran por entorno al momento del despliegue (a cargo de Lautaro/Sergio) y no se publican en este ejemplo.

```yaml
# application.yml (Spring Boot) - Ejemplo
oci:
  object-storage:
    namespace: [POR CONFIGURAR]
    bucket-name: g9-energy-test-bucket
    region: sa-santiago-1 # Chile Central (Santiago)
  auth:
    config-file: [POR CONFIGURAR]
```

---

## 👥 Equipo G9 — LATAM TEAM 09

| Nombre | Rol | Área |
|--------|-----|------|
| **Constanza Albornoz** | Data Analyst | Data Science |
| **Leandro Ariel Moreno** | Backend Developer | Back-End Java |
| **Alan Federico Cabrera** | Backend Developer | Back-End Java |
| **Nahuel Rosas** | Data Scientist | Data Science / ML |
| **Marco Antonio Soto Bobadilla** | Project Manager | Gestión del Proyecto |
| **Randy Roco Mellado** | Data Engineer | Data Engineering / OCI |
| **Lautaro Sebastian Mambrin** | Full Stack Developer | Back-End + Front-End opcional |
| **Sergio Villena** | Software Engineer | Arquitectura / DevOps |

---

## 📄 Licencia

Este proyecto está bajo la licencia **MIT**. Ver el archivo `LICENSE` para más detalles.

---

<div align="center">

**Hackathon ONE — G9 LATAM TEAM 09**

*Alura + Oracle | 2026*

[![Proyecto Hackathon](https://img.shields.io/badge/Specs_Oficiales-Hackathon_ONE-F80000?style=flat-square&logo=oracle)](https://alura-es-cursos.github.io/proyectos-hackathon-g9-latam/)

</div>
