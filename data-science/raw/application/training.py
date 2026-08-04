import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from infrastructure.ml.model_storage import save_metrics, save_model

CAT_COLS = [
    "tipo_inmueble",
    "calidad_aislamiento",
    "fuente_calefaccion",
    "fuente_agua_caliente",
]
NUM_COLS = [
    "metros_cuadrados",
    "antiguedad_vivienda",
    "zona_fria",
    "consumo_kwh",
    "uso_horario_pico",
    "horas_alto_consumo",
    "cantidad_equipos",
]
FEATURE_COLS = NUM_COLS + CAT_COLS
TARGET_COL = "categoria"


def entrenar_y_guardar_modelo(df: pd.DataFrame, output_path: str,
                               metricas_path: str, random_seed: int) -> dict:
    y = df[TARGET_COL]
    X = df[FEATURE_COLS]

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), NUM_COLS),
            ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), CAT_COLS),
        ]
    )

    modelo = Pipeline(steps=[
        ("prep", preprocessor),
        ("clf", RandomForestClassifier(n_estimators=200, random_state=random_seed, n_jobs=-1)),
    ])

    estrato = y if y.value_counts().min() >= 2 else None
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=random_seed, stratify=estrato
    )

    modelo.fit(X_train, y_train)
    y_pred = modelo.predict(X_test)
    reporte = classification_report(y_test, y_pred, zero_division=0)

    save_model(modelo, output_path)
    save_metrics({"y_test": y_test, "y_pred": y_pred}, metricas_path)

    return {"modelo": modelo, "reporte": reporte, "y_test": y_test, "y_pred": y_pred}