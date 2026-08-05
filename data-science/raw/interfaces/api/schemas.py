"""Schemas Pydantic para la API de analisis energetico.

Obligatorias (4) - el usuario tipico las tiene a mano:
    - consumo_kwh: lo que ve en su factura.
    - tipo_inmueble: tipo de vivienda (Casa, Depto, Comercio, Pyme).
    - cantidad_equipos: estimacion del usuario.
    - horas_alto_consumo: estimacion del usuario.

Opcionales (7) - contexto del hogar que el usuario no siempre conoce:
    Las constantes DEFAULT_* debajo son la FUENTE UNICA de los defaults.
    `application.inference.DEFAULTS` las importa y arma el dict de
    defaults para el modelo. Si cambias un valor aqui, se propaga
    automaticamente al modelo de inferencia.
"""

from typing import Literal

from pydantic import BaseModel, Field

TipoInmueble = Literal["Casa", "Departamento", "Comercio", "Pyme"]
CalidadAislamiento = Literal["Muy Alta", "Alta", "Media", "Baja", "Muy Baja"]
FuenteEnergia = Literal["Electricidad", "Solar", "Otros"]


# Defaults para campos opcionales. FUENTE UNICA: importado por
# application.inference para construir su dict DEFAULTS.
DEFAULT_METROS_CUADRADOS = 1000.0
DEFAULT_ANTIGUEDAD_VIVIENDA = 50
DEFAULT_ZONA_FRIA = False
DEFAULT_CALIDAD_AISLAMIENTO = "Media"
DEFAULT_FUENTE_CALEFACCION = "Electricidad"
DEFAULT_FUENTE_AGUA_CALIENTE = "Electricidad"
DEFAULT_USO_HORARIO_PICO = False


class AnalisisRequest(BaseModel):
    """Request del endpoint POST /analisis-energetico.

    4 campos obligatorios (input del usuario). 7 opcionales con defaults
    sensatos (contexto del hogar que el modelo sabe imputar).
    """

    # --- OBLIGATORIOS ---
    consumo_kwh: float = Field(
        ...,
        ge=0,
        description="Consumo mensual en kWh (de la factura).",
    )
    tipo_inmueble: TipoInmueble = Field(
        ...,
        description="Tipo de vivienda: Casa | Departamento | Comercio | Pyme.",
    )
    cantidad_equipos: int = Field(
        ...,
        ge=0,
        description="Cantidad de electrodomesticos/equipos electricos del hogar.",
    )
    horas_alto_consumo: int = Field(
        ...,
        ge=0,
        le=24,
        description="Horas diarias aproximadas de uso de equipos de alto consumo.",
    )

    # --- OPCIONALES (con default) ---
    metros_cuadrados: float = Field(
        default=DEFAULT_METROS_CUADRADOS,
        ge=0,
        description="Superficie del inmueble en m^2. Default: 1000.",
    )
    antiguedad_vivienda: int = Field(
        default=DEFAULT_ANTIGUEDAD_VIVIENDA,
        ge=0,
        description="Anos de antiguedad de la vivienda. Default: 50.",
    )
    zona_fria: bool = Field(
        default=DEFAULT_ZONA_FRIA,
        description="Vive en zona climatica fria. Default: false.",
    )
    calidad_aislamiento: CalidadAislamiento = Field(
        default=DEFAULT_CALIDAD_AISLAMIENTO,
        description=(
            "Calidad del aislamiento termico: "
            "Muy Alta | Alta | Media | Baja | Muy Baja. Default: Media."
        ),
    )
    fuente_calefaccion: FuenteEnergia = Field(
        default=DEFAULT_FUENTE_CALEFACCION,
        description="Fuente de calefaccion: Electricidad | Solar | Otros. Default: Electricidad.",
    )
    fuente_agua_caliente: FuenteEnergia = Field(
        default=DEFAULT_FUENTE_AGUA_CALIENTE,
        description="Fuente de agua caliente: Electricidad | Solar | Otros. Default: Electricidad.",
    )
    uso_horario_pico: bool = Field(
        default=DEFAULT_USO_HORARIO_PICO,
        description="Uso principal en horario punta (18-23hs). Default: false.",
    )
