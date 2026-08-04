import numpy as np
import pandas as pd

from domain.recommendations import calcular_recomendaciones
from infrastructure.ml.model_storage import load_model

TARIFA_KWH = 0.75
MODELO_FEATURES = [
    "tipo_inmueble",
    "metros_cuadrados",
    "antiguedad_vivienda",
    "zona_fria",
    "calidad_aislamiento",
    "fuente_calefaccion",
    "fuente_agua_caliente",
    "consumo_kwh",
    "uso_horario_pico",
    "horas_alto_consumo",
    "cantidad_equipos",
]

DEFAULTS = {
    "tipo_inmueble": "Casa",
    "metros_cuadrados": 1000.0,
    "antiguedad_vivienda": 50,
    "zona_fria": False,
    "calidad_aislamiento": "Media",
    "fuente_calefaccion": "Electricidad",
    "fuente_agua_caliente": "Electricidad",
    "consumo_kwh": 500.0,
    "uso_horario_pico": False,
    "horas_alto_consumo": 12,
    "cantidad_equipos": 30,
}


def _a_fila_modelo(input_data: dict) -> pd.DataFrame:
    row = {feat: input_data.get(feat, DEFAULTS[feat]) for feat in MODELO_FEATURES}
    if "consumo_electrico_kwh" in input_data and "consumo_kwh" not in input_data:
        row["consumo_kwh"] = input_data["consumo_electrico_kwh"]
    return pd.DataFrame([row], columns=MODELO_FEATURES)


def procesar_solicitud_api(input_data: dict, model_path: str) -> dict:
    modelo = load_model(model_path)

    X = _a_fila_modelo(input_data)
    probs = modelo.predict_proba(X)[0]
    clases = list(modelo.classes_)
    idx = int(np.argmax(probs))
    categoria = str(clases[idx])
    probabilidad = float(probs[idx])

    consumo_kwh = float(input_data.get("consumo_kwh",
                                        input_data.get("consumo_electrico_kwh", 0)))
    costo = round(consumo_kwh * TARIFA_KWH, 2)

    recomendaciones = calcular_recomendaciones(input_data)

    return {
        "categoria": categoria,
        "probabilidad": round(probabilidad, 4),
        "costo_estimado_mensual": costo,
        "recomendaciones": recomendaciones,
    }


def _demo_request() -> dict:
    return {
        "tipo_inmueble": "Casa",
        "metros_cuadrados": 1269,
        "antiguedad_vivienda": 61,
        "zona_fria": False,
        "calidad_aislamiento": "Muy Baja",
        "fuente_calefaccion": "Solar",
        "fuente_agua_caliente": "Electricidad",
        "consumo_kwh": 363.4,
        "uso_horario_pico": True,
        "horas_alto_consumo": 14,
        "cantidad_equipos": 19,
    }


if __name__ == "__main__":
    import json
    import sys

    payload = _demo_request()
    output = procesar_solicitud_api(payload, "data/modelo_eficiencia_v1.joblib")
    print(json.dumps(output, indent=2, ensure_ascii=False))
    sys.exit(0)