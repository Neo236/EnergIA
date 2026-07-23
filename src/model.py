import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


def entrenar_y_guardar_modelo(df: pd.DataFrame, output_path: str,
                               metricas_path: str, random_seed: int) -> dict:
    y = df["categoria"]
    X = df.drop(columns=["id_cliente", "categoria", "puntaje"])

    cat_cols = ["tipo_vivienda", "calefaccion", "region",
                "eficiencia_promedio", "energia_renovable"]
    num_cols = [c for c in X.columns if c not in cat_cols]

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), num_cols),
            ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), cat_cols),
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

    joblib.dump(modelo, output_path)
    joblib.dump({"y_test": y_test, "y_pred": y_pred}, metricas_path)

    return {"modelo": modelo, "reporte": reporte, "y_test": y_test, "y_pred": y_pred}
