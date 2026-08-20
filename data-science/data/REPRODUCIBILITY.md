# Reproducibilidad del entrenamiento y evaluación

> Documento auditable. Cualquiera con este repo + Python 3.10 + Docker
> puede reproducir el modelo v1 desde cero y obtener los mismos hashes.

---

## TL;DR — 4 comandos para regenerar todo

```bash
# 1. Entrenar (regenera dataset + modelo + métricas en data-science/data/)
cd data-science/raw
NUM_CLIENTES=2000 RANDOM_SEED=42 \
  OUTPUT_JSON_PATH=../data/database_beta.json \
  OUTPUT_CSV_PATH=../data/database_beta.csv \
  OUTPUT_MODEL_PATH=../data/modelo_eficiencia_v1.joblib \
  OUTPUT_METRICAS_PATH=../data/metricas_v1.joblib \
  python3 -m interfaces.cli.train --dry-run

# 2. Validar artefactos
NUM_CLIENTES=2000 \
  OUTPUT_JSON_PATH=../data/database_beta.json \
  OUTPUT_MODEL_PATH=../data/modelo_eficiencia_v1.joblib \
  OUTPUT_METRICAS_PATH=../data/metricas_v1.joblib \
  python3 -m interfaces.cli.validate

# 3. Verificar binding criptográfico
cd ../..
sha256sum -c data-science/data/MODEL_BINDING.sha256

# 4. Verificar identidad runtime del modelo servido
docker run -d --rm -p 127.0.0.1:8765:8000 -e STORAGE_BACKEND=local \
  energiai-ml-service:fea27b7
sleep 4
curl -s localhost:8765/model-info | python3 -m json.tool
# Debe reportar sha256: "2c06370a7e379d8a1b01e507bdccce3a64831ef23809d142333dca8f4560eba2"
docker stop $(docker ps -q --filter ancestor=energiai-ml-service:fea27b7)
```

---

## Inputs canónicos (versionados en la rama `data`)

| Archivo | SHA-256 |
|---|---:|
| `data-science/data/database_beta.json` | `74939597360ad75823e01654e18f1172b549c283a2a3aed201c2ee182257400b` |
| `data-science/data/database_beta.csv` | `92578ad71e64b2d6e37fdb083cd673a9d933c3c5f4c46239eaab7fde65f5a5f3` |

Verificables con:
```bash
cd data-science/data && sha256sum -c CHECKSUMS.sha256
```

## Outputs generados (gitignored, viven en `data-science/data/`)

| Archivo | SHA-256 | Cómo se produce |
|---|---:|---|
| `data-science/data/modelo_eficiencia_v1.joblib` | `2c06370a7e379d8a1b01e507bdccce3a64831ef23809d142333dca8f4560eba2` | `python -m interfaces.cli.train` |
| `data-science/data/metricas_v1.joblib` | `2945e5048db2ca39253ce788731ef86bccbd078cb78bbbde2223c5f8bcec56d9` | mismo train.py (split interno) |

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

### Configuración exacta

| Parámetro | Valor | Fuente |
|---|---:|---|
| `NUM_CLIENTES` | 2000 | `infrastructure/config.py` |
| `RANDOM_SEED` | 42 | `infrastructure/config.py` (numpy global) |
| `RANDOM_STATE` (RF) | 42 | `application/training.py` |
| `n_estimators` | 200 | `application/training.py` |
| `test_size` | 0.2 | `application/training.py` |
| `stratify` | yes | `application/training.py` |
| `JOBLIB_COMPRESS` | 3 | `infrastructure/ml/model_storage.py` |

---

## Pipeline de evaluación

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

## 3 perfiles canónicos (golden tests)

Para validar que el modelo entrenado se comporta como el esperado:

```bash
docker run -d --rm -p 127.0.0.1:8765:8000 -e STORAGE_BACKEND=local \
  energiai-ml-service:fea27b7
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

docker stop $(docker ps -q --filter ancestor=energiai-ml-service:fea27b7)
```

---

## Matriz de verificación

| Punto | Comando | Resultado esperado |
|---|---|---|
| Dataset canónico intacto | `cd data-science/data && sha256sum -c CHECKSUMS.sha256` | 2/2 OK |
| Binding modelo+dataset+metricas | `sha256sum -c data-science/data/MODEL_BINDING.sha256` | 4/4 OK |
| Validador oficial | `python -m interfaces.cli.validate` | RESULTADO GLOBAL: PASS |
| Identidad runtime | `curl localhost:8765/model-info` | sha256 = `2c06370a...` |
| Healthcheck | `curl localhost:8765/health` | HTTP 200, `{"status":"healthy"}` |
| Tests pytest | `pytest tests/` | 244 passed |
| 3 perfiles golden | curl x3 | Eficiente, Moderado, Ineficiente |

Si falla cualquiera de estos puntos, el modelo no está en estado certificable.
