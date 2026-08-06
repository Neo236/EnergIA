import numpy as np
import pandas as pd

from application.training import FEATURE_COLS
from domain.recommendations import calcular_recomendaciones
from infrastructure.config import Config
from infrastructure.ml.model_storage import load_model
from interfaces.api.schemas import (
    DEFAULT_ANTIGUEDAD_VIVIENDA,
    DEFAULT_CALIDAD_AISLAMIENTO,
    DEFAULT_FUENTE_AGUA_CALIENTE,
    DEFAULT_FUENTE_CALEFACCION,
    DEFAULT_METROS_CUADRADOS,
    DEFAULT_USO_HORARIO_PICO,
    DEFAULT_ZONA_FRIA,
)

# El orden/identidad de las features se deriva del training pipeline para
# garantizar que la inferencia use exactamente el mismo set que el modelo
# aprendio. Cambiar FEATURE_COLS en application.training.py se propaga solo.
MODELO_FEATURES = list(FEATURE_COLS)

CATEGORIAS_VALIDAS = {"Eficiente", "Moderado", "Ineficiente"}

# Defaults para features que el caller puede omitir. FUENTE UNICA:
# las constantes DEFAULT_* de interfaces.api.schemas. Si la API recibe solo
# los campos obligatorios, este dict suple los opcionales al modelo con
# los mismos valores que la API usa por default.
DEFAULTS = {
    "tipo_inmueble": "Casa",
    "metros_cuadrados": DEFAULT_METROS_CUADRADOS,
    "antiguedad_vivienda": DEFAULT_ANTIGUEDAD_VIVIENDA,
    "zona_fria": DEFAULT_ZONA_FRIA,
    "calidad_aislamiento": DEFAULT_CALIDAD_AISLAMIENTO,
    "fuente_calefaccion": DEFAULT_FUENTE_CALEFACCION,
    "fuente_agua_caliente": DEFAULT_FUENTE_AGUA_CALIENTE,
    "consumo_kwh": 500.0,
    "uso_horario_pico": DEFAULT_USO_HORARIO_PICO,
    "horas_alto_consumo": 12,
    "cantidad_equipos": 30,
}


def _a_fila_modelo(input_data: dict) -> pd.DataFrame:
    row = {feat: input_data.get(feat, DEFAULTS[feat]) for feat in MODELO_FEATURES}
    return pd.DataFrame([row], columns=MODELO_FEATURES)


def _normalizar_categoria(raw: str) -> str:
    """Mapea la salida del modelo al set cerrado del dominio."""
    if raw not in CATEGORIAS_VALIDAS:
        raise ValueError(
            f"Modelo devolvio categoria no soportada: {raw!r}. "
            f"Esperado: {CATEGORIAS_VALIDAS}"
        )
    return raw


def procesar_solicitud_api(input_data: dict, model_path: str) -> dict:
    modelo = load_model(model_path)

    X = _a_fila_modelo(input_data)
    probs = modelo.predict_proba(X)[0]
    clases = list(modelo.classes_)
    idx = int(np.argmax(probs))
    categoria = _normalizar_categoria(str(clases[idx]))
    probabilidad = float(probs[idx])

    consumo_kwh = float(input_data.get("consumo_kwh", 0))
    costo = round(consumo_kwh * Config.TARIFA_KWH, 2)

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