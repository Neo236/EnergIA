# Storage

Capa de persistencia para los artefactos del pipeline ML (modelo entrenado,
dataset, métricas, CSV). Soporta dos backends:

| Backend | Default | Cuándo |
|---|---|---|
| `local` | ✓ (dev/CI) | Filesystem local; útil para tests y desarrollo sin bucket |
| `oci` |   | OCI Object Storage; producción |

Se selecciona con `STORAGE_BACKEND` (`local` o `oci`).

---

## Protocolo (`Storage`)

Toda la lógica de storage opera contra este contrato:

```python
class Storage(Protocol):
    def upload(self, local_path: str, remote_path: str) -> None: ...
    def download(self, remote_path: str, local_path: str) -> None: ...
    def exists(self, remote_path: str) -> bool: ...
    def delete(self, remote_path: str) -> None: ...
    def list_objects(self, prefix: str) -> list[str]: ...
    def head_info(self, remote_path: str) -> dict | None: ...
    def copy(self, src_remote: str, dst_remote: str) -> None: ...
```

| Método | Propósito |
|---|---|
| `upload` | Sube un archivo local al remoto (PUT) |
| `download` | Descarga un archivo remoto a local (GET) |
| `exists` | Chequea existencia (HEAD) |
| `delete` | Borra (DELETE) |
| `list_objects` | Lista objetos por prefijo (LIST) |
| `head_info` | Metadata sin body: `{etag, md5, size}` (HEAD) |
| `copy` | Copia server-side (sin transferir body) |

---

## Convención latest / archive

```
latest/database_beta.json
latest/database_beta.csv
latest/modelo_eficiencia_v1.joblib
latest/metricas_v1.joblib

archive/<UTC-timestamp>_<code-short>_<name>
archive/manifest.json
```

- `latest/<name>`: el archivo vigente, siempre sobreescrito en cada upload exitoso.
- `archive/`: snapshots inmutables de versiones anteriores.
- `manifest.json`: índice de qué `code_short` ya fue archivado por archivo.

---

## Code-version awareness

Cada entrenamiento registra un **code_version** (`git:<sha>` o `src:<hash>` fallback).
La rotación de `latest` → `archive` ocurre **solo si el code_version cambió**:

| Escenario | Acción |
|---|---|
| `latest/<name>` no existe | `uploaded` (sin archive) |
| Bytes idénticos a `latest/` | `skipped_identical` (0 ops en bucket) |
| Bytes diferentes, code ya archivado | `refreshed` (sobreescribe latest, sin archive) |
| Bytes diferentes, code nuevo | `rotated` (copy server-side + delete + upload) |

Resultado: el bucket solo acumula archives cuando **la lógica del modelo cambia**, no cuando solo cambia el seed.

---

## Optimizaciones de costo (OCI)

1. **`head_info` en vez de download+hash**: 1 HEAD (sin body transfer) en lugar de 1 GET con el body completo.
2. **Skip upload si MD5 coincide**: si el archivo local tiene el mismo MD5 que `latest/`, no se sube nada.
3. **`copy_object` para archivar**: server-side, sin transferir el body del archivo viejo.
4. **`manifest.json` en vez de `list_objects`**: 1 GET pequeño a `manifest.json` reemplaza 1 LIST que escala con la cantidad de archives.
5. **Compresión `joblib`**: `compress=3` reduce el modelo de ~12MB a ~4MB.
6. **Retry con backoff exponencial**: 3 intentos (1s/2s/4s con jitter ±20%) para errores transitorios; los 404 no se reintentan.

---

## Retry policy

Errores transitorios (red, 5xx) se reintentan hasta 3 veces con backoff
1s → 2s → 4s + jitter ±20%. Errores 4xx (incluyendo 404) NO se reintentan.

Implementado en `infrastructure/storage/retry.py`. Se aplica a TODAS las
operaciones OCI (`upload`, `download`, `exists`, `delete`, `list_objects`,
`head_info`, `copy`).

---

## Variables de entorno

| Variable | Default | Descripción |
|---|---|---|
| `STORAGE_BACKEND` | `local` | `local` o `oci` |
| `STORAGE_LOCAL_ROOT` | `.` | Root para LocalStorage |
| `OCI_NAMESPACE` | (requerido) | Namespace del bucket |
| `OCI_BUCKET` | `g9-energy-test-bucket` | Nombre del bucket |
| `OCI_REGION` | `sa-santiago-1` | Región OCI |
| `OCI_INSTANCE_PRINCIPAL` |   | `true` para auth sin credenciales |
| `OCI_CONFIG_FILE` |   | Path al config OCI alternativo |
| `OCI_USER_OCID` / `OCI_TENANCY_OCID` / `OCI_FINGERPRINT` |   | API key auth |
| `OCI_PRIVATE_KEY_PATH` o `OCI_PRIVATE_KEY_CONTENT` |   | Llave privada |

Si `STORAGE_BACKEND=oci` falta `OCI_NAMESPACE`, `get_storage()` lanza
`RuntimeError` claro. El pipeline (`train.py`) lo tolera y sigue sin bucket.

---

## Tests

```bash
# Unit (todos los backends, incluido OCI mockeado)
pytest tests/unit/test_storage.py -v

# Cobertura:
# - LocalStorage: upload/download/exists/delete/list/head_info/copy
# - OciBucketStorage (mocked): mismas + autenticacion instance_principal
# - TestManifest: read/write/versioning/tolerancia a corrupcion
# - TestUploadWithRotation: 6 escenarios (upload inicial, skip, refresh, rotate, etc.)
# - TestSafeUploadWithRotation: tolerancia a fallos
```

---

## CLI

```bash
# Entrenar y subir
python -m interfaces.cli.train

# Solo entrenar (sin tocar el bucket; util para CI/dev)
python -m interfaces.cli.train --dry-run
```