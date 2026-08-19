# Coleccion Postman — EnergiAI

Coleccion definitiva de testing para la API REST de EnergiAI.

## Archivos

| Archivo | Descripcion |
|---------|-------------|
| `EnergiAI.postman_collection.json` | Coleccion con 18 requests y aserciones automaticas |
| `EnergiAI.postman_environment.json` | Environment para desarrollo local (sin secretos) |

## Prerequisitos

- [Postman](https://www.postman.com/downloads/) v10.0 o superior
- Docker Desktop corriendo
- Stack levantado: `docker compose --profile local up -d --build`

## Importar

1. Abrir Postman.
2. **Collection:** `File > Import` > seleccionar `EnergiAI.postman_collection.json`.
3. **Environment:** `File > Import` > seleccionar `EnergiAI.postman_environment.json`.
4. Seleccionar el environment `EnergiAI — Local Development` en el dropdown superior derecho.

## Ejecutar

### Todas las carpetas (Collection Runner)

1. `Runner` (Ctrl+Shift+R) > seleccionar la coleccion.
2. Seleccionar el environment `EnergiAI — Local Development`.
3. `Run EnergiAI — Analisis Energetico`.

### Solo requests automaticos (sin setup manual)

Ejecutar en orden:
1. `Health Checks` (3 requests)
2. `Happy Path — 3 Perfiles Energeticos` (3 requests)
3. `Validaciones HTTP 400` (5 requests)
4. `Recurso No Encontrado HTTP 404` (1 request)
5. `Contract Validation — ML Service Directo` (3 requests)

Total automaticos: **15 requests** que pasan sin intervencion manual.

### Requests que requieren setup manual

| Carpeta | Request | Que hacer antes | Restablecer |
|---------|---------|-----------------|-------------|
| Respuesta Invalida de ML 502 | ML retorna respuesta no-JSON | Configurar proxy (mitmproxy) que intercepte backend->ML y retorne HTML | Detener proxy |
| ML No Disponible 503 | ML apagado | `docker stop ml-service` | `docker start ml-service` |
| Timeout / Servicio ML Lento | ML timeout | Configurar `ml.service.read-timeout=1000` en backend + agregar `sleep(5)` en ML inference | Restaurar configuracion original |

## Matriz de Resultados Esperados

### Health Checks

| # | Request | Status | Aserciones clave |
|---|---------|--------|------------------|
| 1 | Backend Health | `200` | `status: "UP"` |
| 2 | ML Health | `200` | `status: "healthy"` |
| 3 | ML Root Info | `200` | `service: "EnergiAI"`, `status: "ok"` |

### Happy Path — 3 Perfiles Energeticos

| # | Request | Status | Aserciones clave |
|---|---------|--------|------------------|
| 4 | Perfil Eficiente | `200` | `categoria: "Eficiente"`, `probabilidad` [0-1], `costo >= 0`, `recomendaciones` array no vacio, `id` UUID |
| 5 | Perfil Moderado | `200` | `categoria: "Moderado"`, mismas aserciones de estructura y rangos |
| 6 | Perfil Ineficiente | `200` | `categoria: "Ineficiente"`, mismas aserciones de estructura y rangos |

**Nota:** La clasificacion exacta (Eficiente/Moderado/Ineficiente) depende del modelo ML entrenado. Los tests validan que `categoria` sea uno de esos tres valores.

### Validaciones HTTP 400

| # | Request | Status | Aserciones clave |
|---|---------|--------|------------------|
| 7 | Campo nulo (consumo_kwh faltante) | `400` | `error: "BAD_REQUEST"`, `detalles` array con `campo` y `mensaje` |
| 8 | Fuera de rango (consumo_kwh=1500) | `400` | `error: "BAD_REQUEST"`, `detalles` array |
| 9 | Enum invalido (tipo_inmueble="CasaEstilo") | `400` | `error: "BAD_REQUEST"` |
| 10 | JSON malformado | `400` | `error: "BAD_REQUEST"` |
| 11 | Body vacio | `400` | `error: "BAD_REQUEST"` |

### Recurso No Encontrado HTTP 404

| # | Request | Status | Aserciones clave |
|---|---------|--------|------------------|
| 12 | GET con UUID inexistente | `404` | `error: "NOT_FOUND"`, `mensaje` no vacio |

### Respuesta Invalida de ML HTTP 502

| # | Request | Status | Aserciones clave | Setup |
|---|---------|--------|------------------|-------|
| 13 | ML retorna no-JSON | `502` | `error: "BAD_GATEWAY"` | Requiere proxy que inyecte respuesta invalida |

### ML No Disponible HTTP 503

| # | Request | Status | Aserciones clave | Setup |
|---|---------|--------|------------------|-------|
| 14 | ML apagado | `503` | `error: "SERVICE_UNAVAILABLE"` | `docker stop ml-service` |

### Timeout / Servicio ML Lento

| # | Request | Status | Aserciones clave | Setup |
|---|---------|--------|------------------|-------|
| 15 | ML timeout | `503` | `error: "SERVICE_UNAVAILABLE"` | Configurar timeout bajo + latencia artificial |

### Contract Validation — ML Service Directo

| # | Request | Status | Aserciones clave |
|---|---------|--------|------------------|
| 16 | Happy path ML directo | `200` | `categoria`, `probabilidad`, `costo_estimado_mensual`, `recomendaciones` (sin `id` ni `fecha`) |
| 17 | Validacion Pydantic 422 | `422` | `detail` array con `loc`, `msg`, `type` |
| 18 | ML Health detallado | `200` | `status: "healthy"` |

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

## Variables del Environment

| Variable | Default | Descripcion |
|----------|---------|-------------|
| `baseUrl` | `http://localhost:8080` | URL del backend Spring Boot |
| `mlUrl` | `http://localhost:8000` | URL del ML service FastAPI |

> No contiene secretos, tokens ni URLs de produccion.

## Troubleshooting

| Problema | Solucion |
|----------|----------|
| `Connection refused` en health checks | Verificar que Docker este corriendo: `docker compose ps` |
| 503 en Happy Path | Verificar que el ML service este healthy: `docker logs ml-service` |
| 400 inesperado | Revisar el body — todos los campos obligatorios deben estar presentes |
| 502 en tests automaticos | El ML retorno una respuesta inesperada — revisar `docker logs ml-service` |
| Collection no importa | Verificar que Postman este actualizado a v10 0 superior |
