import json
import sys

import joblib
import numpy as np
import pandas as pd

TARIFA_KWH = 0.75
CATEGORIAS = ("eficiente", "moderado", "ineficiente")
MODELO_FEATURES = [
    "tipo_vivienda", "superficie_m2", "calefaccion", "region", "ingresos",
    "consumo_total_kwh", "cant_electrodomesticos", "anio_promedio",
    "eficiencia_promedio", "energia_renovable",
]
DEFAULTS = {
    "tipo_vivienda": "casa",
    "superficie_m2": 75.0,
    "calefaccion": "gas",
    "region": "centro",
    "ingresos": 1500,
    "consumo_total_kwh": 250.0,
    "cant_electrodomesticos": 8,
    "anio_promedio": 2018,
    "eficiencia_promedio": "A",
    "energia_renovable": "no",
}


def _a_fila_modelo(input_data: dict) -> pd.DataFrame:
    row = {feat: input_data.get(feat, DEFAULTS[feat]) for feat in MODELO_FEATURES}
    if "consumo_electrico_kwh" in input_data and "consumo_total_kwh" not in input_data:
        row["consumo_total_kwh"] = input_data["consumo_electrico_kwh"]
    return pd.DataFrame([row], columns=MODELO_FEATURES)


def _calcular_recomendaciones(input_data: dict) -> list[str]:
    recs: list[str] = []

    consumo = float(input_data.get("consumo_electrico_kwh",
                                   input_data.get("consumo_total_kwh", 0)))
    if consumo > 500:
        recs.append("Tu consumo eléctrico es muy elevado. "
                    "Considera revisar electrodomésticos de alto consumo.")
    elif consumo > 350:
        recs.append("Tu consumo eléctrico está por encima del promedio. "
                    "Audita el uso de calefacción y electrodomésticos.")

    aislamiento = str(input_data.get("calidad_aislamiento", "media")).lower()
    if aislamiento in ("baja", "muy_baja", "muy baja"):
        recs.append("Mejorar el aislamiento térmico de tu hogar reducirá "
                    "drásticamente la necesidad de climatización.")

    solar = str(input_data.get("energia_solar", "no")).lower()
    if solar in ("no", "false", "0"):
        recs.append("Evalúa la instalación de paneles solares para reducir "
                    "tu dependencia de la red eléctrica.")

    eficiencia = str(input_data.get("eficiencia_promedio", "B")).upper()
    if eficiencia in ("C", "D", "E"):
        recs.append("Reemplaza electrodomésticos ineficientes (etiqueta C o inferior) "
                    "por equipos clase A+: el ahorro a 5 años supera la inversión.")

    cant_eq = int(input_data.get("cant_electrodomesticos", 0))
    if cant_eq > 12:
        recs.append("Tienes más de 12 electrodomésticos. Centraliza el uso en horarios "
                    "de menor demanda para optimizar tu tarifa.")

    if not recs:
        recs.append("Tu hogar está bien calibrado. Mantén hábitos de consumo eficientes.")
    return recs


def procesar_solicitud_api(input_data: dict, model_path: str) -> dict:
    modelo = joblib.load(model_path)

    X = _a_fila_modelo(input_data)
    probs = modelo.predict_proba(X)[0]
    clases = list(modelo.classes_)
    idx = int(np.argmax(probs))
    categoria = str(clases[idx])
    probabilidad = float(probs[idx])

    consumo_kwh = float(input_data.get("consumo_electrico_kwh",
                                        input_data.get("consumo_total_kwh", 0)))
    costo = round(consumo_kwh * TARIFA_KWH, 2)

    recomendaciones = _calcular_recomendaciones(input_data)

    return {
        "categoria": categoria,
        "probabilidad": round(probabilidad, 4),
        "costo_estimado_mensual": costo,
        "recomendaciones": recomendaciones,
    }


def _demo_request() -> dict:
    return {
        "tipo_vivienda": "casa",
        "superficie_m2": 140,
        "calefaccion": "electrica",
        "region": "sur",
        "ingresos": 2200,
        "consumo_electrico_kwh": 620,
        "consumo_total_kwh": 620,
        "cant_electrodomesticos": 14,
        "anio_promedio": 2010,
        "eficiencia_promedio": "C",
        "energia_renovable": "no",
        "energia_solar": "no",
        "calidad_aislamiento": "baja",
        "ocupacion": 4,
    }


if __name__ == "__main__":
    payload = _demo_request()
    output = procesar_solicitud_api(payload, "data/modelo_eficiencia_v1.joblib")
    print(json.dumps(output, indent=2, ensure_ascii=False))
    sys.exit(0)
