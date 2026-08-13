# EnergiAI — Data Science / ML Service

Servicio FastAPI que expone el modelo predictivo de eficiencia energetica
(Indice IEE: Eficiente / Moderado / Ineficiente). El codigo es la
traduccion 1:1 a Python del notebook fuente de verdad
`notebooks/data_colab.ipynb` (sincronizado desde Colab).

## Estado

- **Modelo actual**: `data-science/data/modelo_eficiencia_v1.joblib`
- **Accuracy**: ~0.81 sobre 400 registros de test (split 80/20 estratificado)
- **Features**: 11 (5 numericas + 6 categoricas)
- **Algoritmo**: RandomForestClassifier (200 arboles) + ColumnTransformer
  (StandardScaler para numericas, OneHotEncoder para categoricas)
- **Categorias**: Eficiente / Moderado / Ineficiente

## Estructura

```
data-science/
  data/                              # artefactos bakeados en la imagen Docker
    modelo_eficiencia_v1.joblib      # model entrenado (.joblib, gitignored)
    metricas_v1.joblib               # reporte de clasificacion (.joblib)
    database_beta.json               # dataset generado (tracked en git)
    database_beta.csv                # (no generado, se genera en latest/)
  raw/
    application/                     # capa de aplicacion
      training.py                    # entrenar_y_guardar_modelo + CAT/NUM_COLS
      inference.py                   # procesar_solicitud_api + boundary bool→Si/No
    domain/                          # logica de negocio
      scoring.py                     # replica del IEE del colab (Fase 4-5)
      recommendations.py             # recomendaciones post-prediccion
    infrastructure/                  # cross-cutting
      config.py                      # env vars + distribuciones del dataset
      data/simulation.py             # replica del colab (Fase 1-3)
      ml/model_storage.py            # save/load .joblib
      storage/                       # Protocol Storage + local/oci/par
        sync.py                      # ensure_artifacts (download al startup)
        __init__.py                  # factory get_storage()
    interfaces/
      api/                           # FastAPI service
        app.py                       # uvicorn entrypoint (POST /analisis-energetico)
        schemas.py                   # Pydantic AnalisisRequest (4 oblig + 7 opcionales)
      cli/
        train.py                     # CLI: dataset + train + upload
        validate.py                  # CLI: valida artefactos locales
    scripts/                         # utilidades operativas
      sync_colab_notebook.py         # descarga colab y compara contra local
      validate_backend_contract.py   # valida el contrato HTTP backend→ML
    tests/                           # 219 tests (215 unit + 4 integration + e2e)
    notebooks/
      data_colab.ipynb               # UNICO notebook (sync'd desde Colab)
```

## Contrato HTTP (backend Spring → ML FastAPI)

4 obligatorios (alineados con `@NotNull` del backend `DatosRegistroConsumo`):

| Campo | Tipo | Validacion |
| --- | --- | --- |
| `consumo_kwh` | float | ge=0, le=1000 |
| `tipo_inmueble` | enum | Casa \| Departamento \| Comercio \| Pyme |
| `horas_alto_consumo` | int | ge=0, le=24 |
| `cantidad_equipos` | int | ge=1, le=100 |

7 opcionales con default (alineados con backend, sin `@NotNull`):

| Campo | Tipo | Default |
| --- | --- | --- |
| `uso_horario_pico` | bool | False |
| `zona_fria` | bool | False |
| `fuente_calefaccion` | enum | "Electricidad" |
| `fuente_agua_caliente` | enum | "Electricidad" |
| `metros_cuadrados` | float | 1000.0 (ge=26, le=2000) |
| `antiguedad_vivienda` | int | 50 (ge=0, le=150) |
| `calidad_aislamiento` | enum | "Media" |

El backend serializa con Jackson `@JsonInclude(NON_NULL)`, asi que cuando el
front no llena un opcional el back lo omite del JSON y el ML imputa el
default correspondiente.

## Flujo end-to-end

```
front (boolean) → back Spring (JSON wire format)
  ↓
  Jackson @JsonInclude(NON_NULL) omite nulls
  ↓
  POST http://ml-service:8000/analisis-energetico
  ↓
  Pydantic AnalisisRequest: valida + imputa defaults
  ↓
  application.inference._a_fila_modelo:
    - bool → "Si"/"No" para zona_fria/uso_horario_pico (boundary OHE)
    - orden de columnas = NUM_COLS + CAT_COLS (alineado con training)
  ↓
  RandomForestClassifier.predict_proba
  ↓
  {categoria, probabilidad, costo_estimado_mensual, recomendaciones}
  ↓
  back mapea: 200 OK / 422 → 400 / 5xx → 503 al front
```

## Indice IEE (calculo interno, no expuesto)

El scoring replica literalmente la logica del colab (Fases 4-5). Cada
hogar recibe un puntaje 0-100 combinando 4 dimensiones con pesos fijos:

- **Consumo** (peso 0.40): bins sobre `consumo_kwh` + bonificacion por no
  usar horario pico + bins sobre `horas_alto_consumo`
- **Eficiencia** (peso 0.30): map categorico de `calidad_aislamiento` +
  `fuente_calefaccion` + `fuente_agua_caliente`
- **Contexto** (peso 0.20): map de `tipo_inmueble` + bins sobre
  `metros_cuadrados` + bins sobre `antiguedad_vivienda` + bonificacion
  por no vivir en zona fria
- **Equipamiento** (peso 0.10): bins sobre `cantidad_equipos`

Categorias segun IEE:

- **Eficiente**: IEE > 70
- **Moderado**: 50 <= IEE <= 70
- **Ineficiente**: IEE < 50

Las reglas viven en `domain/scoring.py` (Python). El modelo `.joblib`
aprende a aproximar este calculo: en runtime NO se ejecuta el scoring,
solo el RF. El scoring se usa solo en training para generar las labels
(`calcular_iee_y_categoria(df)` en `simulation.py`).

## Pipeline de regeneracion

```
infrastructure/data/simulation.py
  ↓ generar_dataset(seed=42)
  ↓ DataFrame (2000, 13) con strings Si/No
  ↓
  ↓ calcular_iee_y_categoria() → column "categoria"
  ↓
  ↓ OUTPUT_JSON_PATH + OUTPUT_CSV_PATH + OUTPUT_MODEL_PATH
  ↓
  application/training.py
    ↓ entrenar_y_guardar_modelo()
    ↓ ColumnTransformer(StandardScaler + OneHotEncoder) → RandomForestClassifier
    ↓ save_model + save_metrics
    ↓
  infrastructure/storage.sync
    ↓ code_version check (git HEAD short SHA)
    ↓ si cambia → rota archive/<sha>_<artifact>
    ↓ upload latest/<artifact>
```

Comandos:

```bash
make pipeline              # genera dataset, entrena, sube a bucket local
python -m interfaces.cli.train
python -m interfaces.cli.validate     # valida los artefactos locales
```

## Sincronizacion con el Colab (consumidor EDA)

> **Arquitectura**: la fuente de verdad de generacion y scoring IEE vive
> en el codigo Python. La notebook Colab es un **consumidor EDA** que
> descarga el dataset publicado y hace analisis / visualizacion / tests
> estadisticos (chi², ANOVA).

**Fuente de verdad (Python):**

| Logica | Archivo |
|---|---|
| Distribuciones y rangos | `raw/infrastructure/config.py` |
| Generacion sintetica | `raw/infrastructure/data/simulation.py` |
| Scoring IEE + categoria | `raw/domain/scoring.py` |
| Contrato API (Pydantic) | `raw/interfaces/api/schemas.py` |

**Contrato del dataset** (`database_beta.json`, 2000 filas × 13 cols):

- `hogar_id` (string)
- `tipo_inmueble`, `calidad_aislamiento`, `fuente_calefaccion`,
  `fuente_agua_caliente` (string categórico)
- `zona_fria`, `uso_horario_pico` (string `"Si"`/`"No"`)
- `metros_cuadrados`, `antiguedad_vivienda`, `horas_alto_consumo`,
  `cantidad_equipos` (int)
- `consumo_kwh` (float)
- `categoria` (string ∈ {Eficiente, Moderado, Ineficiente})

**Notebook Colab** (`https://colab.research.google.com/drive/1-vJVVndXAngkMmPkeBoVU2pDtBY2SF4y`):
descarga `database_beta.json` desde la rama `develop` y ejecuta EDA,
visualizaciones (`px.bar`, `px.box`, `px.pie`), outliers y tests
estadisticos (`chi2`, `f_oneway`). El repo mantiene una copia local
en `raw/notebooks/data_colab.ipynb`.

```bash
python scripts/sync_colab_notebook.py             # check, exit 1 si difiere
python scripts/sync_colab_notebook.py --json      # output parseable
python scripts/sync_colab_notebook.py --apply     # descarga y sobrescribe
```

El script calcula SHA256 sobre las **celdas de codigo** del notebook
(ignora outputs y execution_count). Cualquier cambio en el codigo del
colab genera un diff por celda (added/removed/changed).

**Validacion del contrato Python ↔ notebook:**

```bash
make verify-notebook-contract    # valida que database_beta.json tiene
                                 # las 13 columnas y tipos que la
                                 # notebook espera consumir.
```

Tambien hay tests automaticos en `tests/unit/test_simulation.py`
(`TestSchemaContractWithNotebook`) que detectan drift entre el
contrato Python y la notebook.

## Storage backends

El servicio soporta 3 backends intercambiables via `STORAGE_BACKEND`:

- `local` (default dev/CI): filesystem en `STORAGE_LOCAL_ROOT=/app`.
  Los "uploads" al bucket son copias a `data-science/raw/latest/`.
- `oci`: SDK oficial de OCI Object Storage. Requiere credenciales OCI.
- `par`: Pre-Authenticated Request de OCI. Solo GET/PUT sobre una URL
  con token embebido. No soporta `delete()` ni `copy()`.

El factory `infrastructure.storage.get_storage()` retorna el backend
activo. El protocolo `Storage` (duck-typed) define la interfaz comun.

## Validacion de contrato con el backend

```bash
python scripts/validate_backend_contract.py              # in-process TestClient
python scripts/validate_backend_contract.py --train-if-missing   # entrena temp si no hay modelo
python scripts/validate_backend_contract.py --url http://ml-service:8000   # contra servicio real
python scripts/validate_backend_contract.py --json      # output parseable
```

Cubre el wire format exacto que Jackson produce desde
`backend/.../dto/DatosRegistroConsumo`: payload completo, payload
minimo (con NON_NULL omitiendo opcionales), bordes de validacion, enums
invalidos.

## Tests

```bash
pytest tests/                            # 219 tests (full suite)
pytest tests/integration/                # integration: training pipeline + inference
pytest tests/e2e/test_api.py             # e2e: FastAPI via TestClient
pytest tests/unit/test_model_storage.py  # artifact consistency guard
pytest tests/unit/test_colab_sync.py     # sync colab + diff logic
```

El guard `TestArtifactConsistency` en `test_model_storage.py` falla si
los `CAT_COLS`/`NUM_COLS` del artifact en disco no matchean con el codigo
actual de `application/training.py`. Evita que un `.joblib` stale llegue
a produccion.

## Variables de entorno

| Var | Default | Descripcion |
| --- | --- | --- |
| `MODEL_PATH` | `data/modelo_eficiencia_v1.joblib` | path al modelo cargado por FastAPI |
| `STORAGE_BACKEND` | `local` | local \| oci \| par |
| `STORAGE_LOCAL_ROOT` | (cwd) | root del "bucket" local |
| `OUTPUT_JSON_PATH` | `data/database_beta.json` | destino del dataset JSON |
| `OUTPUT_CSV_PATH` | (idem .json → .csv) | destino del dataset CSV |
| `OUTPUT_MODEL_PATH` | `data/modelo_eficiencia_v1.joblib` | destino del modelo |
| `OUTPUT_METRICAS_PATH` | `data/metricas_v1.joblib` | destino de metricas |
| `NUM_CLIENTES` | `2000` | hogares en el dataset sintetico |
| `RANDOM_SEED` | `42` | semilla de numpy.random |
| `TARIFA_KWH` | `0.75` | tarifa de referencia para costo estimado |
| `OCI_NAMESPACE` | (vacio) | namespace de OCI Object Storage |
| `OCI_BUCKET` | `g9-energy-test-bucket` | bucket OCI |
| `OCI_REGION` | (vacio) | region OCI |
| `OCI_PAR_URL` | (vacio) | URL pre-autenticada (cuando STORAGE_BACKEND=par) |
| `LOG_LEVEL` | `INFO` | nivel de logging |

## Docker

El `Dockerfile` en la raiz de `data-science/`:

1. `COPY raw/ ./` — todo el codigo fuente
2. `COPY data/ ./data/` — el modelo bakeado al build time
3. `uvicorn interfaces.api.app:app --host 0.0.0.0 --port 8000`

Para actualizar el modelo bakeado en la imagen:

```bash
python -m interfaces.cli.train           # regenera artifacts
cp data-science/raw/data/*.joblib data-science/data/    # copia el fresco
docker build -t energiai-ml-service:latest data-science/
```

Alternativamente en produccion, usar `STORAGE_BACKEND=oci` o `par` para
que `ensure_artifacts()` descargue el modelo desde el bucket al startup
sin bakearlo en la imagen.

## Convenciones

- Paths absolutos en configs, relativos en runtime (compatibilidad Docker)
- Boundaries explicitos (ver `application/inference.py:_coerce_si_no`)
- Defaults exportados como constantes (`interfaces/api/schemas.py:DEFAULT_*`)
- Comentarios y docstrings en espanol (mantener consistencia con el colab)
- Tests con clases `Test*` y fixtures en `tests/conftest.py`
