import os

from fastapi import FastAPI, HTTPException

from application.inference import procesar_solicitud_api
from infrastructure.config import Config
from interfaces.api.schemas import AnalisisRequest

app = FastAPI(title="EnergiAI - Analisis Energetico", version="1.1.0")
MODEL_PATH = os.getenv("MODEL_PATH", Config.OUTPUT_MODEL_PATH)


@app.get("/")
def root():
    return {"service": "EnergiAI", "status": "ok", "endpoint": "POST /analisis-energetico"}


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/analisis-energetico")
def analisis_energetico(req: AnalisisRequest):
    input_data = {
        "tipo_inmueble": req.tipo_inmueble,
        "metros_cuadrados": req.metros_cuadrados,
        "antiguedad_vivienda": req.antiguedad_vivienda,
        "zona_fria": req.zona_fria,
        "calidad_aislamiento": req.calidad_aislamiento,
        "fuente_calefaccion": req.fuente_calefaccion,
        "fuente_agua_caliente": req.fuente_agua_caliente,
        "consumo_kwh": req.consumo_electrico_kwh,
        "uso_horario_pico": req.uso_horario_pico,
        "horas_alto_consumo": req.horas_alto_consumo,
        "cantidad_equipos": req.cantidad_equipos,
    }

    try:
        return procesar_solicitud_api(input_data, MODEL_PATH)
    except FileNotFoundError:
        raise HTTPException(
            status_code=503,
            detail=(
                f"Modelo no encontrado en {MODEL_PATH}. "
                "Ejecuta 'make pipeline' para entrenar y persistir el modelo."
            ),
        )