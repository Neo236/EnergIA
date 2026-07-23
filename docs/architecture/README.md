# 🏛️ Documentación de Arquitectura de la Solución

## 📌 Resumen
Diseño general de la solución y flujo de datos entre servicios.

---

## 📐 Diagrama de Arquitectura (MVP)

```text
[Cliente / Postman]
       │
       ▼ (POST /api/v1/analisis-energetico)
┌───────────────────────────────────────────┐
│        API Spring Boot (Backend)          │
└──────────────────┬────────────────────────┘
                   │ (HTTP / JSON)
                   ▼
┌───────────────────────────────────────────┐
│       Módulo ML (FastAPI / ONNX)          │
└──────────────────┬────────────────────────┘
                   │ (Object Storage)
                   ▼
┌───────────────────────────────────────────┐
│       OCI (Oracle Cloud Infrastructure)   │
└───────────────────────────────────────────┘
```

---

## 🖼️ Archivos y Capturas (`assets/`)
Guarde diagramas C4 o imágenes explicativas en `docs/architecture/assets/`.
