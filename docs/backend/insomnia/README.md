# Coleccion Insomnia — EnergIA

Coleccion de testing para la API REST de EnergIA usando [Insomnia](https://insomnia.rest/). Incluye 13 requests con scripts de validacion automatica (aserciones) que cubren happy paths, validaciones de error y escenarios de fallo del servicio ML.

## Archivos

| Archivo | Descripcion |
|---------|-------------|
| `Insomnia_2026-08-18-10-13-12.yaml` | Coleccion exportada con 13 requests y scripts `afterResponse` |

## Prerequisitos

- [Insomnia](https://insomnia.rest/download) v2023.5 o superior
- Docker Desktop corriendo
- Stack levantado: `docker compose --profile local up -d --build`

## Importar

1. Abrir Insomnia.
2. `File > Import` > seleccionar `Insomnia_2026-08-18-10-13-12.yaml`.
3. La coleccion aparecera como **Hackathon** en el sidebar.

## Ejecutar

### Todas las requests (secuencia recomendada)

Ejecutar en orden:

1. `Health de Backend` (1 request)
2. `Health de ML` (1 request)
3. `Perfil Eficiente` (1 request)
4. `Perfil Moderado` (1 request)
5. `Perfil Ineficiente` (1 request)
6. `Validaciones HTTP 400` (1 request)
7. `Recurso No Encontrado HTTP 404` (1 request)
8. `Respuesta Invalida de ML HTTP 502` (1 request)
9. `ML No Disponible HTTP 503` (1 request)
10. `ML Detenido` (1 request)
11. `Timeout` (1 request)
12. `Validar Estructura y Rangos` (1 request)
13. `Happy Path` (1 request)

Total: **13 requests** con aserciones automaticas.

### Requests que pasan sin setup manual

| # | Request | Status esperado |
|---|---------|-----------------|
| 1 | Health de Backend | `200` |
| 2 | Health de ML | `200` |
| 3 | Perfil Eficiente | `200` |
| 4 | Perfil Moderado | `200` |
| 5 | Perfil Ineficiente | `200` |
| 6 | Validaciones HTTP 400 | `400` |
| 7 | Recurso No Encontrado HTTP 404 | `404` |
| 8 | Validar Estructura y Rangos | `200` |
| 9 | Happy Path | `200` |

Total automaticos: **9 requests** que pasan sin intervencion manual.

### Requests que requieren setup manual

| Request | Que hacer antes | Restablecer |
|---------|-----------------|-------------|
| Respuesta Invalida de ML 502 | Configurar proxy (mitmproxy) que intercepte backend->ML y retorne HTML | Detener proxy |
| ML No Disponible HTTP 503 | `docker stop ml-service` | `docker start ml-service` |
| ML Detenido | `docker stop ml-service` | `docker start ml-service` |
| Timeout | Configurar `ml.service.read-timeout=1000` en backend + agregar `sleep(5)` en ML inference | Restaurar configuracion original |

## Matriz de Resultados Esperados

### Health Checks

| # | Request | Status | Aserciones clave |
|---|---------|--------|------------------|
| 1 | Health de Backend | `200` | `status: "UP"` |
| 2 | Health de ML | `200` | `status: "healthy"` |

### Happy Path — 3 Perfiles Energeticos

| # | Request | Status | Aserciones clave |
|---|---------|--------|------------------|
| 3 | Perfil Eficiente | `200` | `categoria` presente, `recomendaciones` array, `probabilidad` [0-1], `costo_estimado_mensual` > 0 |
| 4 | Perfil Moderado | `200` | Mismas aserciones de estructura y rangos |
| 5 | Perfil Ineficiente | `200` | Mismas aserciones de estructura y rangos |

**Nota:** La clasificacion exacta (Eficiente/Moderado/Ineficiente) depende del modelo ML entrenado. Los tests validan que `categoria` y `recomendaciones` esten presentes.

### Validaciones HTTP 400

| # | Request | Status | Aserciones clave |
|---|---------|--------|------------------|
| 6 | Campo invalido (consumo_kwh=-9) | `400` | `status: 400`, `error: "BAD_REQUEST"`, `detalles` array no vacio |

### Recurso No Encontrado HTTP 404

| # | Request | Status | Aserciones clave |
|---|---------|--------|------------------|
| 7 | GET con UUID inexistente | `404` | `status: 404`, `error` presente |

### Respuesta Invalida de ML HTTP 502

| # | Request | Status | Aserciones clave | Setup |
|---|---------|--------|------------------|-------|
| 8 | ML retorna no-JSON | `502` | `status: 502`, `error: "BAD_GATEWAY"`, `mensaje` | Requiere proxy que inyecte respuesta invalida |

### ML No Disponible HTTP 503

| # | Request | Status | Aserciones clave | Setup |
|---|---------|--------|------------------|-------|
| 9 | ML apagado | `503` | `status: 503`, `error: "SERVICE_UNAVAILABLE"`, `mensaje` | `docker stop ml-service` |

### ML Detenido

| # | Request | Status | Aserciones clave | Setup |
|---|---------|--------|------------------|-------|
| 10 | ML detenido | `503` o `504` | `status`, `error`, `mensaje` | `docker stop ml-service` |

### Timeout / Servicio ML Lento

| # | Request | Status | Aserciones clave | Setup |
|---|---------|--------|------------------|-------|
| 11 | ML timeout | `502` | `status: 502`, `error: "BAD_GATEWAY"`, `mensaje` | Configurar timeout bajo + latencia artificial |

### Validar Estructura y Rangos

| # | Request | Status | Aserciones clave |
|---|---------|--------|------------------|
| 12 | Validacion exhaustiva | `200` | Campos obligatorios, valores numericos no negativos, categoria dentro de perfiles validos |

### Happy Path (General)

| # | Request | Status | Aserciones clave |
|---|---------|--------|------------------|
| 13 | Happy Path | `200` | Status 200, estructura completa, `probabilidad` [0-1], `costo_estimado_mensual` > 0, `recomendaciones` array no vacio |

## Estructura del Response Body (200 OK)

```json
{
  "id": "uuid-v7",
  "fecha": "2026-08-18T10:30:00",
  "categoria": "Eficiente | Moderado | Ineficiente",
  "probabilidad": 0.85,
  "costo_estimado_mensual": 150.00,
  "recomendaciones": ["...", "..."]
}
```

## Estructura del Error Body (400/404/502/503)

```json
{
  "timestamp": "2026-08-18T10:30:00",
  "status": 400,
  "error": "BAD_REQUEST",
  "mensaje": "Descripcion del error",
  "detalles": [
    { "campo": "nombre_campo", "mensaje": "descripcion del error" }
  ]
}
```

> `detalles` solo aparece en errores de validacion (400). En 404, 502 y 503 solo se retornan `timestamp`, `status`, `error` y `mensaje`.

## Variables / URLs

| Servicio | URL |
|----------|-----|
| Backend Spring Boot | `http://localhost:8080` |
| ML Service FastAPI | `http://localhost:8000` |

> **Nota:** A diferencia de la coleccion de Postman, las URLs en Insomnia estan hardcodeadas directamente en cada request. No se utilizan variables de entorno.

## Diferencias con la Coleccion Postman

| Aspecto | Insomnia | Postman |
|---------|----------|---------|
| Total requests | 13 | 18 |
| Variables de entorno | No usa (URLs hardcodeadas) | Si (`baseUrl`, `mlUrl`) |
| Scripts de validacion | `insomnia.test()` / `insomnia.expect()` | `pm.test()` / `pm.expect()` |
| Formato exportacion | YAML | JSON |

### Requests exclusivos de Postman (no presentes en Insomnia)

- JSON malformado (400)
- Body vacio (400)
- Fuera de rango consumo_kwh=1500 (400)
- Enum invalido tipo_inmueble (400)
- Contract Validation ML Service Directo (200, 422)
- ML Health detallado (200)

## Troubleshooting

| Problema | Solucion |
|----------|----------|
| `Connection refused` en health checks | Verificar que Docker este corriendo: `docker compose ps` |
| 503 en Happy Path | Verificar que el ML service este healthy: `docker logs ml-service` |
| 400 inesperado | Revisar el body — todos los campos obligatorios deben estar presentes |
| 502 en tests automaticos | El ML retorno una respuesta inesperada — revisar `docker logs ml-service` |
| Collection no importa | Verificar que Insomnia este actualizado a v2023.5+ |
| Scripts no ejecutan | Verificar que los scripts `afterResponse` esten habilitados en Settings > Core |
