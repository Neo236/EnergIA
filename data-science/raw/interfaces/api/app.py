import os
import sys

from fastapi import FastAPI, HTTPException

from application.inference import procesar_solicitud_api
from infrastructure.config import Config
from infrastructure.storage import get_storage
from infrastructure.storage.sync import ensure_artifacts
from interfaces.api.schemas import AnalisisRequest

log_level = os.getenv("LOG_LEVEL", "INFO")
import logging

logging.basicConfig(level=log_level, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
log = logging.getLogger(__name__)

app = FastAPI(title="EnergiAI - Analisis Energetico", version="1.2.0")
MODEL_PATH = os.getenv("MODEL_PATH", Config.OUTPUT_MODEL_PATH)


@app.on_event("startup")
def _startup():
    try:
        ensure_artifacts()
    except Exception as e:
        log.warning("ensure_artifacts falló al startup: %s", e)


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
                "Si STORAGE_BACKEND=oci, ejecuta 'make pipeline' con STORAGE_BACKEND=oci "
                "para subir el modelo al bucket."
            ),
        )