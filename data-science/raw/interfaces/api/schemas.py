from typing import Literal

from pydantic import BaseModel, Field

TipoInmueble = Literal["Casa", "Departamento", "Comercio", "Pyme"]
CalidadAislamiento = Literal["Muy Alta", "Alta", "Media", "Baja", "Muy Baja"]
FuenteEnergia = Literal["Electricidad", "Solar", "Otros"]


class AnalisisRequest(BaseModel):
    consumo_electrico_kwh: float = Field(..., ge=0, description="Consumo mensual en kWh")
    uso_horario_pico: bool = Field(False, description="Uso principal en horario punta")
    cantidad_equipos: int = Field(..., ge=0, description="Cantidad de electrodomésticos")
    tipo_inmueble: TipoInmueble = Field(..., description="Casa, Departamento, Comercio, Pyme")
    horas_alto_consumo: int = Field(..., ge=0, le=24, description="Horas diarias de alto consumo")
    calidad_aislamiento: CalidadAislamiento = Field(..., description="Muy Alta | Alta | Media | Baja | Muy Baja")
    metros_cuadrados: float = Field(..., ge=0, description="Superficie del inmueble")
    antiguedad_vivienda: int = Field(..., ge=0, description="Años de antigüedad")
    zona_fria: bool = Field(False, description="Vive en zona climática fría")
    fuente_calefaccion: FuenteEnergia = Field(..., description="Electricidad | Solar | Otros")
    fuente_agua_caliente: FuenteEnergia = Field(..., description="Electricidad | Solar | Otros")