# Reproducibilidad del entrenamiento y evaluación

> Documento auditable. Cualquiera con este repo + Python 3.10 + Docker
> puede reproducir el modelo v1 desde cero y obtener los mismos hashes
> en metricas y predicciones (el hash del `.joblib` puede variar entre
> versiones de scikit-learn — ver §Gaps).

---

## ⚠️ Antes de empezar: orden importante

Para que la certificacion end-to-end pase, **el orden importa**:

1. **Primero entrenar** localmente (genera `.joblib`)
2. **Despues construir** la imagen Docker (la bake incluye los `.joblib`)
3. **Despues correr** el contenedor + verificar

Si construyes la imagen sin entrenar primero, el contenedor arranca con
un modelo backup entrenado in-situ (diferente SHA) y la comparacion de
identidad falla. Para orden completo ver TL;DR abajo.

---

## TL;DR — 5 pasos para regenerar + verificar

```bash
# (0) Entrenar localmente (genera .joblib + .sha256 sidecars)
cd data-science/raw
NUM_CLIENTES=2000 RANDOM_SEED=42 \
  OUTPUT_JSON_PATH=../data/database_beta.json \
  OUTPUT_CSV_PATH=../data/database_beta.csv \
  OUTPUT_MODEL_PATH=../data/modelo_eficiencia_v1.joblib \
  OUTPUT_METRICAS_PATH=../data/metricas_v1.joblib \
  python -m interfaces.cli.train --dry-run

# (1) Validar artefactos con el validador oficial del proyecto
NUM_CLIENTES=2000 \
  OUTPUT_JSON_PATH=../data/database_beta.json \
  OUTPUT_MODEL_PATH=../data/modelo_eficiencia_v1.joblib \
  OUTPUT_METRICAS_PATH=../data/metricas_v1.joblib \
  python -m interfaces.cli.validate

# (2) Verificar binding criptografico (los .joblib recien generados)
cd ../..
sha256sum -c data-science/data/MODEL_BINDING.sha256

# (3) Construir la imagen Docker (ahora incluye los .joblib del paso 0)
docker build \
  -t energiai-ml-service:$(git rev-parse --short HEAD) \
  -f data-science/Dockerfile \
  data-science/

# (4) Levantar servicio y correr verificacion automatizada end-to-end
IMAGE_TAG=$(git rev-parse --short HEAD)
docker run -d --rm --name ml-cert-$IMAGE_TAG \
  -p 127.0.0.1:8765:8000 \
  -e STORAGE_BACKEND=local \
  energiai-ml-service:$IMAGE_TAG
sleep 4
ML_SERVICE_URL=http://127.0.0.1:8765 \
  bash data-science/data/verify_certification.sh
docker stop ml-cert-$IMAGE_TAG
```

> **Importante**: en CI el checkout no tiene `.joblib` (gitignored via
> `*.joblib` y `data-science/.dockerignore`). El contenedor arranca
> con un modelo backup y la comparacion de SHA se skipea (ver
> `SKIP_LOCAL_FILES=1` en `.github/workflows/ci.yml`). Los checks de
> runtime (/health, /model-info, 3 perfiles golden) SI se ejecutan.

El script `verify_certification.sh` corre 12 checks cuando hay .joblib
locales, 5 checks en CI (SKIP los locales):

- 4 checks de integridad local: CHECKSUMS (2 archivos), MODEL_BINDING (4
  archivos, exit 0 + cada uno OK explicitamente)
- 1 check de /health
- 1 check de /model-info (path + loaded + size)
- 1 check de identidad SHA binding vs servido
- 3 checks de perfiles golden (Eficiente, Moderado, Ineficiente)

---

## Sobre la imagen Docker

- **Origen**: `data-science/Dockerfile` (versionado, base `python:3.10-slim`)
- **`.dockerignore`**: `data-science/.dockerignore` excluye `*.joblib`,
  `*.sha256`, `__pycache__/`, etc. Sin esto, los `.joblib` locales del
  dev se bakearian en la imagen cuando existen, y producirian un bake
  inconsistente con CI (donde no existen). El exclude garantiza que
  cualquier build (local o CI) arranque con los mismos datos: solo los
  archivos commiteados (`database_beta.{json,csv}`, `CHECKSUMS.sha256`,
  `MODEL_BINDING.sha256`, `METRICS.md`, etc.).
- **Tag por SHA**: `energiai-ml-service:$(git rev-parse --short HEAD)`
  hace la imagen inmutable. La misma imagen puede reconstruirse
  re-corriendo el comando con el mismo SHA de codigo.
- **Sin registry publico**: el repo no publica a Docker Hub / OCI /
  GHCR. Cada build se hace desde el Dockerfile local. Si en el futuro
  se publica, el tag por SHA permite referenciar builds exactos.
- **Para CI**: el job `data-science-ci` en `.github/workflows/ci.yml`
  hace este build + corre `verify_certification.sh` con
  `SKIP_LOCAL_FILES=1`. La ejecucion del CI es la fuente de verdad de
  "el modelo en este commit pasa la certificacion".

---

## Inputs canónicos (versionados en git)

| Archivo | SHA-256 |
|---|---:|
| `data-science/data/database_beta.json` | `74939597360ad75823e01654e18f1172b549c283a2a3aed201c2ee182257400b` |
| `data-science/data/database_beta.csv` | `92578ad71e64b2d6e37fdb083cd673a9d933c3c5f4c46239eaab7fde65f5a5f3` |

Verificables con:
```bash
cd data-science/data && sha256sum -c CHECKSUMS.sha256
```

## Outputs generados (gitignored + dockerignored)

| Archivo | SHA-256 (sklearn 1.9, dev local) | Cómo se produce |
|---|---:|---|
| `data-science/data/modelo_eficiencia_v1.joblib` | `2c06370a7e379d8a1b01e507bdccce3a64831ef23809d142333dca8f4560eba2` | `python -m interfaces.cli.train` |
| `data-science/data/metricas_v1.joblib` | `2945e5048db2ca39253ce788731ef86bccbd078cb78bbbde2223c5f8bcec56d9` | mismo train.py (split interno) |

> ⚠️ **Gaps**: el SHA del `.joblib` varia entre versiones de scikit-learn
> (el `random_state` interno del RF se serializa con detalle de version).
> El **contrato** es: misma accuracy (0.81), misma classification
> report, mismas predicciones para los 3 perfiles golden (ver §
> perfiles). Si sklearn cambia major version, los hashes cambian — eso
> se documenta en el siguiente commit de binding. Para validar el
> binding local, sklearn debe ser 1.9.x (el que genero estos hashes).
> Para CI con sklearn 1.6.1 (version del Dockerfile), el hash sera
> diferente y `SKIP_LOCAL_FILES=1` skipea la comparacion.

---

## Pipeline de entrenamiento

```
infrastructure/data/simulation.py
  ↓ NUM_CLIENTES=2000, RANDOM_SEED=42
  ↓ generar_dataset() -> DataFrame(2000, 13)
  ↓
domain/scoring.py
  ↓ calcular_iee_y_categoria() -> añade column 'categoria'
  ↓
application/training.py
  ↓ entrenar_y_guardar_modelo()
  ↓ ColumnTransformer(StandardScaler + OneHotEncoder) -> RandomForestClassifier
  ↓ train_test_split(test_size=0.2, random_state=42, stratify=y)
  ↓ .fit() + .predict() sobre X_test
  ↓
  ↓ save_model() -> data/modelo_eficiencia_v1.joblib
  ↓ save_metrics({"y_test":..., "y_pred":...}) -> data/metricas_v1.joblib
```

### Configuracion exacta

| Parametro | Valor | Fuente |
|---|---:|---|
| `NUM_CLIENTES` | 2000 | `infrastructure/config.py` |
| `RANDOM_SEED` | 42 | `infrastructure/config.py` (numpy global) |
| `RANDOM_STATE` (RF) | 42 | `application/training.py` |
| `n_estimators` | 200 | `application/training.py` |
| `test_size` | 0.2 | `application/training.py` |
| `stratify` | yes | `application/training.py` |
| `JOBLIB_COMPRESS` | 3 | `infrastructure/ml/model_storage.py` |

---

## Pipeline de evaluacion

```
infrastructure/validators/artifacts.py::validar_metricas()
  ↓ joblib.load('data/metricas_v1.joblib')
  ↓ classification_report(y_test, y_pred, zero_division=0)
  ↓ chequeo: f1-score(Eficiente) > 0.0
  ↓ retorna {'ok': True/False, 'msg': ..., 'reporte': ..., 'f1': ...}
```

O manualmente:
```python
import joblib
from sklearn.metrics import classification_report, accuracy_score, f1_score
m = joblib.load('data/metricas_v1.joblib')
print(classification_report(m['y_test'], m['y_pred'], zero_division=0))
print('Accuracy:', accuracy_score(m['y_test'], m['y_pred']))
print('Macro F1:', f1_score(m['y_test'], m['y_pred'], average='macro', zero_division=0))
```

---

## 3 perfiles canonicos (golden tests)

Para validar que el modelo entrenado se comporta como el esperado.
Mejor correrlos via `verify_certification.sh` (paso 4 del TL;DR).

Manualmente:

```bash
# Asume que ya entrenaste y construiste la imagen
docker run -d --rm --name ml-cert-test \
  -p 127.0.0.1:8765:8000 \
  -e STORAGE_BACKEND=local \
  energiai-ml-service:$(git rev-parse --short HEAD)
sleep 4

# Perfil 1: esperado Eficiente
curl -s -X POST localhost:8765/analisis-energetico \
  -H 'Content-Type: application/json' \
  -d '{"consumo_kwh":180,"tipo_inmueble":"Casa","horas_alto_consumo":4,
       "cantidad_equipos":10,"uso_horario_pico":false,"zona_fria":false,
       "fuente_calefaccion":"Solar","fuente_agua_caliente":"Solar",
       "metros_cuadrados":80,"antiguedad_vivienda":5,
       "calidad_aislamiento":"Muy Alta"}'
# Esperado: {"categoria": "Eficiente", "probabilidad": ~0.94, ...}

# Perfil 2: esperado Moderado
curl -s -X POST localhost:8765/analisis-energetico \
  -H 'Content-Type: application/json' \
  -d '{"consumo_kwh":420,"tipo_inmueble":"Departamento","horas_alto_consumo":8,
       "cantidad_equipos":15,"uso_horario_pico":false,"zona_fria":false,
       "fuente_calefaccion":"Electricidad","fuente_agua_caliente":"Electricidad",
       "metros_cuadrados":100,"antiguedad_vivienda":40,
       "calidad_aislamiento":"Media"}'
# Esperado: {"categoria": "Moderado", "probabilidad": ~0.69, ...}

# Perfil 3: esperado Ineficiente
curl -s -X POST localhost:8765/analisis-energetico \
  -H 'Content-Type: application/json' \
  -d '{"consumo_kwh":780,"tipo_inmueble":"Casa","horas_alto_consumo":18,
       "cantidad_equipos":35,"uso_horario_pico":true,"zona_fria":true,
       "fuente_calefaccion":"Electricidad","fuente_agua_caliente":"Electricidad",
       "metros_cuadrados":200,"antiguedad_vivienda":80,
       "calidad_aislamiento":"Muy Baja"}'
# Esperado: {"categoria": "Ineficiente", "probabilidad": ~0.79, ...}

# Cleanup: nombre especifico, no usa docker ps -q con filter
docker stop ml-cert-test
```

---

## Matriz de verificacion

| Punto | Comando | Resultado esperado |
|---|---|---|
| Dataset canonico intacto | `cd data-science/data && sha256sum -c CHECKSUMS.sha256` | exit 0 + 2/2 OK |
| Binding modelo+dataset+metricas | `sha256sum -c data-science/data/MODEL_BINDING.sha256` | exit 0 + 4/4 OK |
| Validador oficial | `python -m interfaces.cli.validate` | RESULTADO GLOBAL: PASS |
| Identidad runtime | `curl localhost:8765/model-info` | sha256 = `2c06370a...` (sklearn 1.9) |
| Healthcheck | `curl localhost:8765/health` | HTTP 200, `{"status":"healthy"}` |
| Tests pytest | `pytest tests/` | 244 passed |
| Certificacion end-to-end (local) | `bash data-science/data/verify_certification.sh` | 12/12 checks OK, exit 0 |
| Certificacion end-to-end (CI) | Ver GitHub Actions run del commit | job `data-science-ci`, 5/5 OK |

Si falla cualquiera de estos puntos, el modelo no esta en estado certificable.