# Métricas finales del modelo v1

> **Versión**: `modelo_eficiencia_v1.joblib`
> **SHA-256**: `2c06370a7e379d8a1b01e507bdccce3a64831ef23809d142333dca8f4560eba2`
> **Dataset**: `data-science/data/database_beta.{json,csv}` (2000 hogares, **sintético**)
> **Algoritmo**: `RandomForestClassifier(n_estimators=200, random_state=42)`
> **Test set**: 400 hogares (split 80/20 estratificado, `RANDOM_SEED=42`)
> **Fecha**: 2026-08-20

> ⚠️ **Limitación importante**: las métricas reportadas acá se midieron sobre el
> test set del dataset sintético. **No son directamente extrapolables a
> performance en datos reales.** El dataset sintético replica patrones típicos
> del consumo energético argentino, pero no captura variabilidad real
> (estacional, regional, hábitos puntuales). Ver `PARA_CONSTANZA.md` §3.

---

## Métricas agregadas (test set, n=400)

| Métrica | Valor | Lectura técnica |
|---|---:|---|
| **Accuracy** | **0.81** | Proporción de predicciones correctas sobre el test sintético |
| **Macro F1** | 0.72 | Promedio no ponderado de F1 por clase — sensible al desbalance |
| **Weighted F1** | 0.80 | Promedio ponderado por soporte — **es un promedio matemático, no una proyección de performance en producción** |

---

## Métricas por clase (test set, n=400)

| Clase | Precision | Recall | F1 | Support (test) |
|---|---:|---:|---:|---:|
| **Eficiente** | 0.91 | 0.54 | **0.68** | 72 |
| **Ineficiente** | 0.90 | 0.45 | **0.60** | 62 |
| **Moderado** | 0.79 | 0.97 | **0.88** | 266 |

> ⚠️ **Sobre precision = 0.90**: significa que, **dentro del test sintético**,
> el 90% de los hogares que el modelo clasifica como `Ineficiente`
> REALMENTE son `Ineficiente` en el dataset simulado. Esto **no equivale**
> a "en producción, cuando el modelo diga Ineficiente, acertará el 90%
> de las veces". En datos reales el patrón puede ser distinto.

---

## Matriz de confusión (test set, n=400)

|              | pred Eficiente | pred Ineficiente | pred Moderado | **total real** |
|---|---:|---:|---:|---:|
| **true Eficiente** | 39 | 0 | 33 | 72 |
| **true Ineficiente** | 0 | 28 | 34 | 62 |
| **true Moderado** | 4 | 3 | 259 | 266 |
| **total predicho** | 43 | 31 | 326 | 400 |

Lecturas concretas (sobre el test sintético):

- De cada **266 Moderados reales**, el modelo clasifica:
  - 259 como Moderado (97.4%)
  - 4 como Eficiente (1.5%)
  - **34 como Ineficiente (12.8%)**
- De cada **62 Ineficientes reales**, el modelo detecta 28 (45.2%) y
  pierde 34 (54.8% los manda a Moderado).
- Cuando el modelo dice "Ineficiente" (31 casos en test), 28 son
  Ineficientes reales (precision 90.3%) y 3 son Moderados.

> ⚠️ **Sobre el 12.8% (Moderado → Ineficiente)**: este número sale
> directamente de la matriz de confusión sobre el test sintético. Es un
> dato empírico de la performance del modelo en datos simulados, **no
> una estimación de lo que pasará en producción** con datos reales.

---

## Distribución del dataset

Calculado desde `data-science/data/database_beta.json` (2000 registros) y
`metricas_v1.joblib` (400 test rows):

| Clase | Train (1600) | Test (400) | Total (2000) | % Total |
|---|---:|---:|---:|---:|
| Eficiente | 285 | 72 | 357 | 17.85% |
| Moderado | 1065 | 266 | 1331 | 66.55% |
| Ineficiente | 250 | 62 | 312 | 15.60% |
| **Total** | **1600** | **400** | **2000** | **100.00%** |

> El dataset está desbalanceado: Moderado representa 2/3 de los hogares.
> El sesgo del modelo hacia esa clase (recall 0.97 en Moderado, 0.45 en
> Ineficiente) es consecuencia directa de esa distribución.

---

## Reproducir estas métricas desde el artefacto

```bash
cd data-science/raw
python3 -c "
import joblib, collections
import pandas as pd
from sklearn.metrics import classification_report, accuracy_score, f1_score, confusion_matrix

m = joblib.load('../data/metricas_v1.joblib')
y_test, y_pred = m['y_test'], m['y_pred']

# Métricas globales
print(f'Accuracy:    {accuracy_score(y_test, y_pred):.4f}')
print(f'Macro F1:    {f1_score(y_test, y_pred, average=\"macro\", zero_division=0):.4f}')
print(f'Weighted F1: {f1_score(y_test, y_pred, average=\"weighted\", zero_division=0):.4f}')
print()

# Confusion matrix
labels = ['Eficiente', 'Ineficiente', 'Moderado']
cm = confusion_matrix(y_test, y_pred, labels=labels)
print('Confusion matrix:')
print(cm)
print()

# Classification report
print(classification_report(y_test, y_pred, zero_division=0))

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