# Métricas finales del modelo v1

> **Versión**: `modelo_eficiencia_v1.joblib`
> **SHA-256**: `2c06370a7e379d8a1b01e507bdccce3a64831ef23809d142333dca8f4560eba2`
> **Dataset**: `data-science/data/database_beta.{json,csv}` (2000 hogares, canónico)
> **Algoritmo**: `RandomForestClassifier(n_estimators=200, random_state=42)`
> **Test set**: 400 hogares (split 80/20 estratificado, `RANDOM_SEED=42`)
> **Fecha**: 2026-08-20

---

## Métricas agregadas

| Métrica | Valor | Interpretación |
|---|---:|---|
| **Accuracy** | **0.81** | De cada 100 hogares nuevos, ~81 son clasificados correctamente en su categoría IEE |
| **Macro F1** | 0.72 | Promedio no ponderado del F1 por clase — útil cuando las clases están desbalanceadas |
| **Weighted F1** | 0.80 | Promedio ponderado por soporte — refleja lo que "se ve" en producción |
| **Macro Precision** | 0.87 | Cuando el modelo dice "X categoría", acierta ~87% de las veces (promedio) |
| **Macro Recall** | 0.66 | El modelo detecta ~66% de los hogares de cada categoría (promedio) |

---

## Métricas por clase (test set)

| Clase | Precision | Recall | F1 | Support (test) |
|---|---:|---:|---:|---:|
| **Eficiente** | 0.91 | 0.54 | **0.68** | 72 |
| **Ineficiente** | 0.90 | 0.45 | **0.60** | 62 |
| **Moderado** | 0.79 | 0.97 | **0.88** | 266 |

Lectura:
- **`Moderado`** es la clase dominante y el modelo la detecta muy bien (recall 0.97).
- **`Ineficiente`** tiene alta precision (0.90) pero recall moderado (0.45) — cuando el modelo dice "Ineficiente" acierta, pero se le escapan ~55% de los ineficientes reales (los clasifica como Moderado).
- **`Eficiente`** tiene precision alta (0.91) pero recall bajo (0.54) — similar a Ineficiente.

> **Implicación práctica**: si el modelo clasifica un hogar como `Ineficiente`, esa predicción es muy confiable (precision 0.90). Pero si lo clasifica como `Moderado`, podría haber un 5–10% de probabilidad de que en realidad sea Ineficiente — vale la pena revisar manualmente los casos borderline.

---

## Distribución del dataset

Estos números se calcularon directamente desde `data-science/data/database_beta.json`
(2000 registros) y desde `metricas_v1.joblib` (400 test rows):

| Clase | Train (1600) | Test (400) | Total (2000) | % Total |
|---|---:|---:|---:|---:|
| Eficiente | 285 | 72 | 357 | 17.85% |
| Moderado | 1065 | 266 | 1331 | 66.55% |
| Ineficiente | 250 | 62 | 312 | 15.60% |
| **Total** | **1600** | **400** | **2000** | **100.00%** |

> El dataset está desbalanceado: Moderado representa 2/3 de los hogares. Esto
> explica el sesgo del modelo hacia esa clase. Para mejorar recall de
> Ineficiente en futuras versiones, considerar técnicas de balanceo
> (`class_weight='balanced'`, SMOTE, o sobre-muestreo).

---

## Reproducir estas métricas desde el artefacto

```bash
cd data-science/raw
python3 -c "
import joblib, collections
import pandas as pd
from sklearn.metrics import classification_report, accuracy_score, f1_score

m = joblib.load('../data/metricas_v1.joblib')
y_test, y_pred = m['y_test'], m['y_pred']

# Métricas globales
print(f'Accuracy:    {accuracy_score(y_test, y_pred):.4f}')
print(f'Macro F1:    {f1_score(y_test, y_pred, average=\"macro\", zero_division=0):.4f}')
print(f'Weighted F1: {f1_score(y_test, y_pred, average=\"weighted\", zero_division=0):.4f}')
print()

# Distribución real (test)
print('Distribución test (y_test):')
for k, v in sorted(collections.Counter(y_test).items()):
    print(f'  {k}: {v}')
print()

# Classification report
print(classification_report(y_test, y_pred, zero_division=0))
print()

# Distribución del dataset completo
data = pd.read_json('../data/database_beta.json')
print('Distribución total dataset:')
total = collections.Counter(data['categoria'])
total_n = sum(total.values())
for k in sorted(total):
    n = total[k]
    train = n - (72 if k == 'Eficiente' else 266 if k == 'Moderado' else 62)
    print(f'  {k}: {n} total ({n/total_n*100:.2f}%) -> train={train}, test={n-train}')
"
```

O usar el validador oficial:

```bash
cd data-science/raw
NUM_CLIENTES=2000 \
  OUTPUT_JSON_PATH=../data/database_beta.json \
  OUTPUT_MODEL_PATH=../data/modelo_eficiencia_v1.joblib \
  OUTPUT_METRICAS_PATH=../data/metricas_v1.joblib \
  python3 -m interfaces.cli.validate
```

Salida esperada:
```
RESULTADO GLOBAL: PASS
  accuracy: 0.81  (400 test, 80/20 split)
```