from fastapi import FastAPI
from pydantic import BaseModel, Field

from src.inference import procesar_solicitud_api

app = FastAPI(title="EnergiAI - Analisis Energetico", version="1.0.0")


class AnalisisRequest(BaseModel):
    consumo_electrico_kwh: float = Field(..., ge=0, description="Consumo mensual en kWh")
    uso_horario_pico: bool = Field(False, description="Uso principal en horario punta")
    cantidad_equipos: int = Field(..., ge=0, description="Cantidad de electrodomesticos")
    tipo_inmueble: str = Field(..., description="Casa, Departamento, Duplex, etc.")
    horas_alto_consumo: int = Field(..., ge=0, le=24, description="Horas diarias de alto consumo")
    calidad_aislamiento: str = Field(..., description="alta | media | baja | muy_baja")
    energia_solar: str = Field(..., description="si | no")


@app.get("/")
def root():
    return {"service": "EnergiAI", "status": "ok", "endpoint": "POST /analisis-energetico"}


@app.post("/analisis-energetico")
def analisis_energetico(req: AnalisisRequest):
    solar_norm = req.energia_solar.strip().lower()
    renewable_norm = "si" if solar_norm == "si" else "no"

    input_data = {
        "consumo_electrico_kwh": req.consumo_electrico_kwh,
        "consumo_total_kwh": req.consumo_electrico_kwh,
        "uso_horario_pico": req.uso_horario_pico,
        "cant_electrodomesticos": req.cantidad_equipos,
        "cantidad_equipos": req.cantidad_equipos,
        "tipo_inmueble": req.tipo_inmueble,
        "tipo_vivienda": req.tipo_inmueble.strip().lower(),
        "horas_alto_consumo": req.horas_alto_consumo,
        "calidad_aislamiento": req.calidad_aislamiento,
        "energia_solar": req.energia_solar,
        "energia_renovable": renewable_norm,
    }

    return procesar_solicitud_api(input_data, "data/modelo_eficiencia_v1.joblib")
