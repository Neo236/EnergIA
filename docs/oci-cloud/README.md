# ☁️ Documentación de Oracle Cloud Infrastructure (OCI)

## 📌 Resumen
Guía y registro de la configuración e integración de los servicios de Oracle Cloud para el almacenamiento de modelos y despliegue del proyecto.

---

## 🛠️ Servicios OCI Utilizados

| Servicio OCI | Uso / Propósito | Estado |
|--------------|------------------|--------|
| **OCI Object Storage** | Almacenamiento del dataset de entrenamiento y modelo `.pkl` / `.onnx`. | Evidencia parcial registrada (Sprint 2) |
| **OCI Compute** | Instancia de Máquina Virtual para el despliegue Docker en producción. | Arquitectura confirmada (**ARM**) — despliegue aún pendiente |

---

## 📦 Evidencia registrada — OCI Object Storage (Sprint 2)

| Campo | Valor |
|-------|-------|
| Bucket | `g9-energy-test-bucket` |
| Compartimento | `sergiovillenavergara (raíz)` |
| Región (consola) | Chile Central (Santiago) |
| Visibilidad | Privado |
| Nivel de almacenamiento | Estándar |
| Objeto de prueba | `prueba_consumo_electrico.csv` |
| Tamaño del objeto | 149 bytes |
| Content-Type | `text/csv` |
| Última modificación | 21 jul 2026, 19:43 UTC |

> No se registran credenciales, claves de API ni archivos de configuración de autenticación en esta documentación.

### Capturas

| Captura | Descripción |
|---------|-------------|
| ![Bucket creado](./assets/01-oci-object-storage-bucket-creado.png) | Consola OCI → Buckets: bucket `g9-energy-test-bucket` creado en el compartimento raíz, región Chile Central (Santiago). |
| ![Carga de objeto](./assets/02-oci-object-storage-carga-objeto.png) | Carga del archivo de prueba `prueba_consumo_electrico.csv` al 100%, estado "Listo". |
| ![Bucket con objeto listado](./assets/03-oci-object-storage-bucket-listado-objetos.png) | Pestaña "Objetos" del bucket mostrando el archivo cargado (149 bytes). |
| ![Detalle del objeto](./assets/04-oci-object-storage-objeto-detalle.png) | Detalles del objeto: cabeceras de respuesta (Content-Type, ETag, hash MD5) y vista previa del contenido CSV. |

---

## 🔗 Acceso de equipo — Pre-Authenticated Request (PAR)

Para dar acceso al bucket sin compartir credenciales individuales de OCI, se creó una **Pre-Authenticated Request (PAR)** — "solicitud autenticada previamente" en la consola en español.

| Campo | Valor |
|-------|-------|
| Nombre de la PAR | `acceso-equipo-desarrollo` |
| Destino | Bucket completo (`g9-energy-test-bucket`) |
| Tipo de acceso | Lectura y escritura de objetos |
| Listado de objetos | Activado |
| Caducidad | 31/12/2026, 20:00 UTC |

> ⚠️ La URL de la PAR funciona como credencial de acceso (bearer token) y **no se publica aquí ni en ninguna captura** — quien la necesite debe solicitarla directamente al integrante que la generó.

### Capturas

| Captura | Descripción |
|---------|-------------|
| ![Crear solicitud PAR](./assets/par-oci-object-storage/01-oci-par-crear-solicitud.png) | Formulario "Crear solicitud autenticada previamente": destino Bucket, acceso de lectura/escritura, listado de objetos activado, caducidad 31/12/2026. |
| ![Detalle de la PAR](./assets/par-oci-object-storage/02-oci-par-detalle-url.png) | Detalles de la PAR creada (`acceso-equipo-desarrollo`); la URL fue tapada intencionalmente antes de guardar la captura. |
| ![Prueba del enlace](./assets/par-oci-object-storage/03-oci-par-prueba-enlace.png) | Respuesta JSON al consultar la PAR, confirmando que el enlace lista correctamente el objeto `prueba_consumo_electrico.csv`. |

### Procedimiento reproducible (PAR)

1. En el bucket del proyecto, ir a **Solicitudes autenticadas previamente → Crear solicitud autenticada previamente**.
2. Definir un nombre descriptivo (ej. `acceso-equipo-desarrollo`), destino (Bucket / Objeto / Objetos con prefijo), tipo de acceso y fecha de caducidad.
3. Activar **listado de objetos** si el equipo necesita ver qué contiene el bucket a través del enlace.
4. Copiar la URL generada **una sola vez** (no se vuelve a mostrar) y compartirla por un canal seguro (nunca en el repositorio ni en capturas públicas).
5. Verificar que el enlace funciona consultándolo y confirmando que devuelve el listado/objeto esperado.

---

## 🔁 Procedimiento reproducible — Carga de objetos

Pasos para que cualquier integrante del equipo repita la prueba de Object Storage:

1. Ingresar a la consola de OCI con una cuenta con acceso al compartimento del proyecto.
2. Ir a **Almacenamiento → Almacenamiento de objetos y de archivo → Buckets**.
3. Verificar que exista el bucket `g9-energy-test-bucket` (o crear uno nuevo con **Crear bucket** si no existe).
4. Dentro del bucket, ir a la pestaña **Objetos** y usar **Cargar objetos** para subir un archivo de prueba.
5. Confirmar que el archivo aparece en la lista de **Objetos** con su tamaño y fecha de modificación.
6. Abrir el archivo y revisar **Detalles de objeto** para confirmar cabeceras (Content-Type, ETag) y contenido, sin exponer credenciales.
7. Adjuntar capturas de cada paso en `docs/oci-cloud/assets/` siguiendo la convención `NN-oci-object-storage-<descripcion>.png`.

---

## ✅ Resuelto en Sprint 2

- **Arquitectura de la instancia Compute confirmada como ARM** (no x86). Como consecuencia, se actualizaron las imágenes base del `Dockerfile` del backend a variantes multi-arquitectura (`maven:3.9-eclipse-temurin-17`, `eclipse-temurin:17-jre`) que sí publican `arm64`. Ver [`backend/Dockerfile`](../../backend/Dockerfile) y [`docs/backend/README.md`](../backend/README.md).
- **Acceso del equipo al bucket sin compartir credenciales de OCI**: resuelto mediante una Pre-Authenticated Request (PAR) — ver sección [Acceso de equipo — Pre-Authenticated Request (PAR)](#-acceso-de-equipo--pre-authenticated-request-par) arriba.
- **Acceso de consola/IAM a OCI definido y acotado**: el equipo decidió restringir el acceso directo a la consola de OCI (y a la instancia Compute de producción) a **Lautaro Mambrin** (Full Stack Developer, responsable de la instancia donde se despliega el proyecto) y **Sergio Villena** (Software Engineer, Arquitectura/DevOps). El resto del equipo accede al Object Storage mediante la PAR, sin necesidad de cuenta propia en la consola.

---

## 🖼️ Archivos y Capturas (`assets/`)
Guarde las capturas de la consola de OCI, configuración de buckets y red en `docs/oci-cloud/assets/`, siguiendo la convención `NN-oci-<servicio>-<descripcion>.png` usada arriba. Para procedimientos con varias capturas, agrupe en una subcarpeta kebab-case (ej. `assets/par-oci-object-storage/`).
